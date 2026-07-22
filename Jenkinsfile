pipeline {
    agent any

    options {
        timestamps()
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }

    environment {
        VENV = "${WORKSPACE}/.venv"
        REPORT_DIR = "${WORKSPACE}/reports"

        COMPOSE_PROJECT_NAME = "you-want-ticket-ci"
        APP_IMAGE = "you-want-ticket:ci"
        DB_IMAGE = "you-want-ticket-postgres:ci"

        // Different host ports let local Docker and Jenkins run together.
        APP_PORT = "18000"
        DB_PORT = "15434"

        // Jenkins is a container, so 127.0.0.1 would point to Jenkins itself.
        APP_URL = "http://host.docker.internal:18000"

        // Scanner containers join the application's Compose network.
        INTERNAL_APP_URL = "http://app:8000"

        // Used by --volumes-from so scanners can access the Jenkins workspace.
        JENKINS_CONTAINER = "you-want-ticket-jenkins"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Cleaning Jenkins workspace...'
                deleteDir()

                echo 'Checking out repository...'
                checkout scm
            }
        }

        stage('Prepare Environment') {
            steps {
                sh '''
                    set -eu

                    python3 --version
                    git --version
                    docker --version
                    docker compose version

                    python3 -m venv "$VENV"
                    "$VENV/bin/python" -m pip install --upgrade pip
                    "$VENV/bin/python" -m pip install -r requirements.txt
                    "$VENV/bin/python" -m pip install \
                        bandit \
                        pip-audit \
                        black \
                        isort \
                        flake8 \
                        mypy \
                        pytest

                    mkdir -p "$REPORT_DIR/sqlmap"
                    : > "$REPORT_DIR/pipeline_issues.txt"
                    : > "$REPORT_DIR/check_summary.txt"

                    # Scanner images may run as non-root users.
                    chmod -R 0777 "$REPORT_DIR"
                '''
            }
        }

        stage('Static Checks') {
            steps {
                script {
                    String summaryFile = "${env.REPORT_DIR}/check_summary.txt"
                    String issueFile = "${env.REPORT_DIR}/pipeline_issues.txt"

                    def recordResult = { String label, int status, String passNote = 'PASS' ->
                        String summary = fileExists(summaryFile) ? readFile(summaryFile) : ''
                        String resultLine = status == 0
                            ? "${label}: ${passNote}"
                            : "${label}: FAIL (exit ${status})"

                        writeFile(file: summaryFile, text: summary + resultLine + '\n')

                        if (status != 0) {
                            echo "[WARNING] ${label} failed with exit code ${status}"
                            String currentIssues = fileExists(issueFile) ? readFile(issueFile) : ''
                            writeFile(
                                file: issueFile,
                                text: currentIssues + "${label}: exit ${status}\n"
                            )
                        }
                    }

                    def runCheck = { String label, String command ->
                        int status = sh(script: command, returnStatus: true)
                        recordResult(label, status)
                    }

                    runCheck('secret detection', '''"$VENV/bin/python" scripts/check_secrets.py''')
                    runCheck('python syntax check', '''"$VENV/bin/python" scripts/check_python_syntax.py''')
                    runCheck('application health check', '''"$VENV/bin/python" scripts/check_app_health.py''')
                    runCheck('black', '''"$VENV/bin/python" -m black --check app main.py scripts''')
                    runCheck('isort', '''"$VENV/bin/python" -m isort --check-only app main.py scripts''')
                    runCheck('flake8', '''"$VENV/bin/python" -m flake8 app main.py scripts''')
                    runCheck('mypy', '''"$VENV/bin/python" -m mypy app''')
                    runCheck('bandit', '''"$VENV/bin/python" -m bandit -r app main.py scripts -f json -o "$REPORT_DIR/bandit.json"''')
                    runCheck('pip-audit', '''"$VENV/bin/python" -m pip_audit -r requirements.txt -f json -o "$REPORT_DIR/pip-audit.json"''')

                    // Do not use -v "$PWD:/workspace" from Dockerized Jenkins.
                    runCheck('semgrep', '''
                        docker run --rm \
                          --volumes-from "$JENKINS_CONTAINER" \
                          -w "$WORKSPACE" \
                          returntocorp/semgrep:latest \
                          semgrep scan \
                          --config=p/ci \
                          --error \
                          --json \
                          --output "$REPORT_DIR/semgrep.json" \
                          .
                    ''')

                    runCheck('hadolint', '''
                        docker run --rm \
                          --volumes-from "$JENKINS_CONTAINER" \
                          -w "$WORKSPACE" \
                          hadolint/hadolint:latest-debian \
                          hadolint docker/Dockerfile
                    ''')

                    int pytestStatus = sh(
                        script: '"$VENV/bin/python" -m pytest',
                        returnStatus: true
                    )

                    if (pytestStatus == 5) {
                        echo 'Pytest found no tests. Continuing.'
                        recordResult('pytest', 0, 'PASS (no tests found)')
                    } else {
                        recordResult('pytest', pytestStatus)
                    }
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    int buildStatus = sh(
                        script: '''
                            docker compose \
                              -p "$COMPOSE_PROJECT_NAME" \
                              -f docker/docker-compose.yml \
                              build db app
                        ''',
                        returnStatus: true
                    )

                    String summaryFile = "${env.REPORT_DIR}/check_summary.txt"
                    String issueFile = "${env.REPORT_DIR}/pipeline_issues.txt"
                    String summary = fileExists(summaryFile) ? readFile(summaryFile) : ''

                    if (buildStatus != 0) {
                        echo "[WARNING] Docker Compose build failed with exit code ${buildStatus}"
                        String currentIssues = fileExists(issueFile) ? readFile(issueFile) : ''
                        writeFile(
                            file: issueFile,
                            text: currentIssues + "docker compose build: exit ${buildStatus}\n"
                        )
                        writeFile(
                            file: summaryFile,
                            text: summary + "docker compose build: FAIL (exit ${buildStatus})\n"
                        )
                    } else {
                        writeFile(
                            file: summaryFile,
                            text: summary + "docker compose build: PASS\n"
                        )
                    }
                }
            }
        }

        stage('Dynamic Checks') {
            steps {
                script {
                    String summaryFile = "${env.REPORT_DIR}/check_summary.txt"
                    String issueFile = "${env.REPORT_DIR}/pipeline_issues.txt"

                    def recordResult = { String label, int status, String passNote = 'PASS' ->
                        String summary = fileExists(summaryFile) ? readFile(summaryFile) : ''
                        String resultLine = status == 0
                            ? "${label}: ${passNote}"
                            : "${label}: FAIL (exit ${status})"

                        writeFile(file: summaryFile, text: summary + resultLine + '\n')

                        if (status != 0) {
                            echo "[WARNING] ${label} failed with exit code ${status}"
                            String currentIssues = fileExists(issueFile) ? readFile(issueFile) : ''
                            writeFile(
                                file: issueFile,
                                text: currentIssues + "${label}: exit ${status}\n"
                            )
                        }
                    }

                    def runCheck = { String label, String command ->
                        int status = sh(script: command, returnStatus: true)
                        recordResult(label, status)
                        return status
                    }

                    int composeStatus = sh(
                        script: '''
                            docker compose \
                              -p "$COMPOSE_PROJECT_NAME" \
                              -f docker/docker-compose.yml \
                              up -d --no-build db app
                        ''',
                        returnStatus: true
                    )

                    recordResult('docker compose up', composeStatus)

                    if (composeStatus != 0) {
                        sh '''
                            echo "===== Compose status ====="
                            docker compose \
                              -p "$COMPOSE_PROJECT_NAME" \
                              -f docker/docker-compose.yml \
                              ps -a || true

                            echo "===== PostgreSQL logs ====="
                            docker compose \
                              -p "$COMPOSE_PROJECT_NAME" \
                              -f docker/docker-compose.yml \
                              logs --no-color db || true

                            echo "===== Application logs ====="
                            docker compose \
                              -p "$COMPOSE_PROJECT_NAME" \
                              -f docker/docker-compose.yml \
                              logs --no-color app || true
                        '''
                    }

                    int readinessStatus = 1

                    if (composeStatus == 0) {
                        readinessStatus = sh(
                            script: '''
                                attempt=1

                                while [ "$attempt" -le 30 ]; do
                                    if "$VENV/bin/python" - <<'PY'
import os
from urllib.request import urlopen

url = os.environ["APP_URL"] + "/openapi.json"
urlopen(url, timeout=2).read()
PY
                                    then
                                        exit 0
                                    fi

                                    attempt=$((attempt + 1))
                                    sleep 2
                                done

                                exit 1
                            ''',
                            returnStatus: true
                        )
                    } else {
                        echo 'Skipping readiness polling because Compose startup failed.'
                    }

                    recordResult('openapi readiness', readinessStatus)

                    runCheck('trivy', '''
                        docker run --rm \
                          --volumes-from "$JENKINS_CONTAINER" \
                          -w "$WORKSPACE" \
                          aquasec/trivy:latest \
                          image \
                          --severity HIGH,CRITICAL \
                          --exit-code 0 \
                          --format json \
                          --output "$REPORT_DIR/trivy.json" \
                          "$APP_IMAGE"
                    ''')

                    if (readinessStatus == 0) {
                        runCheck('zap', '''
                            docker run --rm \
                              --network "${COMPOSE_PROJECT_NAME}_default" \
                              --volumes-from "$JENKINS_CONTAINER" \
                              -w "$WORKSPACE" \
                              owasp/zap2docker-stable \
                              zap-api-scan.py \
                              -t "$INTERNAL_APP_URL/openapi.json" \
                              -f openapi \
                              -r "$REPORT_DIR/zap.html" \
                              -J "$REPORT_DIR/zap.json"
                        ''')

                        runCheck('nmap', '''
                            docker run --rm \
                              --network "${COMPOSE_PROJECT_NAME}_default" \
                              --volumes-from "$JENKINS_CONTAINER" \
                              -w "$WORKSPACE" \
                              instrumentisto/nmap:latest \
                              -Pn \
                              -p 8000 \
                              -oN "$REPORT_DIR/nmap.txt" \
                              app
                        ''')

                        runCheck('sqlmap', '''
                            while IFS='|' read -r method url data; do
                                [ -z "$method" ] && continue

                                case "$method" in
                                    "#"*) continue ;;
                                esac

                                if [ "$method" = "POST" ]; then
                                    docker run --rm \
                                      --network "${COMPOSE_PROJECT_NAME}_default" \
                                      --volumes-from "$JENKINS_CONTAINER" \
                                      -w "$WORKSPACE" \
                                      sqlmapproject/sqlmap \
                                      sqlmap \
                                      -u "$url" \
                                      --data="$data" \
                                      --method=POST \
                                      --batch \
                                      --risk=1 \
                                      --level=1 \
                                      --output-dir="$REPORT_DIR/sqlmap"
                                else
                                    docker run --rm \
                                      --network "${COMPOSE_PROJECT_NAME}_default" \
                                      --volumes-from "$JENKINS_CONTAINER" \
                                      -w "$WORKSPACE" \
                                      sqlmapproject/sqlmap \
                                      sqlmap \
                                      -u "$url" \
                                      --batch \
                                      --risk=1 \
                                      --level=1 \
                                      --output-dir="$REPORT_DIR/sqlmap"
                                fi
                            done < endpoints.txt
                        ''')
                    } else {
                        echo 'Skipping ZAP, Nmap and SQLMap because the application is not ready.'
                        recordResult('zap', 0, 'SKIPPED (application unavailable)')
                        recordResult('nmap', 0, 'SKIPPED (application unavailable)')
                        recordResult('sqlmap', 0, 'SKIPPED (application unavailable)')
                    }
                }
            }
        }

        stage('Generate Report') {
            steps {
                script {
                    String summary = fileExists("${env.REPORT_DIR}/check_summary.txt")
                        ? readFile("${env.REPORT_DIR}/check_summary.txt").trim()
                        : ''

                    String issues = fileExists("${env.REPORT_DIR}/pipeline_issues.txt")
                        ? readFile("${env.REPORT_DIR}/pipeline_issues.txt").trim()
                        : ''

                    if (issues) {
                        currentBuild.result = 'UNSTABLE'
                    }

                    writeFile(
                        file: "${env.REPORT_DIR}/final-report.txt",
                        text: """CI/CD and security pipeline completed.

Check summary:
${summary ? summary : 'No checks recorded.'}

Collected outputs:
- reports/bandit.json
- reports/pip-audit.json
- reports/semgrep.json
- reports/trivy.json
- reports/zap.html
- reports/zap.json
- reports/nmap.txt
- reports/sqlmap/

Recorded issues:
${issues ? issues : 'None'}
"""
                    )
                }
            }
        }
    }

    post {
        always {
            sh '''
                docker compose \
                  -p "$COMPOSE_PROJECT_NAME" \
                  -f docker/docker-compose.yml \
                  down -v || true
            '''

            archiveArtifacts(
                artifacts: 'reports/**/*',
                allowEmptyArchive: true
            )
        }

        unstable {
            echo 'Pipeline completed with warnings. Review reports/final-report.txt and reports/pipeline_issues.txt.'
        }

        success {
            echo 'All pipeline checks completed successfully.'
        }
    }
}