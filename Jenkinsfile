pipeline {
  agent none
  stages {
	stage('Build') {
		agent {
			docker {
				image 'python:2-alphine'
			}
		}
		steps {
			sh 'python -m py_compile rungns3.py'
			stash(name: 'compiled-results', includes: '*.py*')
		}
	}

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

