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

kubectl run acceptance-tests -it --command --rm --quiet --generator=run-pod/v1 \
    --image=$IMAGE --restart=Never \
    $(while read env; do echo --env=${env}; done < kubernetes.env) \
    --env=SFTP_USERNAME=$(kubectl get secret sftp-credentials -o=jsonpath="{.data.username}" | base64 --decode) \
    --env=SFTP_PASSWORD=$(kubectl get secret sftp-credentials -o=jsonpath="{.data.password}" | base64 --decode) \
    --env=REDIS_SERVICE_HOST=$(kubectl get configmap redis-config -o=jsonpath="{.data.redis-host}") \
    --env=REDIS_SERVICE_PORT=$(kubectl get configmap redis-config -o=jsonpath="{.data.redis-port}") \
    -- /bin/bash -c "sleep 2; behave acceptance_tests/features"