pipeline {
  agent {
    docker {
      image 'ubuntu:24.04'
      args '-u root'
    }
  }

  options {
    timestamps()
    ansiColor('xterm')
    disableConcurrentBuilds()
  }

  environment {
    DEBIAN_FRONTEND = 'noninteractive'
    CODEQL_VERSION  = 'latest'
  }

  stages {

    stage('Bootstrap Environment') {
      steps {
        sh '''#!/usr/bin/env bash
set -euo pipefail
echo "[Bootstrap] Installing dependencies..."
apt-get update -qq
apt-get install -y -qq curl jq ca-certificates git unzip openjdk-11-jdk nodejs npm python3 &>/dev/null
echo "[Bootstrap] Environment ready"
'''
      }
    }

    stage('Install CodeQL CLI') {
      steps {
        sh '''#!/usr/bin/env bash
set -euo pipefail
echo "[CodeQL] Downloading CLI..."
curl -sSL -o codeql.zip "https://github.com/github/codeql-cli-binaries/releases/${CODEQL_VERSION}/download/codeql-linux64.zip"
unzip -q codeql.zip -d /opt
ln -sf /opt/codeql/codeql codeql
./codeql --version
'''
      }
    }

    stage('Detect Languages') {
      steps {
        script {
          env.HAS_JAVA = sh(script: "find . -name '*.java' | head -n 1 | wc -l", returnStdout: true).trim()
          env.HAS_JS   = sh(script: "find . -name '*.js' | head -n 1 | wc -l", returnStdout: true).trim()
          env.HAS_PY   = sh(script: "find . -name '*.py' | head -n 1 | wc -l", returnStdout: true).trim()
          echo "[Detect] Java: ${env.HAS_JAVA}, JavaScript: ${env.HAS_JS}, Python: ${env.HAS_PY}"
        }
      }
    }

    stage('CodeQL Analysis') {
      parallel {
        stage('Java Analysis') {
          when { expression { env.HAS_JAVA == '1' } }
          steps {
            sh '''#!/usr/bin/env bash
set -euo pipefail
echo "[CodeQL] Analysing Java code..."
./codeql database create python-db --language=python --source-root=. --overwrite
./codeql database analyze python-db codeql/python-queries --format=sarifv2.1.0 --output=python-results.sarif
'''
          }
        }
        stage('JavaScript Analysis') {
          when { expression { env.HAS_JS == '1' } }
          steps {
            sh '''#!/usr/bin/env bash
set -euo pipefail
echo "[CodeQL] Analysing JavaScript code..."
./codeql database create js-db --language=javascript --source-root=.
./codeql database analyze js-db codeql/javascript-queries --format=sarifv2.1.0 --output=js-results.sarif
'''
          }
        }
        stage('Python Analysis') {
          when { expression { env.HAS_PY == '1' } }
          steps {
            sh '''#!/usr/bin/env bash
set -euo pipefail
echo "[CodeQL] Analysing Python code..."
./codeql database create python-db --language=python --source-root=.
./codeql database analyze python-db codeql/python-queries --format=sarifv2.1.0 --output=python-results.sarif
'''
          }
        }
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: '*-results.sarif', fingerprint: true
    }
  }
}

