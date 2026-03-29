pipeline {
    agent any

    environment {
        OCP_API   = 'https://api.rm1.0a51.p1.openshiftapps.com:6443'
        OCP_PROJ  = 'benbewul-dev'
        APP_NAME  = 'pcc-gozcu-demo'
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
                oc delete all -l app=${APP_NAME} --ignore-not-found=true || true
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
                oc new-app ${APP_NAME}:${IMAGE_TAG} --name=${APP_NAME} || true
                oc expose service/${APP_NAME} || true
                oc set env deployment/${APP_NAME} PYTHONUNBUFFERED=1 || true
                oc rollout latest deployment/${APP_NAME} || true
                oc get pods
                oc get svc
                oc get route
                '''
            }
        }
    }
}
