#!/bin/bash
set -e

if [ -z "$ENV" ]; then
    ENV=ci
fi

GCP_PROJECT=census-rm-$ENV
GCP_REGION=europe-west2

if [ -z "$IMAGE" ]; then
    IMAGE=eu.gcr.io/$GCP_PROJECT/rm/census-rm-acceptance-tests:latest
elif [ "$IMAGE" = "ci" ]; then
    IMAGE=eu.gcr.io/census-rm-ci/rm/census-rm-acceptance-tests:latest
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

echo "Using RM Acceptance Tests image [$IMAGE]"

if [ -z "$NAMESPACE" ]; then
    KUBERNETES_NAMESPACE=response-management-$ENV
else
    KUBERNETES_NAMESPACE=$NAMESPACE
fi

gcloud config set project $GCP_PROJECT
gcloud container clusters get-credentials rm-k8s-cluster \
    --region $GCP_REGION \
    --project $GCP_PROJECT

echo "Running RM Acceptance Tests in GKE [$GCP_PROJECT/rm-k8s-cluster/$KUBERNETES_NAMESPACE]..."

kubectl run acceptance-tests -it --command --rm --quiet --generator=run-pod/v1 \
    --image=$IMAGE --restart=Never \
    $(while read env; do echo --env=${env}; done < kubernetes.env) \
    --env=SFTP_USERNAME=$(kubectl get secret sftp-credentials -o=jsonpath="{.data.username}" --namespace=${KUBERNETES_NAMESPACE} | base64 --decode) \
    --env=SFTP_PASSWORD=$(kubectl get secret sftp-credentials -o=jsonpath="{.data.password}" --namespace=${KUBERNETES_NAMESPACE} | base64 --decode) \
    --env=REDIS_SERVICE_HOST=$(kubectl get configmap redis-config -o=jsonpath="{.data.redis-host}" --namespace=${KUBERNETES_NAMESPACE}) \
    --env=REDIS_SERVICE_PORT=$(kubectl get configmap redis-config -o=jsonpath="{.data.redis-port}" --namespace=${KUBERNETES_NAMESPACE}) \
    --namespace=$KUBERNETES_NAMESPACE \
    -- /bin/bash -c "sleep 2; behave acceptance_tests/features"
