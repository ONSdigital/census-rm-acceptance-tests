#!/bin/bash
set -e

if [ -z "$ENV" ]; then
    echo "No ENV set. Using kubectl current context."

else
    GCP_PROJECT=census-rm-$ENV
    gcloud config set project $GCP_PROJECT
    gcloud container clusters get-credentials rm-k8s-cluster \
        --region europe-west2 \
        --project $GCP_PROJECT
fi

BEHAVE_TAGS='--tags=~@local-docker'
if [ "$SMOKE" = "true" ]; then
    echo "Running only the tagged smoke tests"
    BEHAVE_TAGS+=' --tags=@smoke'
fi

if [ "$NAMESPACE" ]; then
    kubectl config set-context $(kubectl config current-context) --namespace=$NAMESPACE
    echo "NAMESPACE = [$NAMESPACE] Set kubectl namespace for subsequent commands [$NAMESPACE]."
fi
echo "Running RM Acceptance Tests [$(kubectl config current-context)]..."

kubectl delete pod acceptance-tests --wait || true

kubectl apply -f acceptance_tests_pod.yml

kubectl wait --for=condition=Ready pod/acceptance-tests --timeout=200s

kubectl exec -it acceptance-tests -- /bin/bash -c "sleep 2; behave acceptance_tests/features $BEHAVE_TAGS"

kubectl delete pod acceptance-tests || true

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
    -- /bin/bash /home/qidbatchrunner/run_acceptance_tests.sh
kubectl delete deploy qid-batch-runner --force --now
