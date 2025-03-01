pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '5', daysToKeepStr: '5'))
        timestamps()
    }

    environment {
        registry = 'nvlinh99/brain-tumor-detection'
        registryCredential = 'dockerhub'
    }

    stages {
        stage('Build') {
            steps {
                script {
                    echo 'Building image for deployment...'
                    sh "DOCKER_BUILDKIT=1 docker build -t ${registry}:${BUILD_NUMBER} ."
                    
                    echo 'Pushing image to Docker Hub...'
                    docker.withRegistry('', registryCredential) {
                        sh """
                            docker push ${registry}:${BUILD_NUMBER} --quiet
                            docker tag ${registry}:${BUILD_NUMBER} ${registry}:latest
                            docker push ${registry}:latest --quiet
                        """
                    }
                }
            }
        }

        stage('Deploy') {
            agent {
                kubernetes {
                    yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: jenkins-agent
spec:
  containers:
    - name: helm
      image: nvlinh99/jenkins-docker-helm:latest
      imagePullPolicy: Always
      command:
        - cat
      tty: true
"""
                }
            }
            
            steps {
                container('helm') {
                    dir('charts/brain-tumor-detection') {
                        script {
                            sh """
                                echo 'Rolling out new version...'
                                helm upgrade --install brain-tumor-detection . \
                                    --namespace model-serving \
                                    --set image.pullPolicy=Always \
                                    --set image.tag=${BUILD_NUMBER} \
                                    --wait --timeout 300s
                            """
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up...'
            sh "docker rmi -f ${registry}:${BUILD_NUMBER} || true"
            sh "docker rmi -f ${registry}:latest || true"
        }
        failure {
            echo '❌ Pipeline failed! Check logs.'
        }
        success {
            echo '✅ Pipeline succeeded!'
        }
    }
}