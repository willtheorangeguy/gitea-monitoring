import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "src"))

from gitea_exporter import (  # noqa: E402
    ExporterState,
    collect_metrics,
    parse_timestamp,
    render_metrics,
)


class FakeAPI:
    def get(self, path, params=None):
        if path == "/version":
            return {"version": "1.27.3"}, {}
        if path == "/admin/actions/runners":
            return {
                "total_count": 2,
                "runners": [
                    {"status": "online", "busy": True, "disabled": False},
                    {"status": "offline", "busy": False, "disabled": True},
                ],
            }, {}
        raise AssertionError((path, params))

    def get_paginated(self, path, list_key=None, per_page=50):
        if path == "/repos/search":
            self.assert_equal(list_key, "data")
            return [
                {
                    "private": False,
                    "internal": False,
                    "archived": False,
                    "fork": False,
                    "mirror": False,
                    "template": True,
                    "language": "Python",
                    "stars_count": 3,
                    "forks_count": 2,
                    "release_counter": 4,
                    "size": 999999,
                },
                {
                    "private": True,
                    "internal": False,
                    "archived": True,
                    "fork": True,
                    "mirror": False,
                    "template": False,
                    "language": "",
                    "stars_count": 1,
                    "forks_count": 0,
                    "release_counter": 0,
                },
            ]
        if path == "/admin/users":
            return [{"active": True, "is_admin": True}, {"active": False, "is_admin": False}]
        if path == "/admin/orgs":
            return [{"visibility": "public"}, {"visibility": "private"}]
        if path == "/admin/cron":
            return [{
                "name": "repo_health_check",
                "exec_times": 7,
                "prev": "2026-09-19T12:00:00Z",
                "next": "2026-09-19T13:00:00Z",
            }]
        raise AssertionError((path, list_key, per_page))

    def get_total(self, path, params=None):
        if path == "/repos/issues/search":
            values = {
                ("issues", "open"): 5,
                ("issues", "closed"): 8,
                ("pulls", "open"): 2,
                ("pulls", "closed"): 3,
            }
            return values[(params["type"], params["state"])]
        if path in ("/admin/actions/runs", "/admin/actions/jobs"):
            return 1 if params["status"] == "success" else 0
        raise AssertionError((path, params))

    def assert_equal(self, left, right):
        if left != right:
            raise AssertionError((left, right))


class ExporterTests(unittest.TestCase):
    def test_collects_only_direct_values(self):
        text = render_metrics(collect_metrics(FakeAPI()))
        self.assertIn("gitea_instance_repositories 2", text)
        self.assertIn('gitea_instance_repositories_by_visibility{visibility="private"} 1', text)
        self.assertIn('gitea_instance_repositories_by_language{language="Python"} 1', text)
        self.assertIn("gitea_instance_repositories_without_language 1", text)
        self.assertIn('gitea_instance_issues{state="open"} 5', text)
        self.assertIn('gitea_instance_pull_requests{state="closed"} 3', text)
        self.assertIn('gitea_instance_actions_runs{status="success"} 1', text)
        self.assertIn('gitea_instance_cron_task_executions_total{task="repo_health_check"} 7', text)
        self.assertNotIn("repository_size", text)
        self.assertNotIn("999999", text)

    def test_invalid_or_zero_timestamp_is_omitted(self):
        self.assertIsNone(parse_timestamp(""))
        self.assertIsNone(parse_timestamp("not-a-date"))
        self.assertIsNone(parse_timestamp("0001-01-01T00:00:00Z"))
        self.assertGreater(parse_timestamp("2026-09-19T12:00:00Z"), 0)

    def test_label_values_are_escaped(self):
        text = render_metrics(collect_metrics(FakeAPI()))
        self.assertNotIn("size=", text)
        self.assertTrue(text.endswith("\n"))

    def test_failure_retains_last_successful_domain_snapshot(self):
        state = ExporterState()
        state.record_success("gitea_instance_repositories 2\n", 0.25, 4)
        successful_timestamp = state.last_success
        state.record_failure(1.5, 1, "upstream unavailable")
        text = state.metrics()
        self.assertIn("gitea_instance_repositories 2", text)
        self.assertIn("gitea_exporter_up 0", text)
        self.assertIn("gitea_exporter_collection_failures_total 1", text)
        self.assertEqual(state.last_success, successful_timestamp)
        self.assertEqual(state.api_requests, 5)



if __name__ == "__main__":
    unittest.main()
