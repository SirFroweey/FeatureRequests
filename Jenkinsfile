pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/SirFroweey/FeatureRequests'
            }
        }
        stage('Build') {
            steps {
                sh 'sudo service apache2 restart'
            }
        }
    }
}
