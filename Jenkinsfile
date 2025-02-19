pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        timestamps()
    }
    ub'
    environment {
        registry = 'nvlinh99/brain-tumor-detection'
        registryCredential = 'dockerh
    }
    
    stages {
        stage('Test') {
            steps {
                script {
                    echo 'Running tests...'
                    // Build a temporary test image
                    sh '''
                        docker build -t test-image -f Dockerfile .
                        docker run --rm test-image bash -c "cd /app/api && pytest -v"
                        docker rmi test-image
                    '''
                }
            }
        }


        stage('Build') {
            steps {
                script {
                    echo 'Building image for deployment...'
                    sh "docker rmi -f ${registry}:$BUILD_NUMBER || true"
                    sh "docker rmi -f ${registry}:latest || true"
                    
                    dockerImage = docker.build registry + ":$BUILD_NUMBER", "./"
                    
                    echo 'Pushing image to dockerhub...'
                    docker.withRegistry('', registryCredential) {
                        dockerImage.push()
                        dockerImage.push('latest')
                    }
                }
            }
        }

        stage('Deploy') {
            agent {
                kubernetes {
                    containerTemplate {
                        name 'helm'
                        image 'nvlinh99/jenkins-docker-helm:latest'
                        alwaysPullImage true
                    }
                }
            }
            steps {
                dir('charts/brain-tumor-detection') {
                    script {
                        container('helm') {
                            sh """
                                kubectl delete pods -n model-serving -l app=brain-tumor-detection || true
                                helm upgrade --install brain-tumor-detection . \
                                    --namespace model-serving \
                                    --set image.pullPolicy=Always \
                                    --set image.tag=${BUILD_NUMBER}
                            """
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            sh "docker rmi -f ${registry}:$BUILD_NUMBER || true"
            sh "docker rmi -f ${registry}:latest || true"
        }
        failure {
            echo 'Pipeline failed!'
        }
        success {
            echo 'Pipeline succeeded!'
        }
    }
}