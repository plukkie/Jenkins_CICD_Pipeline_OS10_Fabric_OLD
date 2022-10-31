pipeline {
  agent any
  stages {
	stage('Build') {
		steps {
			sh 'pip install -r pyrequirements.txt'
			sh 'python3 -m py_compile startcicd.py'
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
        		sh 'python3 -u startcicd.py startgns3'
			sleep(time: 30)
      		}
	}

	stage("Configure GNS3") {
		environment {
        		LS = "${sh(script:'python3 -u startcicd.py launchawx | grep proceed', returnStdout: true).trim()}"
    		}
            
		steps {
                	echo "LS = ${env.LS}"
		
		script {
		if (env.LS == 'main') {
            		echo 'Hello from main branch'
        	} else {
            		sh "echo 'else was reached'"
        	}
		}
		}
        }
	  
	
  }
}

