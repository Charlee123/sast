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
    DEBIAN_FRONTEND          = 'noninteractive'
    CODEQL_VERSION           = 'latest'
    // Persist CodeQL packs/cache in the Jenkins workspace so subsequent builds are faster
    // (workspace is volume-mounted into the Docker agent)
    CODEQL_USER_CACHE_DIR    = "${WORKSPACE}/.codeql-cache"
    CODEQL_NO_UPDATE_NOTIFIER= '1'
  }

  stages {

    stage('Bootstrap Environment') {
      steps {
        sh '''#!/usr/bin/env bash
set -euo pipefail
echo "[Bootstrap] Installing base dependencies..."
apt-get update -qq
apt-get install -y -qq curl jq ca-certificates git unzip \
  openjdk-17-jdk python3 python3-venv nodejs npm >/dev/null
echo "[Bootstrap] Done."
'''
      }
    }

    stage('Install CodeQL CLI') {
      steps {
        sh '''#!/usr/bin/env bash
set -euo pipefail
echo "[CodeQL] Downloading CLI..."
curl -sSL -o codeql.zip "https://github.com/github/codeql-cli-binaries/releases/${CODEQL_VERSION}/download/codeql-linux64.zip"
unzip -q -o codeql.zip -d /opt
ln -sf /opt/codeql/codeql codeql
./codeql --version
echo "[CodeQL] Cache dir: ${CODEQL_USER_CACHE_DIR}"
mkdir -p "${CODEQL_USER_CACHE_DIR}"
'''
      }
    }

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Detect Languages') {
      steps {
        script {
          // Skip common noise folders
          def findBase = "find . -type f -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/venv/*'"
          env.HAS_JAVA = sh(returnStdout: true, script: "${findBase} -name '*.java' | head -n 1 | wc -l").trim()
          env.HAS_JS   = sh(returnStdout: true, script: "${findBase} \\( -name '*.js' -o -name '*.ts' \\) | head -n 1 | wc -l").trim()
          env.HAS_PY   = sh(returnStdout: true, script: "${findBase} -name '*.py' | head -n 1 | wc -l").trim()
          echo "[Detect] Java: ${env.HAS_JAVA}, JavaScript/TypeScript: ${env.HAS_JS}, Python: ${env.HAS_PY}"
        }
      }
    }

    stage('Install Query Packs') {
      steps {
        sh '''#!/usr/bin/env bash
set -euo pipefail
echo "[CodeQL] Installing query packs (idempotent; uses cache if present)..."
# Install all three commonly used language packs; harmless if not used later
./codeql pack install codeql/java-queries codeql/javascript-queries codeql/python-queries
echo "[CodeQL] Query packs installed."
'''
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
./codeql database create java-db --language=java --source-root=. --overwrite
./codeql database analyze java-db codeql/java-queries \
  --format=sarifv2.1.0 --output=java-results.sarif
'''
          }
        }

        stage('JavaScript/TypeScript Analysis') {
          when { expression { env.HAS_JS == '1' } }
          steps {
            sh '''#!/usr/bin/env bash
set -euo pipefail
echo "[CodeQL] Analysing JavaScript/TypeScript code..."
./codeql database create js-db --language=javascript --source-root=. --overwrite
./codeql database analyze js-db codeql/javascript-queries \
  --format=sarifv2.1.0 --output=js-results.sarif
'''
          }
        }

        stage('Python Analysis') {
          when { expression { env.HAS_PY == '1' } }
          steps {
            sh '''#!/usr/bin/env bash
set -euo pipefail
echo "[CodeQL] Analysing Python code..."
# If your repo uses a venv, you can activate it before analysis; not required for pure static parse:
# python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt || true
./codeql database create python-db --language=python --source-root=. --overwrite
./codeql database analyze python-db codeql/python-queries \
  --format=sarifv2.1.0 --output=python-results.sarif
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
