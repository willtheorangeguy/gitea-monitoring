# Development guide

The implementation and dashboard definitions are in the repository root. Gitea API -> read-only Python exporter -> authenticated /metrics -> Prometheus. Gitea native /metrics is scraped separately. Both feed the Grafana dashboard.

## Local checks

The repository CI workflow runs `python -m unittest discover -s tests -v`. Run it from the repository root after changing the relevant source or dashboard JSON.

When editing dashboards, export the final JSON from Grafana and keep data source variables, job names and panel descriptions in sync with [configuration](configuration.md).

The exporter is a Python standard library service in [src/gitea_exporter.py](https://github.com/willtheorangeguy/gitea-monitoring/blob/HEAD/src/gitea_exporter.py). It polls the Gitea API, retains the last successful domain sample set, and exposes collector status separately. The Docker image is defined in [Dockerfile](https://github.com/willtheorangeguy/gitea-monitoring/tree/HEAD/Dockerfile); [compose.yml](https://github.com/willtheorangeguy/gitea-monitoring/blob/HEAD/compose.yml) mounts the API and metrics tokens as read-only files. Extend the API collection and its mock responses together in [tests/](https://github.com/willtheorangeguy/gitea-monitoring/tree/HEAD/tests).
