# Configuration

## Precedence

This repository combines dashboard defaults with settings for external services. It defines no shared command-line, environment variable and configuration-file override order; each external service resolves its own settings.

## Integration settings

The exporter defaults to port 9178 and polls every 300 seconds. BIND_IP defaults to 127.0.0.1. GITEA_URL, GITEA_NETWORK and POLL_INTERVAL_SECONDS are set through .env; config.example.yml lists the Python process settings, including REQUEST_TIMEOUT_SECONDS and secret file paths. The API token needs read-only administrative access to users, organizations, repositories, issues and Actions.

## Dashboard variables

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `gitea-application.json / prometheus_ds` | datasource | `prometheus` | Grafana data source selected by the dashboard. |
| `gitea-application.json / job_gitea_domain` | textbox | `gitea-domain` | Dashboard variable whose value selects a scrape job, instance or endpoint. |
| `gitea-application.json / job_gitea_native` | textbox | `gitea-native` | Dashboard variable whose value selects a scrape job, instance or endpoint. |
| `gitea-application.json / instance` | query | `label_values(up{job="${job_gitea_domain}"}, instance)` | Queries the data source for available values. |

## Prometheus jobs

The supplied [scrape example](https://github.com/willtheorangeguy/gitea-monitoring/blob/HEAD/examples/prometheus-scrape.yml) defines `gitea-domain`, `gitea-native`. Copy its entries into your own scrape_configs and replace documentation hostnames. Job names can change if the dashboard variables change with them.

## Environment example

Start from [.env.example](https://github.com/willtheorangeguy/gitea-monitoring/blob/HEAD/.env.example). Keep the resulting .env and all secret files outside version control.

The dashboard selects an `instance` from `gitea-domain` and uses that value in native panels. The supplied scrape example labels both jobs `instance: gitea`. If you rename that logical instance, use the same value for both jobs. The Service Health panel requires both scrapes to be healthy; a missing job displays down.

## Examples

The complete scrape job examples are in [`examples/prometheus-scrape.yml`](https://github.com/willtheorangeguy/gitea-monitoring/blob/HEAD/examples/prometheus-scrape.yml). Copy the relevant job into your Prometheus configuration and replace the example targets.
