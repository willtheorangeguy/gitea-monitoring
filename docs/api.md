# API

Gitea API -> read-only Python exporter -> authenticated /metrics -> Prometheus. Gitea native /metrics is scraped separately. Both feed the Grafana dashboard.

## Interfaces

- `/metrics` requires the bearer token configured in the deployment. `/healthz` reports collector health.

## Prometheus scrape reference

See [examples/prometheus-scrape.yml](https://github.com/willtheorangeguy/gitea-monitoring/blob/HEAD/examples/prometheus-scrape.yml) for the target, job name and authorization settings.

## Gitea API reads

The exporter calls `/api/v1/version`, `/repos/search`, `/admin/users`, `/admin/orgs`, `/admin/cron` and `/admin/actions/runners`. It also queries `/repos/issues/search` separately for issues and pull requests, and `/admin/actions/runs` and `/admin/actions/jobs` for supported statuses. Collection requires the corresponding read-only administrative permissions.

## Exported families

The `gitea_instance_*` families cover repository visibility, features, language, issue and pull request states, users, organizations, Actions and cron tasks. `gitea_exporter_up`, `gitea_exporter_collection_failures_total`, `gitea_exporter_collection_duration_seconds` and `gitea_exporter_last_success_timestamp_seconds` describe the exporter itself. See [the source](https://github.com/willtheorangeguy/gitea-monitoring/blob/HEAD/src/gitea_exporter.py) for each metric's exact HELP text and labels.
