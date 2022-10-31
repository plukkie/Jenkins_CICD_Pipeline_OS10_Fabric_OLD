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
			sleep(time: 10)
      		}
	}

	stage("Configure GNS3") {
		environment {
        		LS = "${sh(script:'python3 -u startcicd.py launchawx', returnStdout: true).trim()}"
			proceed = sh(echo env.LS | grep "proceed" | awk -F"=" '{print $2}')
    		}
            
		steps {
                	echo "${env.LS}"
			echo env.proceed
			
			script {
				if ('proceed = True' in env.LS) {
            				sh "echo 'start connectivity tests'"
        			} else {
            				echo 'Failures. Terminating pipeline.'
					sh 'exit 0'
        			}
			}
		}
        }
	  
	
  }
}

