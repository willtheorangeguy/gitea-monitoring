# gitea-monitoring — Quickstart

## Prerequisites

Docker Compose, Gitea API access with a scoped read-only administrative token, Gitea native metrics, Prometheus and Grafana.

## Set up

Copy .env.example to .env. Set GITEA_URL and GITEA_NETWORK; create secrets/gitea-api-token and secrets/metrics-token. Start docker compose up -d --build. Add the gitea-domain and gitea-native jobs in examples/prometheus-scrape.yml, then import the dashboard.

The example Prometheus scrape job names are `gitea-domain`, `gitea-native`.

## Confirm data

In Prometheus, check `up{job="gitea-domain"}`, `up{job="gitea-native"}` and inspect a panel query in Grafana.
For missing data, see [troubleshooting](./troubleshooting.md).
