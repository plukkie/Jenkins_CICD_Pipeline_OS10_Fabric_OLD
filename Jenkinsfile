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

    	stage('Start GNS33 Test Stage') {
      		steps {
        		sh 'python3 -u startcicd.py startgns3 teststage'
			sleep(time: 25)
      		}
	}

	stage("Configure GNS3 test Stage") {
		environment {
			LS = "${sh(script:'python3 -u startcicd.py launchawx | grep "proceed"', returnStdout: true).trim()}"
    		}
            
		steps {
                	
			script {
				echo "${env.LS}"
				if (env.LS == 'proceed = True') {
            				sh "echo 'start connectivity tests'"
        			} else {
            				error "There were failures in the job template execution. Pipeline stops here."
        			}
			}
		}
        }
	  
  }
}

