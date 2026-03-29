pipeline {
    agent any

    environment {
        OCP_API   = 'https://api.rm1.0a51.p1.openshiftapps.com:6443'
        OCP_PROJ  = 'benbewul-dev'
        APP_NAME  = 'pcc-analiz-tool'
        IMAGE_TAG = 'latest'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('OCP Login') {
            steps {
                withCredentials([string(credentialsId: 'ocp-token', variable: 'TOKEN')]) {
                    sh '''
                    oc login ${OCP_API} --token=${TOKEN} --insecure-skip-tls-verify=true
                    oc project ${OCP_PROJ}
                    '''
                }
            }
        }

        stage('Cleanup Old Resources') {
            steps {
                sh '''
                oc delete route/${APP_NAME} --ignore-not-found=true || true
                oc delete all -l app=${APP_NAME} --ignore-not-found=true || true
                oc delete svc/${APP_NAME} deployment/${APP_NAME} --ignore-not-found=true || true
                oc delete buildconfig/${APP_NAME} --ignore-not-found=true || true
                oc delete imagestream/${APP_NAME} --ignore-not-found=true || true
                '''
            }
        }

        stage('Build Image') {
            steps {
                sh '''
                oc new-build --name=${APP_NAME} --binary --strategy=docker --to=${APP_NAME}:${IMAGE_TAG} || true
                oc start-build ${APP_NAME} --from-dir=. --follow
                '''
            }
        }

        stage('Deploy App') {
            steps {
                sh '''
                set -e
                oc project ${OCP_PROJ}
                REG=$(oc get imagestream ${APP_NAME} -o jsonpath='{.status.dockerImageRepository}')
                if [ -z "$REG" ]; then
                  echo "HATA: ImageStream yok veya dockerImageRepository boş — build adımı başarılı mı?"
                  exit 1
                fi
                IMG="${REG}:${IMAGE_TAG}"
                sed -e "s|__APP_NAME__|${APP_NAME}|g" -e "s|__IMAGE__|${IMG}|g" openshift/application.yaml | oc apply -f -
                oc rollout status deployment/${APP_NAME} --timeout=300s
                oc get pods -l app=${APP_NAME} -o wide
                oc get endpoints ${APP_NAME} -o wide
                oc get svc ${APP_NAME} -o wide
                oc get route ${APP_NAME} -o wide
                if ! oc get endpoints ${APP_NAME} -o jsonpath='{.subsets[0].addresses[0].ip}' 2>/dev/null | grep -q .; then
                  echo "HATA: Service endpoint yok"
                  oc describe deployment/${APP_NAME}
                  oc logs deployment/${APP_NAME} --tail=80 || true
                  exit 1
                fi
                HOST=$(oc get route ${APP_NAME} -o jsonpath='{.spec.host}')
                echo "Route URL: https://${HOST}/"
                echo "HTTP: http://${HOST}/"
                '''
            }
        }
    }
}
