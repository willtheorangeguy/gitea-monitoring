#!/usr/bin/env python3
"""Low-cardinality, read-only Prometheus exporter for Gitea instance data."""

from __future__ import annotations

import collections
import dataclasses
import datetime as dt
import hmac
import json
import logging
import os
import signal
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Iterable


VERSION = "1.0.0"
ACTION_STATUSES = ("pending", "queued", "in_progress", "failure", "success", "skipped")


@dataclasses.dataclass(frozen=True)
class Metric:
    name: str
    help: str
    metric_type: str
    samples: tuple[tuple[dict[str, str], float], ...]


def _escape_help(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n")


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def render_metrics(metrics: Iterable[Metric]) -> str:
    lines: list[str] = []
    for metric in metrics:
        lines.append(f"# HELP {metric.name} {_escape_help(metric.help)}")
        lines.append(f"# TYPE {metric.name} {metric.metric_type}")
        for labels, value in metric.samples:
            label_text = ""
            if labels:
                rendered = ",".join(
                    f'{key}="{_escape_label(str(labels[key]))}"' for key in sorted(labels)
                )
                label_text = "{" + rendered + "}"
            lines.append(f"{metric.name}{label_text} {value:g}")
    return "\n".join(lines) + "\n"


def parse_timestamp(value: Any) -> float | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    timestamp = parsed.timestamp()
    return timestamp if timestamp > 0 else None


class GiteaAPI:
    def __init__(self, base_url: str, token: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/") + "/api/v1"
        self.token = token
        self.timeout = timeout
        self.request_count = 0

    def get(self, path: str, params: dict[str, Any] | None = None) -> tuple[Any, dict[str, str]]:
        query = urllib.parse.urlencode(params or {})
        url = self.base_url + path + ("?" + query if query else "")
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "Authorization": "token " + self.token,
                "User-Agent": f"gitea-domain-exporter/{VERSION}",
            },
        )
        self.request_count += 1
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.load(response), {key.lower(): value for key, value in response.headers.items()}
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"Gitea API returned HTTP {exc.code} for {path}") from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Gitea API request failed for {path}: {type(exc).__name__}") from exc

    def get_total(self, path: str, params: dict[str, Any] | None = None) -> int:
        query = dict(params or {})
        query.update({"limit": 1, "page": 1})
        body, headers = self.get(path, query)
        if "x-total-count" in headers:
            return int(headers["x-total-count"])
        if isinstance(body, dict) and isinstance(body.get("total_count"), int):
            return int(body["total_count"])
        raise RuntimeError(f"Gitea API did not return an authoritative total for {path}")

    def get_paginated(self, path: str, list_key: str | None = None, per_page: int = 50) -> list[dict[str, Any]]:
        page = 1
        result: list[dict[str, Any]] = []
        expected_total: int | None = None
        while True:
            body, headers = self.get(path, {"limit": per_page, "page": page})
            if list_key is not None:
                if not isinstance(body, dict) or not isinstance(body.get(list_key), list):
                    raise RuntimeError(f"Unexpected paginated response for {path}")
                items = body[list_key]
                body_total = body.get("total_count")
                if isinstance(body_total, int):
                    expected_total = body_total
            else:
                if not isinstance(body, list):
                    raise RuntimeError(f"Unexpected paginated response for {path}")
                items = body
            if "x-total-count" in headers:
                expected_total = int(headers["x-total-count"])
            result.extend(item for item in items if isinstance(item, dict))
            if not items or (expected_total is not None and len(result) >= expected_total):
                break
            if expected_total is None and len(items) < per_page:
                break
            page += 1
        return result


def _single(value: float, labels: dict[str, str] | None = None) -> tuple[tuple[dict[str, str], float], ...]:
    return ((labels or {}, float(value)),)


def _counter_samples(values: collections.Counter[Any], label_names: tuple[str, ...]) -> tuple[tuple[dict[str, str], float], ...]:
    samples: list[tuple[dict[str, str], float]] = []
    for key, value in sorted(values.items(), key=lambda pair: str(pair[0])):
        keys = key if isinstance(key, tuple) else (key,)
        labels = {name: str(item).lower() if isinstance(item, bool) else str(item) for name, item in zip(label_names, keys)}
        samples.append((labels, float(value)))
    return tuple(samples)


def collect_metrics(api: GiteaAPI) -> list[Metric]:
    version_body, _ = api.get("/version")
    version = version_body.get("version") if isinstance(version_body, dict) else None
    if not isinstance(version, str) or not version:
        raise RuntimeError("Gitea API did not return a version")

    repositories = api.get_paginated("/repos/search", list_key="data")
    users = api.get_paginated("/admin/users")
    organizations = api.get_paginated("/admin/orgs")
    cron_tasks = api.get_paginated("/admin/cron")
    runners_body, _ = api.get("/admin/actions/runners")
    if not isinstance(runners_body, dict) or not isinstance(runners_body.get("runners"), list):
        raise RuntimeError("Unexpected Gitea Actions runners response")
    runners = [item for item in runners_body["runners"] if isinstance(item, dict)]
    runners_total = runners_body.get("total_count")
    if not isinstance(runners_total, int):
        raise RuntimeError("Gitea Actions runners response did not include total_count")

    visibility = collections.Counter()
    features = collections.Counter()
    languages = collections.Counter()
    no_language = 0
    stars = 0
    forks = 0
    releases = 0
    for repo in repositories:
        if repo.get("internal") is True:
            visibility["internal"] += 1
        elif repo.get("private") is True:
            visibility["private"] += 1
        else:
            visibility["public"] += 1
        for feature in ("archived", "fork", "mirror", "template"):
            if repo.get(feature) is True:
                features[feature] += 1
        language = repo.get("language")
        if isinstance(language, str) and language.strip():
            languages[language.strip()] += 1
        else:
            no_language += 1
        for field, target in (("stars_count", "stars"), ("forks_count", "forks"), ("release_counter", "releases")):
            value = repo.get(field)
            if isinstance(value, int) and value >= 0:
                if target == "stars":
                    stars += value
                elif target == "forks":
                    forks += value
                else:
                    releases += value

    issue_counts = collections.Counter()
    pull_counts = collections.Counter()
    for state in ("open", "closed"):
        issue_counts[state] = api.get_total("/repos/issues/search", {"type": "issues", "state": state})
        pull_counts[state] = api.get_total("/repos/issues/search", {"type": "pulls", "state": state})

    user_counts = collections.Counter()
    for user in users:
        user_counts[("active" if user.get("active") is True else "inactive", user.get("is_admin") is True)] += 1

    organization_visibility = collections.Counter()
    for organization in organizations:
        value = organization.get("visibility")
        if isinstance(value, str) and value:
            organization_visibility[value] += 1

    runner_counts = collections.Counter()
    for runner in runners:
        status = runner.get("status")
        if not isinstance(status, str) or not status:
            status = "unknown"
        runner_counts[(status, runner.get("busy") is True, runner.get("disabled") is True)] += 1

    action_runs = collections.Counter()
    action_jobs = collections.Counter()
    for status in ACTION_STATUSES:
        action_runs[status] = api.get_total("/admin/actions/runs", {"status": status})
        action_jobs[status] = api.get_total("/admin/actions/jobs", {"status": status})

    cron_execution_samples: list[tuple[dict[str, str], float]] = []
    cron_previous_samples: list[tuple[dict[str, str], float]] = []
    cron_next_samples: list[tuple[dict[str, str], float]] = []
    for task in cron_tasks:
        name = task.get("name")
        executions = task.get("exec_times")
        if not isinstance(name, str) or not name or not isinstance(executions, int):
            continue
        labels = {"task": name}
        cron_execution_samples.append((labels, float(executions)))
        previous = parse_timestamp(task.get("prev"))
        upcoming = parse_timestamp(task.get("next"))
        if previous is not None:
            cron_previous_samples.append((labels, previous))
        if upcoming is not None:
            cron_next_samples.append((labels, upcoming))

    return [
        Metric("gitea_instance_info", "Installed Gitea instance version.", "gauge", _single(1, {"version": version})),
        Metric("gitea_instance_repositories", "Repositories visible to the read-only administrative API token.", "gauge", _single(len(repositories))),
        Metric("gitea_instance_repositories_by_visibility", "Repositories by Gitea visibility.", "gauge", _counter_samples(visibility, ("visibility",))),
        Metric("gitea_instance_repositories_by_feature", "Repositories with a directly reported Gitea feature flag.", "gauge", _counter_samples(features, ("feature",))),
        Metric("gitea_instance_repositories_by_language", "Repositories by directly reported primary language; repositories without a language are excluded.", "gauge", _counter_samples(languages, ("language",))),
        Metric("gitea_instance_repositories_without_language", "Repositories for which Gitea reports no primary language.", "gauge", _single(no_language)),
        Metric("gitea_instance_repository_stars", "Sum of repository star counts reported by Gitea.", "gauge", _single(stars)),
        Metric("gitea_instance_repository_forks", "Sum of repository fork counts reported by Gitea.", "gauge", _single(forks)),
        Metric("gitea_instance_releases", "Sum of repository release counts reported by Gitea.", "gauge", _single(releases)),
        Metric("gitea_instance_issues", "Gitea issues by state, excluding pull requests.", "gauge", _counter_samples(issue_counts, ("state",))),
        Metric("gitea_instance_pull_requests", "Gitea pull requests by state.", "gauge", _counter_samples(pull_counts, ("state",))),
        Metric("gitea_instance_users", "Gitea users by active and administrator state.", "gauge", _counter_samples(user_counts, ("status", "admin"))),
        Metric("gitea_instance_organizations", "Gitea organizations returned by the administrative API.", "gauge", _single(len(organizations))),
        Metric("gitea_instance_organizations_by_visibility", "Gitea organizations by directly reported visibility.", "gauge", _counter_samples(organization_visibility, ("visibility",))),
        Metric("gitea_instance_actions_runners", "Gitea Actions runners returned by the administrative API.", "gauge", _single(runners_total)),
        Metric("gitea_instance_actions_runners_by_state", "Gitea Actions runners by reported status, busy state, and disabled state.", "gauge", _counter_samples(runner_counts, ("status", "busy", "disabled"))),
        Metric("gitea_instance_actions_runs", "Gitea Actions workflow runs by API-supported status.", "gauge", _counter_samples(action_runs, ("status",))),
        Metric("gitea_instance_actions_jobs", "Gitea Actions jobs by API-supported status.", "gauge", _counter_samples(action_jobs, ("status",))),
        Metric("gitea_instance_cron_tasks", "Gitea cron tasks returned by the administrative API.", "gauge", _single(len(cron_tasks))),
        Metric("gitea_instance_cron_task_executions_total", "Executions reported by Gitea for each configured cron task.", "counter", tuple(cron_execution_samples)),
        Metric("gitea_instance_cron_task_previous_run_timestamp_seconds", "Previous execution time reported by Gitea for each cron task.", "gauge", tuple(cron_previous_samples)),
        Metric("gitea_instance_cron_task_next_run_timestamp_seconds", "Next execution time reported by Gitea for each cron task.", "gauge", tuple(cron_next_samples)),
    ]


class ExporterState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.domain_text = ""
        self.up = 0.0
        self.failures = 0
        self.duration = 0.0
        self.last_success = 0.0
        self.api_requests = 0
        self.last_error = "not collected yet"

    def record_success(self, domain_text: str, duration: float, api_requests: int) -> None:
        with self.lock:
            self.domain_text = domain_text
            self.up = 1.0
            self.duration = duration
            self.last_success = time.time()
            self.api_requests += api_requests
            self.last_error = ""

    def record_failure(self, duration: float, api_requests: int, error: str) -> None:
        with self.lock:
            self.up = 0.0
            self.failures += 1
            self.duration = duration
            self.api_requests += api_requests
            self.last_error = error

    def metrics(self) -> str:
        with self.lock:
            self_metrics = [
                Metric("gitea_exporter_build_info", "Gitea domain exporter build information.", "gauge", _single(1, {"version": VERSION})),
                Metric("gitea_exporter_up", "Whether the most recent Gitea API collection succeeded.", "gauge", _single(self.up)),
                Metric("gitea_exporter_collection_failures_total", "Gitea API collection failures since exporter start.", "counter", _single(self.failures)),
                Metric("gitea_exporter_collection_duration_seconds", "Duration of the most recent Gitea API collection.", "gauge", _single(self.duration)),
                Metric("gitea_exporter_last_success_timestamp_seconds", "Unix timestamp of the most recent successful Gitea API collection.", "gauge", _single(self.last_success)),
                Metric("gitea_exporter_api_requests_total", "Gitea API requests attempted since exporter start.", "counter", _single(self.api_requests)),
            ]
            return render_metrics(self_metrics) + self.domain_text

    def health(self) -> tuple[bool, str]:
        with self.lock:
            return self.up == 1.0, self.last_error


def collect_once(state: ExporterState, base_url: str, token: str, timeout: float) -> None:
    api = GiteaAPI(base_url, token, timeout)
    started = time.monotonic()
    try:
        domain_text = render_metrics(collect_metrics(api))
    except Exception as exc:  # collector must stay alive and expose failure state
        duration = time.monotonic() - started
        state.record_failure(duration, api.request_count, str(exc))
        logging.error("Gitea collection failed: %s", exc)
        return
    state.record_success(domain_text, time.monotonic() - started, api.request_count)


def read_secret(path: str) -> str:
    with open(path, encoding="utf-8") as secret_file:
        value = secret_file.read().strip()
    if not value:
        raise RuntimeError(f"Secret file is empty: {path}")
    return value


def make_handler(state: ExporterState, bearer_token: str):
    class Handler(BaseHTTPRequestHandler):
        server_version = "gitea-domain-exporter/" + VERSION

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            path = urllib.parse.urlsplit(self.path).path
            if path == "/healthz":
                healthy, error = state.health()
                payload = b"ok\n" if healthy else ("unhealthy: " + error + "\n").encode()
                self.send_response(200 if healthy else 503)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            if path != "/metrics":
                self.send_error(404)
                return
            supplied = self.headers.get("Authorization", "")
            expected = "Bearer " + bearer_token
            if not hmac.compare_digest(supplied, expected):
                payload = b"unauthorized\n"
                self.send_response(401)
                self.send_header("WWW-Authenticate", "Bearer")
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return
            payload = state.metrics().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, fmt: str, *args: Any) -> None:
            logging.info("HTTP %s - %s", self.address_string(), fmt % args)

    return Handler


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(message)s")
    base_url = os.getenv("GITEA_URL", "http://server:3000")
    api_token = read_secret(os.getenv("GITEA_TOKEN_FILE", "/run/secrets/gitea_api_token"))
    bearer_token = read_secret(os.getenv("EXPORTER_BEARER_TOKEN_FILE", "/run/secrets/exporter_bearer_token"))
    poll_interval = max(30.0, float(os.getenv("POLL_INTERVAL_SECONDS", "300")))
    request_timeout = max(1.0, float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")))
    listen_address = os.getenv("LISTEN_ADDRESS", "0.0.0.0")
    listen_port = int(os.getenv("LISTEN_PORT", "9178"))

    state = ExporterState()
    collect_once(state, base_url, api_token, request_timeout)
    stop_event = threading.Event()

    def polling_loop() -> None:
        while not stop_event.wait(poll_interval):
            collect_once(state, base_url, api_token, request_timeout)

    polling_thread = threading.Thread(target=polling_loop, name="gitea-poller", daemon=True)
    polling_thread.start()

    server = ThreadingHTTPServer((listen_address, listen_port), make_handler(state, bearer_token))

    def stop_server(_signum: int, _frame: Any) -> None:
        stop_event.set()
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop_server)
    signal.signal(signal.SIGINT, stop_server)
    logging.info("Listening on %s:%d; polling %s every %.0f seconds", listen_address, listen_port, base_url, poll_interval)
    try:
        server.serve_forever()
    finally:
        stop_event.set()
        server.server_close()


if __name__ == "__main__":
    main()
