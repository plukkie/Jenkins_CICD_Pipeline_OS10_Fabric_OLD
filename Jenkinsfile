pipeline {
  agent any
  stages {
	stage('Build') {
		steps {
			sh 'python -m pip3 install --upgrade pip'
			sh 'pip3 install -r pyrequirements.txt'
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

