pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Install') {
            steps {
                sh 'python -m pip install --upgrade pip'
                sh 'python -m pip install -r requirements.txt'
            }
        }

        stage('Static Health') {
            steps {
                sh 'python scripts/check_secrets.py'
                sh 'python scripts/check_python_syntax.py'
                sh 'python scripts/check_app_health.py'
            }
        }

        stage('Tests and Types') {
            steps {
                sh '''
                    python -m pytest
                    status=$?
                    if [ "$status" -ne 0 ] && [ "$status" -ne 5 ]; then
                        exit "$status"
                    fi
                '''
                sh 'python -m mypy app'
            }
        }
    }
}