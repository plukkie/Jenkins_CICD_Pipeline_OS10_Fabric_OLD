pipeline {
  agent any
	
  environment {
	  PROCEED = false
  }
  
  stages {
	  script {
	  if ( env.PROCEED == false ) { return }
	  }
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

	stage("Deploy GNS3 test Stage") {
		environment {
			LS = "${sh(script:'python3 -u startcicd.py launchawx teststage deploy | grep "proceed"', returnStdout: true).trim()}"
    		}
            
		steps {
                	
			script {
				echo "${env.LS}"
				if (env.LS == 'proceed = True') {
            				sh "echo 'Proceed to TEST stage fase PINGTESTS'"
        			} else {
            				error "There were failures in the job template execution. Pipeline stops here."
					sh 'exit 0'
        			}
			}
		}
        }
	  
	stage("Start connectivity Tests GNS3 on test Stage") {
		environment {
			LS = "${sh(script:'python3 -u startcicd.py launchawx teststage test | grep "proceed"', returnStdout: true).trim()}"
    		}
            
		steps {
                	
			script {
				echo "${env.LS}"
				if (env.LS == 'proceed = True') {
            				sh "echo 'Proceed to PROD stage fase Deploy'"
        			} else {
            				error "There were failures in the job template execution. Pipeline stops here."
					sh 'exit 0'
        			}
			}
		}
        }
  }
}

