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
			error ("EXIT TEST, REMOVE WHEN WORKS")
      		}
    	}

    	stage('Start GNS33 Test Stage') {
      		steps {
        		sh 'python3 -u startcicd.py startgns3 teststage'
			sleep(time: 25)
      		}
	}

	stage("Stage Test: Deploy Test network") {
		environment {
			LS = "${sh(script:'python3 -u startcicd.py launchawx teststage deploy | grep "proceed"', returnStdout: true).trim()}"
    		}
                            
		steps {
			script {
				echo "${env.LS}"
				if (env.LS == 'proceed = True') {
            				sh "echo 'Proceed to TEST stage fase PINGTESTS'"
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
            				sh "echo 'Proceed to PROD stage fase Deploy'"
        			} else {
            				error ("There were failures in the job template execution. Pipeline stops here.")
        			}
			}
		}
        }
  }
}

