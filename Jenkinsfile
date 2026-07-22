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
                '''
            }
        }

        stage('Static Checks') {
            steps {
                sh '''
                    set -eu
                    "$VENV/bin/python" scripts/check_secrets.py
                    "$VENV/bin/python" scripts/check_python_syntax.py
                    "$VENV/bin/python" scripts/check_app_health.py
                    "$VENV/bin/python" -m black --check app main.py scripts
                    "$VENV/bin/python" -m isort --check-only app main.py scripts
                    "$VENV/bin/python" -m flake8 app main.py scripts
                    "$VENV/bin/python" -m mypy app
                    "$VENV/bin/python" -m bandit -r app main.py scripts -f json -o "$REPORT_DIR/bandit.json"
                    "$VENV/bin/python" -m pip_audit -r requirements.txt -f json -o "$REPORT_DIR/pip-audit.json"
                '''

                sh '''
                    set -eu
                    docker run --rm \
                        -v "$PWD:/workspace" \
                        -w /workspace \
                        returntocorp/semgrep:latest \
                        semgrep scan --config=p/ci --error --json --output reports/semgrep.json .
                '''

                sh '''
                    set -eu
                    docker run --rm \
                        -v "$PWD:/workspace" \
                        -w /workspace \
                        hadolint/hadolint:latest-debian \
                        hadolint docker/Dockerfile
                '''

                script {
                    int pytestStatus = sh(
                        script: '"$VENV/bin/python" -m pytest',
                        returnStatus: true
                    )

                    if (pytestStatus != 0 && pytestStatus != 5) {
                        error("Pytest failed with exit code ${pytestStatus}")
                    }

                    if (pytestStatus == 5) {
                        echo 'Pytest found no tests. Continuing.'
                    }
                }
            }
        }

        stage('Build') {
            steps {
                sh '''
                    set -eu
                    docker build -f docker/Dockerfile -t "$APP_IMAGE" .
                '''
            }
        }

        stage('Dynamic Checks') {
            steps {
                sh '''
                    set -eu
                    docker compose -p "$COMPOSE_PROJECT_NAME" -f docker/docker-compose.yml up -d db app

                    for attempt in $(seq 1 30); do
                        if "$VENV/bin/python" - <<'PY'
from urllib.request import urlopen
urlopen("http://127.0.0.1:8000/openapi.json", timeout=2).read()
PY
                        then
                            break
                        fi
                        sleep 2
                    done

                    "$VENV/bin/python" - <<'PY'
from urllib.request import urlopen
urlopen("http://127.0.0.1:8000/openapi.json", timeout=5).read()
PY

                    docker run --rm \
                        --network "${COMPOSE_PROJECT_NAME}_default" \
                        -v "$PWD:/workspace" \
                        -w /workspace \
                        aquasec/trivy:latest \
                        image --severity HIGH,CRITICAL --exit-code 0 --format json \
                        --output /workspace/reports/trivy.json "$APP_IMAGE"

                    docker run --rm \
                        --network "${COMPOSE_PROJECT_NAME}_default" \
                        -v "$PWD:/workspace" \
                        -w /workspace \
                        owasp/zap2docker-stable \
                        zap-api-scan.py -t "$APP_URL/openapi.json" -f openapi \
                        -r /workspace/reports/zap.html -J /workspace/reports/zap.json

                    docker run --rm \
                        --network "${COMPOSE_PROJECT_NAME}_default" \
                        -v "$PWD:/workspace" \
                        -w /workspace \
                        instrumentisto/nmap:latest \
                        -Pn -p 8000 -oN /workspace/reports/nmap.txt app

                    while IFS='|' read -r method url data; do
                        [ -z "$method" ] && continue
                        case "$method" in
                            \#*) continue ;;
                        esac

                        if [ "$method" = "POST" ]; then
                            docker run --rm \
                                --network "${COMPOSE_PROJECT_NAME}_default" \
                                -v "$PWD:/workspace" \
                                -w /workspace \
                                sqlmapproject/sqlmap \
                                sqlmap -u "$url" --data="$data" --method=POST \
                                --batch --risk=1 --level=1 --output-dir=/workspace/reports/sqlmap
                        else
                            docker run --rm \
                                --network "${COMPOSE_PROJECT_NAME}_default" \
                                -v "$PWD:/workspace" \
                                -w /workspace \
                                sqlmapproject/sqlmap \
                                sqlmap -u "$url" --batch --risk=1 --level=1 \
                                --output-dir=/workspace/reports/sqlmap
                        fi
                    done < endpoints.txt
                '''
            }
        }

        stage('Generate Report') {
            steps {
                sh '''
                    set -eu
                    cat > "$REPORT_DIR/final-report.txt" <<'EOF'
CI/CD and security pipeline completed.

Collected outputs:
- reports/bandit.json
- reports/pip-audit.json
- reports/semgrep.json
- reports/trivy.json
- reports/zap.html
- reports/zap.json
- reports/nmap.txt
- reports/sqlmap/
EOF
                '''
            }
        }
    }

    post {
        always {
            sh 'docker compose -p "$COMPOSE_PROJECT_NAME" -f docker/docker-compose.yml down -v || true'
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
        }

        success {
            echo 'All pipeline checks completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Review the archived reports and the failed stage above.'
        }
    }
}