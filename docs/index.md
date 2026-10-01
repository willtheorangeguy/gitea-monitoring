# Gitea Monitoring

A read-only Gitea API exporter paired with native Gitea metrics and a Grafana application dashboard.

## Key features

- Read-only Gitea domain metrics from its API.
- Native and domain metric views in one dashboard.
- Repository, issue, user, Actions and cron inventory.
- Bearer protected metrics and collector health endpoint.

## Quick start

Open Grafana and import `dashboards/gitea-application.json` through **Dashboards → New → Import**. Select the configured data source and match the dashboard variables to your labels. See [Getting started](getting-started.md) for prerequisites and setup.

## Where to next

<div class="wt-grid" markdown>

[:material-rocket-launch: **Getting started**<br>Set up the required integrations](getting-started.md){ .wt-card }

[:material-download: **Installation**<br>Install and connect the required services](installation.md){ .wt-card }

[:material-tune: **Configuration**<br>Review scrape examples and dashboard variables](configuration.md){ .wt-card }

[:material-sitemap: **Architecture**<br>Follow metrics from source to dashboard](architecture.md){ .wt-card }

[:material-view-dashboard: **Dashboard usage**<br>Import and use the dashboard](usage.md){ .wt-card }

</div>

## Support

{{ support() }}
