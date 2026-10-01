# gitea-monitoring — Architecture

Gitea API -> read-only Python exporter -> authenticated /metrics -> Prometheus. Gitea native /metrics is scraped separately. Both feed the Grafana dashboard.

## Components

- [compose.yml](../compose.yml): container deployment
- [dashboards/](../dashboards): Grafana dashboard definitions
- [examples/](../examples): deployment and scrape examples
- [src/](../src): collector or proxy implementation

## Data interpretation

API collection runs on a timer; the exporter exposes last success and failure metrics. Native and domain scrapes should share the same instance label for dashboard panels that compare them.
