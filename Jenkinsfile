pipeline {
    agent any

    options {
        timestamps()
        skipDefaultCheckout(true)
    }

    environment {
        VENV = "${WORKSPACE}/.venv"
        REPORT_DIR = "${WORKSPACE}/reports"
        APP_IMAGE = "you-want-ticket:ci"
        COMPOSE_PROJECT_NAME = "you-want-ticket-ci"
        APP_URL = "http://127.0.0.1:8000"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Environment') {
            steps {
                sh '''
                    set -eu
                    python3 --version
                    python3 -m venv "$VENV"
                    "$VENV/bin/python" -m pip install --upgrade pip
                    "$VENV/bin/python" -m pip install -r requirements.txt
                    "$VENV/bin/python" -m pip install bandit pip-audit
                    mkdir -p "$REPORT_DIR"
                    : > "$REPORT_DIR/pipeline_issues.txt"
                    : > "$REPORT_DIR/check_summary.txt"
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
                        String resultLine = status == 0 ? "${label}: ${passNote}" : "${label}: FAIL (exit ${status})"
                        writeFile(file: summaryFile, text: summary + resultLine + '\n')

                        if (status != 0) {
                            echo "[WARNING] ${label} failed with exit code ${status}"
                            String currentIssues = fileExists(issueFile) ? readFile(issueFile) : ''
                            writeFile(file: issueFile, text: currentIssues + "${label}: exit ${status}\n")
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
                    runCheck('semgrep', '''docker run --rm -v "$PWD:/workspace" -w /workspace returntocorp/semgrep:latest semgrep scan --config=p/ci --error --json --output reports/semgrep.json .''')
                    runCheck('hadolint', '''docker run --rm -v "$PWD:/workspace" -w /workspace hadolint/hadolint:latest-debian hadolint docker/Dockerfile''')

                    int pytestStatus = sh(script: '"$VENV/bin/python" -m pytest', returnStatus: true)
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
                    int buildStatus = sh(script: 'docker build -f docker/Dockerfile -t "$APP_IMAGE" .', returnStatus: true)
                    String summaryFile = "${env.REPORT_DIR}/check_summary.txt"
                    String issueFile = "${env.REPORT_DIR}/pipeline_issues.txt"
                    String summary = fileExists(summaryFile) ? readFile(summaryFile) : ''
                    if (buildStatus != 0) {
                        echo "[WARNING] docker build failed with exit code ${buildStatus}"
                        String currentIssues = fileExists(issueFile) ? readFile(issueFile) : ''
                        writeFile(file: issueFile, text: currentIssues + "docker build: exit ${buildStatus}\n")
                        writeFile(file: summaryFile, text: summary + "docker build: FAIL (exit ${buildStatus})\n")
                    } else {
                        writeFile(file: summaryFile, text: summary + "docker build: PASS\n")
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
                        String resultLine = status == 0 ? "${label}: ${passNote}" : "${label}: FAIL (exit ${status})"
                        writeFile(file: summaryFile, text: summary + resultLine + '\n')

                        if (status != 0) {
                            echo "[WARNING] ${label} failed with exit code ${status}"
                            String currentIssues = fileExists(issueFile) ? readFile(issueFile) : ''
                            writeFile(file: issueFile, text: currentIssues + "${label}: exit ${status}\n")
                        }
                    }

                    def runCheck = { String label, String command ->
                        int status = sh(script: command, returnStatus: true)
                        recordResult(label, status)
                    }

                    runCheck('docker compose up', '''docker compose -p "$COMPOSE_PROJECT_NAME" -f docker/docker-compose.yml up -d db app''')
                    runCheck('openapi readiness', '''
attempt=1
while [ "$attempt" -le 30 ]; do
    if "$VENV/bin/python" - <<'PY'
from urllib.request import urlopen
urlopen("http://127.0.0.1:8000/openapi.json", timeout=2).read()
PY
    then
        exit 0
    fi
    attempt=$((attempt + 1))
    sleep 2
done
exit 1
''')
                    runCheck('trivy', '''docker run --rm --network "${COMPOSE_PROJECT_NAME}_default" -v "$PWD:/workspace" -w /workspace aquasec/trivy:latest image --severity HIGH,CRITICAL --exit-code 0 --format json --output /workspace/reports/trivy.json "$APP_IMAGE"''')
                    runCheck('zap', '''docker run --rm --network "${COMPOSE_PROJECT_NAME}_default" -v "$PWD:/workspace" -w /workspace owasp/zap2docker-stable zap-api-scan.py -t "$APP_URL/openapi.json" -f openapi -r /workspace/reports/zap.html -J /workspace/reports/zap.json''')
                    runCheck('nmap', '''docker run --rm --network "${COMPOSE_PROJECT_NAME}_default" -v "$PWD:/workspace" -w /workspace instrumentisto/nmap:latest -Pn -p 8000 -oN /workspace/reports/nmap.txt app''')
                    runCheck('sqlmap', '''
while IFS='|' read -r method url data; do
    [ -z "$method" ] && continue
    case "$method" in
        #*) continue ;;
    esac

    if [ "$method" = "POST" ]; then
        docker run --rm --network "${COMPOSE_PROJECT_NAME}_default" -v "$PWD:/workspace" -w /workspace sqlmapproject/sqlmap sqlmap -u "$url" --data="$data" --method=POST --batch --risk=1 --level=1 --output-dir=/workspace/reports/sqlmap
    else
        docker run --rm --network "${COMPOSE_PROJECT_NAME}_default" -v "$PWD:/workspace" -w /workspace sqlmapproject/sqlmap sqlmap -u "$url" --batch --risk=1 --level=1 --output-dir=/workspace/reports/sqlmap
    fi
done < endpoints.txt
''')
                }
            }
        }

        stage('Generate Report') {
            steps {
                script {
                    String summary = ''
                    if (fileExists("${env.REPORT_DIR}/check_summary.txt")) {
                        summary = readFile("${env.REPORT_DIR}/check_summary.txt").trim()
                    }

                    String issues = ''
                    if (fileExists("${env.REPORT_DIR}/pipeline_issues.txt")) {
                        issues = readFile("${env.REPORT_DIR}/pipeline_issues.txt").trim()
                    }

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
            sh 'docker compose -p "$COMPOSE_PROJECT_NAME" -f docker/docker-compose.yml down -v || true'
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
        }

        unstable {
            echo 'Pipeline completed with warnings. Review reports/final-report.txt and reports/pipeline_issues.txt.'
        }

        success {
            echo 'All pipeline checks completed successfully.'
        }
    }
}