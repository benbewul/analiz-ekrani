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
                oc new-app ${APP_NAME}:${IMAGE_TAG} --name=${APP_NAME} -l app=${APP_NAME}
                oc label deployment/${APP_NAME} app=${APP_NAME} --overwrite
                oc label svc/${APP_NAME} app=${APP_NAME} --overwrite
                oc set env deployment/${APP_NAME} PYTHONUNBUFFERED=1 PORT=8080
                # Varsayılan veya yanlış HTTP probe trafiği keser; 8080 TCP readiness yeterli
                oc set probe deployment/${APP_NAME} --remove --readiness --liveness 2>/dev/null || true
                oc set probe deployment/${APP_NAME} --readiness --get-url=http://:8080/ --initial-delay-seconds=5 --timeout-seconds=5 --period-seconds=10
                oc rollout status deployment/${APP_NAME} --timeout=300s
                oc delete route/${APP_NAME} --ignore-not-found=true
                # Önce pod hazır, sonra route (yoksa router boş backend görür)
                oc expose svc/${APP_NAME} --name=${APP_NAME} --port=8080
                oc patch route/${APP_NAME} -p '{"spec":{"tls":{"termination":"edge","insecureEdgeTerminationPolicy":"Allow"}}}'
                oc get pods -l app=${APP_NAME} -o wide
                oc get endpoints ${APP_NAME} -o wide
                oc get svc ${APP_NAME} -o wide
                oc get route ${APP_NAME} -o wide
                if ! oc get endpoints ${APP_NAME} -o jsonpath='{.subsets[0].addresses[0].ip}' 2>/dev/null | grep -q .; then
                  echo "HATA: Service endpoint yok — pod/selector/port kontrol et"
                  oc describe deployment/${APP_NAME}
                  oc logs deployment/${APP_NAME} --tail=80 || true
                  exit 1
                fi
                echo "Route URL: http://$(oc get route ${APP_NAME} -o jsonpath='{.spec.host}')/"
                '''
            }
        }
    }
}
