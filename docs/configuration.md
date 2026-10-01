# gitea-monitoring — Configuration

The exporter defaults to port 9178 and polls every 300 seconds. BIND_IP defaults to 127.0.0.1. GITEA_URL, GITEA_NETWORK and POLL_INTERVAL_SECONDS are set through .env; config.example.yml lists the Python process settings, including REQUEST_TIMEOUT_SECONDS and secret file paths. The API token needs read-only administrative access to users, organizations, repositories, issues and Actions.

## Dashboard variables

| Dashboard | Variable | Type | Default or query |
|---|---|---|---|
| `gitea-application.json` | `prometheus_ds` | datasource | `prometheus` |
| `gitea-application.json` | `job_gitea_domain` | textbox | `gitea-domain` |
| `gitea-application.json` | `job_gitea_native` | textbox | `gitea-native` |
| `gitea-application.json` | `instance` | query | `label_values(up{job="${job_gitea_domain}"}, instance)` |

## Prometheus jobs

The supplied [scrape example](../examples/prometheus-scrape.yml) defines `gitea-domain`, `gitea-native`. Copy its entries into your own scrape_configs and replace documentation hostnames. Job names can change if the dashboard variables change with them.

## Environment example

Start from [.env.example](../.env.example). Keep the resulting .env and all secret files outside version control.

The dashboard selects an `instance` from `gitea-domain` and uses that value in native panels. The supplied scrape example labels both jobs `instance: gitea`. If you rename that logical instance, use the same value for both jobs. The Service Health panel requires both scrapes to be healthy; a missing job displays down.
