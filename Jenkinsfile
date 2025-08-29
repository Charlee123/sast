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
apt-get install -y -qq curl jq ca-certificates git unzip openjdk-11-jdk nodejs npm &>/dev/null
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

  }
}
