# Architecture

This project connects its data source to its Grafana dashboard through the components shown below.

## Overview

This diagram shows the data path for this project.

```mermaid
graph LR
  A[Gitea API] -->|polled by| B[Domain exporter]
  C[Gitea native metrics] -->|scraped by| D[Prometheus]
  B -->|exposes metrics to| D
  D -->|queried by| E[Grafana dashboard]
```

## Components

### Data source

Gitea API -> Python exporter -> authenticated /metrics -> Prometheus -> Grafana; native Gitea metrics use a separate scrape.

### Dashboard

`dashboards/gitea-application.json` contains the Grafana dashboard definition.

## Data flow

Gitea API -> Python exporter -> authenticated /metrics -> Prometheus -> Grafana; native Gitea metrics use a separate scrape. Grafana evaluates dashboard queries against the selected data source and label values.

## Directory layout

```text
.
├── dashboards/  Grafana dashboard JSON files
├── src/  Python services and collectors
├── tests/  Automated unit tests
├── examples/  Scrape and deployment examples
├── docs/        Documentation source
└── README.md    Project overview and quick links
```
