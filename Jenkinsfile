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

    	stage('Start GNS33 Stage TEST') {
      		steps {
        		sh 'python3 -u startcicd.py startgns3 teststage'
			sleep( time: 20 )
      		}
	}

	stage("Stage TEST: Deploy Test network") {
		environment {
			LS = "${sh(script:'python3 -u startcicd.py launchawx teststage deploy | grep "proceed"', returnStdout: true).trim()}"
    		}
                            
		steps {
			script {
				echo "${env.LS}"
				if (env.LS == 'proceed = True') {
            				sh "echo 'Proceed to Sttage TEST fase Ping Tests'"
        			} else {
            				error ("There were failures in the job template execution. Pipeline stops here.")
        			}
			}
		}
        }
	  
	stage("Stage Test: Start connectivity Tests") {
		environment {
			LS = "${sh(script:'python3 -u startcicd.py launchawx teststage test | grep "proceed"', returnStdout: true).trim()}"
    		}
            
		steps {
                	
			script {
				echo "${env.LS}"
				if (env.LS == 'proceed = True') {
            				sh "echo 'Proceed to Stage PROD fase Deploy'"
        			} else {
            				error ("There were failures in the job template execution. Pipeline stops here.")
        			}
			}
		}
        }
  }
}

