# CI/CD and Security Pipeline Documentation

## Scope

This document covers only the CI/CD, security testing, containerization, and reporting workflow.
It does not describe or change the application’s business logic.

## Implemented Pipeline

The repository now has a Jenkins pipeline that follows the required flow:

1. Checkout the code from Git.
2. Run static checks.
3. Build the application Docker image.
4. Run dynamic checks against the running container stack.
5. Collect and archive results.
6. Generate a final report.

The implementation is defined in [Jenkinsfile](../Jenkinsfile).

## Static Checks

The pipeline now covers more than three static-check categories.

### Secret and Credential Detection

Files:

- [scripts/check_secrets.py](../scripts/check_secrets.py)

Why this is included:

- It detects obvious secrets in staged changes without introducing extra tooling overhead.
- It is already part of the repository and fits the current Python-only workflow.

### Linting and Formatting

Tools used in CI:

- Black
- isort
- Flake8

Why this is included:

- Black gives deterministic formatting checks.
- isort keeps imports stable.
- Flake8 catches common style and correctness issues.

### Static Application Security Testing

Tools used in CI:

- Bandit
- Semgrep

Why this is included:

- Bandit is Python-focused and catches insecure code patterns.
- Semgrep adds rule-based security scanning and complements Bandit.

### Dependency Vulnerability Scanning

Tools used in CI:

- pip-audit

Why this is included:

- The application uses [requirements.txt](../requirements.txt), so dependency scanning maps directly to the project structure.
- It helps identify vulnerable packages before a build is promoted.

### Dockerfile and Container Configuration Checks

Tools used in CI:

- Hadolint

Why this is included:

- The repository now includes a dedicated application [Dockerfile](../docker/Dockerfile).
- Hadolint validates container best practices and catches common Dockerfile mistakes.

### Code Quality and Type Checks

Tools used in CI:

- mypy
- pytest

Why this is included:

- Type checking protects the service, repository, and DTO layers from regressions.
- Pytest remains the main execution-time validation step for unit or integration coverage.

## Dynamic Checks

The pipeline now includes multiple runtime security checks.

### Container Image Vulnerability Scanning

Tool used in CI:

- Trivy

Why this is included:

- It scans the built Docker image for known CVEs.
- It is run after the build stage, which matches the normal CI/CD order.

### API Security Scanning

Tool used in CI:

- OWASP ZAP API scan

Why this is included:

- It scans the live FastAPI/OpenAPI surface instead of only the source code.
- It is a practical DAST baseline for this repository.

### Port and Service Discovery

Tool used in CI:

- Nmap

Why this is included:

- It confirms which ports are exposed on the running stack.
- It provides a quick runtime sanity check for the containerized app.

### SQL Injection Testing Targets

File:

- [endpoints.txt](../endpoints.txt)

Why this is included:

- If sqlmap is used, the scan scope must be explicit and reproducible.
- The target file keeps SQLi testing separate from the application code.

The current target file contains the login endpoint because it is available without needing a prior authenticated session.

## Docker and Reproducibility

The repository now contains the container assets needed for reproducible CI execution:

- [docker/Dockerfile](../docker/Dockerfile) for the application image.
- [docker/docker-compose.yml](../docker/docker-compose.yml) for the app and database stack.
- [.dockerignore](../.dockerignore) to keep the build context clean.
- [endpoints.txt](../endpoints.txt) for sqlmap target declaration.
- [Jenkinsfile](../Jenkinsfile) for the repeatable pipeline definition.

The application container runs the FastAPI app on port 8000, and the compose file starts Postgres plus the app service so the security tools can scan a live service.

## Stored Results

The pipeline archives its outputs under `reports/`, including:

- Bandit JSON output.
- pip-audit JSON output.
- Semgrep JSON output.
- Trivy image scan output.
- ZAP HTML and JSON reports.
- Nmap output.
- sqlmap output.
- A final summary file.

## Justification Summary

The selected tools were chosen to cover the main risk areas of this project with a reasonable CI footprint:

- Secret detection prevents accidental leakage of credentials.
- Linting and type checks improve correctness.
- Bandit and Semgrep cover source-level security issues.
- pip-audit covers dependency risk.
- Hadolint covers container configuration.
- Trivy, ZAP, Nmap, and sqlmap validate the running artifact instead of only the source tree.

## What This Documentation Does Not Change

This document does not add features to the API, alter the database schema, or replace the application’s existing runtime behavior.