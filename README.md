# Gitea domain exporter and application dashboard

Portable monitoring bundle with example configuration. Replace example addresses and token paths for your installation; no live credentials are included.

## Requirements

Gitea native metrics plus the included read-only domain exporter. The exporter requires a scoped Gitea API token.

## Dashboards

- `dashboards/gitea-application.json`

Import the JSON in Grafana using **Dashboards > New > Import**. Select your data source from the dashboard variable(s) at the top. Update the Prometheus job variables to match your `scrape_configs` job names; use the Instance selector when present. The dashboard's JSON is also suitable for file provisioning after you have selected or provisioned data source UIDs.

Expected default job labels:

- `gitea-application.json`: gitea-domain, gitea-native

## Monitoring code

See the code and example configuration in this folder, if present. Keep API keys and metrics bearer tokens in local secret files or another secret manager; never commit them. Scrape examples use documentation addresses and must be edited for your network.

## Before publishing

Test against the application and Grafana versions you intend to support. Add a license you choose and check attribution for upstream components. No release or Grafana catalog upload has been performed.

## Run the exporter

Copy `.env.example` to `.env`, set the Gitea URL and existing Docker network, create `secrets/gitea-api-token` and `secrets/metrics-token`, then run `docker compose up -d --build`. Set `BIND_IP` to an address reachable by Prometheus if it runs on another host. Protect both secret files. The Gitea API token needs read-only admin, repository, issue, user, and organization scopes. The exporter publishes `/metrics` with the bearer token and `/healthz` without it. Run `python -m unittest discover -s tests -v` before release.

Scrape with the job names `gitea-domain` (this exporter) and `gitea-native` (Gitea's native endpoint), or change the dashboard job variables. Add `authorization: {type: Bearer, credentials_file: /path/to/metrics-token}` to the domain scrape job.

A sample `scrape_configs` fragment is in `examples/prometheus-scrape.yml`; replace the example hosts and token paths.
