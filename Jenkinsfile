pipeline {
  agent any
  stages {
    stage('version') {
      steps {
        sh 'python3 --version'
      }
    }
    stage('start gns3') {
      steps {
        sh 'python3 rungns3.py start'
      }
    }
  }
}
