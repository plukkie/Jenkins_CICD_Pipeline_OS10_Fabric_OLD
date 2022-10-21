pipeline {
  agent none
  stages {
	stage('Build') {
		steps {
			sh 'pip install --user .'
			sh 'python3 -m py_compile rungns3.py'
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

