pipeline {
    agent any

    environment {
        username = "pvdr8978"
        password = "PVdr@8978"
        name = "flask"
    }

    stages {

        stage('checkout') {
            steps {
                git branch: "main",
                    url: "https://github.com/venkatadurgaraoponnaganti/ai-chatbot"
            }
        }

        stage('build') {
            steps {
                sh '''
                    echo "Building Docker image..."
                    docker build -t "$username/$name" .
                '''
            }
        }

        stage('deploy') {
            steps {
                sh '''
                    echo "Logging in to Docker Hub..."
                    echo "$password" | docker login -u "$username" --password-stdin

                    echo "Pushing image to Docker Hub..."
                    docker push "$username/$name"
                '''
            }
        }

        stage('run') {
            steps {
                withCredentials([string(credentialsId: 'api', variable: 'OPENAIKEY')]) {
                    sh '''
                        echo "Stopping old container..."
                        docker stop flask-container || true
                        docker rm flask-container || true

                        echo "Running new container..."
                        docker run -d --name flask-container -p 5000:5000 \
                            -e OPENAI_API_KEY="$OPENAIKEY" \
                            "$username/$name"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline Success!"
        }
        failure {
            echo "Pipeline Failed!"
        }
    }
}

