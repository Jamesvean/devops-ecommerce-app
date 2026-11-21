
pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'devops-ecommerce:v1'
        COMPOSE = '/usr/libexec/docker/cli-plugins/docker-compose'
        PROJECT_NAME = 'devops-ecommerce-phase1'
    }

    stages {
        stage('Checkout Source') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Python Tests') {
            steps {
                sh '''
                    set -eu
                    python3 -m venv .ci-venv
                    . .ci-venv/bin/activate
                    python -m pip install -r requirements.txt
                    python -m pytest -v --junitxml=pytest-results.xml
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    set -eu
                    docker build -t "$IMAGE_NAME" .
                    docker image inspect "$IMAGE_NAME" --format '{{.Id}}'
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    set -eu
                    trivy image --scanners vuln \
                        --severity HIGH,CRITICAL \
                        --exit-code 0 \
                        --format json \
                        --output trivy-report.json \
                        "$IMAGE_NAME"

                    trivy image --scanners vuln \
                        --severity HIGH,CRITICAL \
                        --exit-code 0 \
                        "$IMAGE_NAME"
                '''
            }
        }

        stage('Deploy Docker Compose') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'ecommerce-secret-key',
                        variable: 'SECRET_KEY'
                    )
                ]) {
                    sh '''
                        set -eu
                        "$COMPOSE" -p "$PROJECT_NAME" \
                            -f compose.yaml \
                            up -d --no-build \
                            --force-recreate ecommerce
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'ecommerce-secret-key',
                        variable: 'SECRET_KEY'
                    )
                ]) {
                    sh '''
                        set -eu
                        attempts=0

                        until curl --fail --silent \
                            http://127.0.0.1:5001/health
                        do
                            attempts=$((attempts + 1))

                            if [ "$attempts" -ge 12 ]; then
                                echo "Health check failed"
                                exit 1
                            fi

                            sleep 5
                        done

                        echo
                        echo "Health check successful"

                        "$COMPOSE" -p "$PROJECT_NAME" \
                            -f compose.yaml ps

                        echo "Deployment verification successful"
                    '''
                }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true,
                  testResults: 'pytest-results.xml'

            archiveArtifacts(
                artifacts: 'trivy-report.json',
                allowEmptyArchive: true
            )
        }

        success {
            echo 'CI/CD pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Check the console log.'
        }
    }
}

