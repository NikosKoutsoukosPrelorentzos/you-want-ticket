pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        VENV = "${WORKSPACE}/.venv"
    }

    stages {
        stage('Create Environment') {
            steps {
                sh '''
                    python3 --version
                    python3 -m venv "$VENV"
                    "$VENV/bin/python" -m pip install --upgrade pip
                '''
            }
        }

        stage('Install') {
            steps {
                sh '''
                    "$VENV/bin/python" -m pip install -r requirements.txt
                '''
            }
        }

        stage('Static Health') {
            steps {
                sh '''
                    "$VENV/bin/python" scripts/check_secrets.py
                    "$VENV/bin/python" scripts/check_python_syntax.py
                    "$VENV/bin/python" scripts/check_app_health.py
                '''
            }
        }

        stage('Tests and Types') {
            steps {
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

                sh '''
                    "$VENV/bin/python" -m mypy app
                '''
            }
        }
    }

    post {
        success {
            echo 'All pipeline checks completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Review the failed stage above.'
        }
    }
}