<h1 align="center">gitea-monitoring</h1>
<h4 align="center">A read-only Gitea API exporter paired with native Gitea metrics and a Grafana application dashboard.</h4>

<div align="center">
  <img alt="GitHub Issues" src="https://img.shields.io/github/issues/willtheorangeguy/gitea-monitoring">
  <img alt="GitHub Pull Requests" src="https://img.shields.io/github/issues-pr/willtheorangeguy/gitea-monitoring">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue">
  <img alt="gitleaks workflow" src="https://github.com/willtheorangeguy/gitea-monitoring/actions/workflows/gitleaks.yml/badge.svg">
  <img alt="testing workflow" src="https://github.com/willtheorangeguy/gitea-monitoring/actions/workflows/testing.yml/badge.svg">
</div>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#support">Support</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

<!-- Screenshot: after adding gitea-monitoring/overview.png to .github/icons/, replace this comment with ![Dashboard overview](https://raw.githubusercontent.com/willtheorangeguy/.github/main/icons/gitea-monitoring/overview.png). -->

A read-only Gitea API exporter paired with native Gitea metrics and a Grafana application dashboard.

## Key Features

- Read-only Gitea domain metrics from its API.
- Native and domain metric views in one dashboard.
- Repository, issue, user, Actions and cron inventory.
- Bearer protected metrics and collector health endpoint.

## Installation

Docker Compose, Gitea API access with a scoped read-only administrative token, Gitea native metrics, Prometheus and Grafana. Copy .env.example to .env. Set GITEA_URL and GITEA_NETWORK; create secrets/gitea-api-token and secrets/metrics-token. Start docker compose up -d --build. Add the gitea-domain and gitea-native jobs in examples/prometheus-scrape.yml, then import the dashboard. See [installation](docs/installation.md) for more detail.

## Usage

Import [gitea-application.json](dashboards/gitea-application.json) in Grafana using **Dashboards → New → Import**. Choose the data source and match the dashboard variables to your monitoring labels. See [dashboard usage](docs/usage.md).

## Documentation

Full documentation lives in [docs/](docs/index.md): [Quickstart](docs/getting-started.md) · [Configuration](docs/configuration.md) · [Architecture](docs/architecture.md) · [Dashboard usage](docs/usage.md) · [Troubleshooting](docs/troubleshooting.md).

## Support

Open a [GitHub Discussion](https://github.com/willtheorangeguy/gitea-monitoring/discussions/new) or file an [issue](https://github.com/willtheorangeguy/gitea-monitoring/issues/new/choose).

## Contributing

Contributions welcome. See the org-wide [Contributing Guide](https://github.com/willtheorangeguy/.github/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/willtheorangeguy/.github/blob/main/CODE_OF_CONDUCT.md).

## License

MIT — see [LICENSE.md](LICENSE.md).
