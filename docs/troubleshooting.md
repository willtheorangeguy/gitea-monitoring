# Troubleshooting

| Symptom | Check |
| --- | --- |
| Exporter /healthz returns 503 | inspect logs and API token scopes, URL, and API responses. |
| /metrics returns 401 | match the Prometheus bearer credential to secrets/metrics-token. |
| Native panels blank | enable Gitea metrics and check the gitea-native job and instance label. |

## First checks

Check the selected Grafana data source and dashboard variables in [configuration](configuration.md). For Prometheus, inspect the target state and the exact job and instance labels before changing panel queries.
