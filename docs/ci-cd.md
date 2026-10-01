# CI/CD

GitHub Actions checks source changes and builds this documentation site.

## Workflows

| Workflow | Trigger | Purpose |
| --- | --- | --- |
| `testing.yml` | Push and pull request | testing.yml` runs the Python unit tests selected by its unittest discovery command. |
| `gitleaks.yml` | Push, pull request and manual dispatch | Scans repository history for exposed secrets. |
| `docs.yml` | Push to `main` or manual dispatch | Builds and deploys the MkDocs site to GitHub Pages. |
| `docs-lint.yml` | Pull request | Runs Markdown style, strict site build and external link checks. |

## Documentation deployment

The repository calls the reusable build and deployment workflow in [willtheorangeguy/mkdocs](https://github.com/willtheorangeguy/mkdocs). A deployment runs when documentation, site configuration, the deployment caller or included root files change.

## Secret scanning

`gitleaks.yml` scans pushes and pull requests. A finding fails the workflow and requires removing or rotating the exposed credential.

## Dashboard validation

`testing.yml` runs the Python unit tests selected by its unittest discovery command.
