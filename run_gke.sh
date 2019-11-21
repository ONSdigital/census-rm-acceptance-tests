#!/bin/bash
set -e

if [ -z "$ENV" ]; then
    echo "No ENV set. Using kubectl current context."
    if [ -z "$IMAGE" ] || [ "$IMAGE" = "ci" ]; then
        IMAGE=eu.gcr.io/census-rm-ci/rm/census-rm-acceptance-tests:latest
    fi
else
    GCP_PROJECT=census-rm-$ENV
    if [ -z "$IMAGE" ]; then
        IMAGE=eu.gcr.io/$GCP_PROJECT/rm/census-rm-acceptance-tests:latest
    elif [ "$IMAGE" = "ci" ]; then
        IMAGE=eu.gcr.io/census-rm-ci/rm/census-rm-acceptance-tests:latest
    fi

    gcloud config set project $GCP_PROJECT
    gcloud container clusters get-credentials rm-k8s-cluster \
        --region europe-west2 \
        --project $GCP_PROJECT
fi

if [ "$BUILD" = "true" ]; then
    echo "Building and pushing Docker image [$IMAGE]..."
    read -p "Are you sure (y/N)? " -n 1 -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker build -t $IMAGE .
        docker push $IMAGE
    else
        exit 1
    fi
fi

echo "Using RM Acceptance Tests image [$IMAGE]."
if [ "$NAMESPACE" ]; then
    kubectl config set-context $(kubectl config current-context) --namespace=$NAMESPACE
    echo "Set kubectl namespace for subsequent commands [$NAMESPACE]."
fi
echo "Running RM Acceptance Tests [`kubectl config current-context`]..."

SFTP_TARGET_DIRECTORY=$(kubectl get configmap project-config -o=jsonpath="{.data.sftp-target-directory}")

kubectl run acceptance-tests -it --command --rm --quiet --generator=run-pod/v1 \
    --image=$IMAGE --restart=Never \
    $(while read env; do echo --env=${env}; done < kubernetes.env) \
    --env=SFTP_HOST=$(kubectl get secret sftp-ssh-credentials -o=jsonpath="{.data.host}" | base64 --decode) \
    --env=SFTP_USERNAME=$(kubectl get secret sftp-ssh-credentials -o=jsonpath="{.data.username}" | base64 --decode) \
    --env=SFTP_KEY=$(kubectl get secret sftp-ssh-credentials -o=jsonpath="{.data.private-key}") \
    --env=SFTP_PASSPHRASE=$(kubectl get secret sftp-ssh-credentials -o=jsonpath="{.data.passphrase}" | base64 --decode) \
    --env=SFTP_PPO_DIRECTORY=$(kubectl get configmap project-config -o=jsonpath="{.data.sftp-ppo-supplier-directory}") \
    --env=SFTP_QM_DIRECTORY=$(kubectl get configmap project-config -o=jsonpath="{.data.sftp-qm-supplier-directory}") \
    --env=REDIS_SERVICE_HOST=$(kubectl get configmap redis-config -o=jsonpath="{.data.redis-host}") \
    --env=REDIS_SERVICE_PORT=$(kubectl get configmap redis-config -o=jsonpath="{.data.redis-port}") \
    --env=RECEIPT_TOPIC_PROJECT=$(kubectl get configmap pubsub-config -o=jsonpath="{.data.receipt-topic-project-id}") \
    --env=RECEIPT_TOPIC_ID=$(kubectl get configmap pubsub-config -o=jsonpath="{.data.receipt-topic-name}") \
    --env=OFFLINE_RECEIPT_TOPIC_PROJECT=$(kubectl get configmap project-config -o=jsonpath="{.data.project-name}") \
    --env=OFFLINE_RECEIPT_TOPIC_ID=offline-receipt-topic \
    --env=PPO_UNDELIVERED_PROJECT_ID=$(kubectl get configmap project-config -o=jsonpath="{.data.project-name}") \
    --env=PPO_UNDELIVERED_TOPIC_NAME=ppo-undelivered-topic \
    --env=QM_UNDELIVERED_PROJECT_ID=$(kubectl get configmap project-config -o=jsonpath="{.data.project-name}") \
    --env=QM_UNDELIVERED_TOPIC_NAME=qm-undelivered-topic \
    --env=GOOGLE_SERVICE_ACCOUNT_JSON=$(kubectl get secret pubsub-credentials -o=jsonpath="{.data['service-account-key\.json']}") \
    --env=GOOGLE_APPLICATION_CREDENTIALS="/app/service-account-key.json" \
    --env=RABBITMQ_USER=$(kubectl get secret rabbitmq -o=jsonpath="{.data.rabbitmq-username}" | base64 --decode) \
    --env=RABBITMQ_PASSWORD=$(kubectl get secret rabbitmq -o=jsonpath="{.data.rabbitmq-password}" | base64 --decode) \
    --env=RABBITMQ_HTTP_PORT=15672 \
    --env=NOTIFY_STUB_HOST=notify-stub \
    --env=NOTIFY_STUB_PORT=80 \
    --env=EXCEPTIONMANAGER_CONNECTION_HOST=exception-manager \
    --env=EXCEPTIONMANAGER_CONNECTION_PORT=80 \
    -- /bin/bash -c "sleep 2; behave acceptance_tests/features --tags=~@local-docker"

if [ -z "$QID_BATCH_BRANCH" ]; then
    QID_BATCH_BRANCH=master
fi


# Run acceptance tests for unaddressed batch
# Pre-delete to avoid unintentionally running with an old image
BATCH_RUNNER_CONFIG=https://raw.githubusercontent.com/ONSdigital/census-rm-qid-batch-runner/$QID_BATCH_BRANCH/qid-batch-runner.yml
kubectl delete deploy qid-batch-runner --force --now || true
kubectl apply -f ${BATCH_RUNNER_CONFIG}
kubectl rollout status deploy qid-batch-runner --watch=true
kubectl exec -it $(kubectl get pods -o name | grep -m1 qid-batch-runner | cut -d'/' -f 2) \
-- /bin/bash /app/run_acceptance_tests.sh
kubectl delete deploy qid-batch-runner --force --now