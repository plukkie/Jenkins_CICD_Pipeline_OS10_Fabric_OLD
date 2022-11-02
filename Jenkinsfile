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

    	stage('Start GNS3 Stage TEST') {
      		steps {
			echo 'Request API call to GNS3 server to start Test fabric.'
        		sh 'python3 -u startcicd.py startgns3 teststage'
			echo 'Waiting for systems te become active'
			sleep( time: 120 )
      		}
	}

	stage("Stage TEST: Deploy Test network") {
		environment {
			LS = "${sh(script:'python3 -u startcicd.py launchawx teststage deploy | grep "proceed"', returnStdout: true).trim()}"
    		}
                            
		steps {
			script {
				echo 'Waiting till network deployment has finished. This can take couple of minutes.'
				echo "${env.LS}"
				if (env.LS == 'proceed = True') {
            				echo 'Proceed to Stage TEST fase Ping Tests'
        			} else {
            				error ("There were failures in the job template execution. Pipeline stops here.")
        			}
			}
		}
        }
	  
	stage("Stage TEST: Start connectivity Tests") {
		environment {
			LS = "${sh(script:'python3 -u startcicd.py launchawx teststage test | grep "proceed"', returnStdout: true).trim()}"
    		}
            
		steps {
			script {
				echo 'Waiting till network ping tests has finished. This can take some minutes.'
				echo "${env.LS}"
				if (env.LS == 'proceed = True') {
					echo 'SUCCESS. Shutting down Test network'
					sh 'python3 -u startcicd.py stopgns3 teststage'
            				echo 'Proceed to Stage PROD fase Deploy'
        			} else {
            				error ("There were failures in the job template execution. Pipeline stops here.")
        			}
			}
		}
        }
  }
}

