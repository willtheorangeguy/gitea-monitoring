# gitea-monitoring — Dashboard Usage

Import the JSON files using **Grafana → Dashboards → New → Import**. Set the data source and variables listed in [configuration](./configuration.md).

## Gitea Application Overview

Source: [gitea-application.json](../dashboards/gitea-application.json). Refresh: `30s`.

<!-- Screenshot: after adding gitea-application.png to .github/icons/gitea-monitoring/, replace this comment with ![Gitea Application Overview](https://raw.githubusercontent.com/willtheorangeguy/.github/main/icons/gitea-monitoring/gitea-application.png). -->

### Panels

| Panel | Type | What it shows |
|---|---|---|
| Service Health | stat | Both the native Gitea scrape and read-only domain exporter must be healthy. |
| Repositories | stat | Authoritative repository total returned by Gitea's administrative repository search API. |
| Open Issues | stat | Open issues reported by Gitea, excluding pull requests. |
| Open Pull Requests | stat | Open pull requests reported by Gitea. |
| Releases | stat | Sum of repository release counters returned by Gitea. |
| Users | stat | Users returned by Gitea's administrative API. |
| Organizations | stat | Organizations returned by Gitea's administrative API. |
| Server Cron Tasks | stat | Configured cron tasks returned by Gitea's administrative API. |
| Mirrors | stat | Repositories for which Gitea directly reports mirror=true. |
| Public Repositories | stat | Repositories for which Gitea directly reports public visibility. |
| Private Repositories | stat | Repositories for which Gitea directly reports private visibility. |
| Primary Languages | stat | Number of distinct non-empty primary-language values returned by Gitea. |
| No Reported Language | stat | Repositories for which Gitea returns no primary language. |
| Stars | stat | Sum of repository star counters returned by Gitea. |
| Forks | stat | Sum of repository fork counters returned by Gitea. |
| Exporter Data Age | stat | Seconds since the last successful read-only Gitea API collection. |
| Repository Visibility | piechart | Repository counts grouped only by Gitea's directly reported visibility. |
| Repository Features | bargauge | Counts for directly reported repository flags. Absent flags are left absent rather than synthesized as zero. |
| Repositories by Primary Language | bargauge | Gitea's directly reported primary language; empty language values are excluded and counted separately above. |
| Issues by State | bargauge | Issue totals returned by Gitea's global issue search API; pull requests are excluded. |
| Pull Requests by State | bargauge | Pull-request totals returned by Gitea. The API exposes open/closed totals but no authoritative global merged-state total. |
| Users by State | bargauge | Users grouped by the active and administrator flags returned by Gitea. |
| Actions Workflow Runs | bargauge | Workflow-run totals for each status supported by Gitea's administrative Actions API. |
| Actions Jobs | bargauge | Job totals for each status supported by Gitea's administrative Actions API. |
| Cron Task Executions | bargauge | Cumulative execution counts directly reported for each configured Gitea cron task. |
| Time Since Previous Cron Run | bargauge | Elapsed seconds since each previous cron execution. Tasks without a reported previous run are absent. |
| Time Until Next Cron Run | bargauge | Seconds until the next execution timestamp reported by Gitea. Tasks without a reported next run are absent. |
| Native Gitea Object Inventory | bargauge | Application object counts exposed directly by Gitea's native Prometheus endpoint. |
| Repository History | timeseries | History of total, public, private, and mirror repository counts after monitoring was enabled. |
| Issue and Pull Request History | timeseries | Direct issue and pull-request state totals over time. |
| Actions State History | timeseries | Direct workflow-run and job totals by Gitea-supported status. |

<!-- Screenshot: add a focused panel or section image here after uploading it to .github/icons/gitea-monitoring/. -->

### Reading the results

API collection runs on a timer; the exporter exposes last success and failure metrics. Native and domain scrapes should share the same instance label for dashboard panels that compare them.

### Query reference

These expressions are copied from the dashboard JSON. Grafana substitutes the dashboard variables at runtime.

#### Service Health

```promql
(min(up{job="${job_gitea_domain}",instance="$instance"}) or vector(0)) * (min(up{job="${job_gitea_native}",instance="$instance"}) or vector(0))
```

#### Repositories

```promql
gitea_instance_repositories{job="${job_gitea_domain}",instance="$instance"}
```

#### Open Issues

```promql
gitea_instance_issues{job="${job_gitea_domain}",instance="$instance",state="open"}
```

#### Open Pull Requests

```promql
gitea_instance_pull_requests{job="${job_gitea_domain}",instance="$instance",state="open"}
```

#### Releases

```promql
gitea_instance_releases{job="${job_gitea_domain}",instance="$instance"}
```

#### Users

```promql
sum(gitea_instance_users{job="${job_gitea_domain}",instance="$instance"})
```

#### Organizations

```promql
gitea_instance_organizations{job="${job_gitea_domain}",instance="$instance"}
```

#### Server Cron Tasks

```promql
gitea_instance_cron_tasks{job="${job_gitea_domain}",instance="$instance"}
```

#### Mirrors

```promql
gitea_instance_repositories_by_feature{job="${job_gitea_domain}",instance="$instance",feature="mirror"}
```

#### Public Repositories

```promql
gitea_instance_repositories_by_visibility{job="${job_gitea_domain}",instance="$instance",visibility="public"}
```

#### Private Repositories

```promql
gitea_instance_repositories_by_visibility{job="${job_gitea_domain}",instance="$instance",visibility="private"}
```

#### Primary Languages

```promql
count(gitea_instance_repositories_by_language{job="${job_gitea_domain}",instance="$instance"})
```

#### No Reported Language

```promql
gitea_instance_repositories_without_language{job="${job_gitea_domain}",instance="$instance"}
```

#### Stars

```promql
gitea_instance_repository_stars{job="${job_gitea_domain}",instance="$instance"}
```

#### Forks

```promql
gitea_instance_repository_forks{job="${job_gitea_domain}",instance="$instance"}
```

#### Exporter Data Age

```promql
time() - gitea_exporter_last_success_timestamp_seconds{job="${job_gitea_domain}",instance="$instance"}
```

#### Repository Visibility

```promql
gitea_instance_repositories_by_visibility{job="${job_gitea_domain}",instance="$instance"}
```

#### Repository Features

```promql
gitea_instance_repositories_by_feature{job="${job_gitea_domain}",instance="$instance"}
```

#### Repositories by Primary Language

```promql
sort_desc(gitea_instance_repositories_by_language{job="${job_gitea_domain}",instance="$instance"})
```

#### Issues by State

```promql
gitea_instance_issues{job="${job_gitea_domain}",instance="$instance"}
```

#### Pull Requests by State

```promql
gitea_instance_pull_requests{job="${job_gitea_domain}",instance="$instance"}
```

#### Users by State

```promql
gitea_instance_users{job="${job_gitea_domain}",instance="$instance"}
```

#### Actions Workflow Runs

```promql
gitea_instance_actions_runs{job="${job_gitea_domain}",instance="$instance"}
```

#### Actions Jobs

```promql
gitea_instance_actions_jobs{job="${job_gitea_domain}",instance="$instance"}
```

#### Cron Task Executions

```promql
sort_desc(gitea_instance_cron_task_executions_total{job="${job_gitea_domain}",instance="$instance"})
```

#### Time Since Previous Cron Run

```promql
sort_desc(time() - gitea_instance_cron_task_previous_run_timestamp_seconds{job="${job_gitea_domain}",instance="$instance"})
```

#### Time Until Next Cron Run

```promql
sort_desc(gitea_instance_cron_task_next_run_timestamp_seconds{job="${job_gitea_domain}",instance="$instance"} - time())
```

#### Native Gitea Object Inventory

```promql
{job="${job_gitea_native}",instance="$instance",__name__=~"gitea_(attachments|comments|hooktasks|issues|labels|milestones|mirrors|organizations|projects|releases|repositories|stars|users|watches|webhooks)"}
```

#### Repository History

```promql
gitea_instance_repositories{job="${job_gitea_domain}",instance="$instance"}
gitea_instance_repositories_by_visibility{job="${job_gitea_domain}",instance="$instance",visibility="public"}
gitea_instance_repositories_by_visibility{job="${job_gitea_domain}",instance="$instance",visibility="private"}
gitea_instance_repositories_by_feature{job="${job_gitea_domain}",instance="$instance",feature="mirror"}
```

#### Issue and Pull Request History

```promql
gitea_instance_issues{job="${job_gitea_domain}",instance="$instance",state="open"}
gitea_instance_issues{job="${job_gitea_domain}",instance="$instance",state="closed"}
gitea_instance_pull_requests{job="${job_gitea_domain}",instance="$instance",state="open"}
gitea_instance_pull_requests{job="${job_gitea_domain}",instance="$instance",state="closed"}
```

#### Actions State History

```promql
gitea_instance_actions_runs{job="${job_gitea_domain}",instance="$instance"}
gitea_instance_actions_jobs{job="${job_gitea_domain}",instance="$instance"}
```
