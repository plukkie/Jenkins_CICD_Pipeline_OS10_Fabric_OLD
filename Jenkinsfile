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

	stage("Env Variables") {
            steps {
                script {
                    env.LS = sh(script:'python3 -u startcicd.py launchawx', returnStdout: true).trim()
                    echo "LS = ${env.LS}"
                    // or if you access env variable in the shell command
                    sh 'echo $LS'
                }
            }
        }
	  
	
  }
}

