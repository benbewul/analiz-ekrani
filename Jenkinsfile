pipeline {
    agent any

    environment {
        OCP_API  = 'https://api.rm1.0a51.p1.openshiftapps.com:6443'
        OCP_PROJ = 'benbewul-dev'
        APP_NAME = 'pcc-analiz-tool'
        GIT_URL  = 'https://github.com/benbewul/analiz-ekrani.git'
    }

    stages {

        stage('Checkout') {
            steps {
                git url: "${GIT_URL}", branch: 'main'
            }
        }

        stage('Deploy PCC tool') {
            steps {
                withCredentials([string(credentialsId: 'ocp-token', variable: 'TOKEN')]) {
                    sh '''
                    oc login ${OCP_API} --token=${TOKEN} --insecure-skip-tls-verify=true
                    oc project ${OCP_PROJ}

                    echo "Eski app siliniyor..."
                    oc delete all -l app=${APP_NAME} --ignore-not-found=true || true
                    oc delete bc/${APP_NAME} --ignore-not-found=true || true
                    oc delete is/${APP_NAME} --ignore-not-found=true || true

                    echo "Build oluşturuluyor..."
                    oc new-build --name=${APP_NAME} --binary --strategy=docker || true

                    echo "Build başlatılıyor..."
                    oc start-build ${APP_NAME} --from-dir=. --follow

                    echo "Deploy ediliyor..."
                    oc new-app ${APP_NAME}:latest --name=${APP_NAME}

                    echo "Route açılıyor..."
                    oc expose service/${APP_NAME} || true

                    oc get pods
                    oc get svc
                    oc get route
                    '''
                }
            }
        }
    }
}
