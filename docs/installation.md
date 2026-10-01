# gitea-monitoring — Installation

## Requirements

Docker Compose, Gitea API access with a scoped read-only administrative token, Gitea native metrics, Prometheus and Grafana.

## Procedure

Copy .env.example to .env. Set GITEA_URL and GITEA_NETWORK; create secrets/gitea-api-token and secrets/metrics-token. Start docker compose up -d --build. Add the gitea-domain and gitea-native jobs in examples/prometheus-scrape.yml, then import the dashboard.

The files under [examples](../examples) are reference configuration. Replace example addresses, token paths and bind addresses for your deployment.

Next, review [configuration](./configuration.md) and [dashboard usage](./usage.md).

## Compose lifecycle

From the repository root run `docker compose up -d --build` when Compose builds a local image, or `docker compose up -d` for prebuilt images. Inspect container output with `docker compose logs`. Keep credential files out of Git.
