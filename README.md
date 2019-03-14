# census-rm-acceptance-tests

Python Behave BDD tests for RM Census.

### Run the tests locally against census-rm-docker-dev
1. Clone [census-rm-docker-dev](https://github.com/ONSdigital/census-rm-kubernetes) and run `make up` to start the required services  
1. Run:
```bash 
make test
```

### Run tests against a GCP project

1st make sure that your gcloud is pointing at the correct project e.g.

```
gcloud config set project <project_name>
```

Then run the below kubectl command will run the latest master image of acceptance tests from census-rm-ci.
Your projects service account will need to be added to https://console.cloud.google.com/iam-admin/iam?organizationId=884444642818&project=census-rm-ci
in order to have permission to pull the image.

```
kubectl run acceptance-tests -it --command --rm --quiet --generator=run-pod/v1 \
--image=eu.gcr.io/census-rm-ci/rm/census-rm-acceptance-tests:latest --restart=Never \
$(while read env; do echo --env=${env}; done < kubernetes.env) \
--env=SFTP_USERNAME=$(kubectl get secret sftp-credentials -o=jsonpath="{.data.username}" --namespace=${KUBERNETES_NAMESPACE} | base64 --decode) \
--env=SFTP_PASSWORD=$(kubectl get secret sftp-credentials -o=jsonpath="{.data.password}" --namespace=${KUBERNETES_NAMESPACE} | base64 --decode) \
-- /bin/bash -c "sleep 2; behave acceptance_tests/features"
```

This will deploy the the image to a container in k8s and run it, streaming back the logs.
You should see the output of the tests in your terminal as if you were running them locally.


###  Testing a new branch of acceptance tests
If you are testing a new branch of the acceptance-tests themselves you will need to build an image yourself 
and push it to your gcr and then reference that.  
Go to the gcr container api enabler https://console.cloud.google.com/flows/enableapi?apiid=containerregistry.googleapis.com
Choose your project and enable it

Build the image locally and push it to gcr

```
docker build -t eu.gcr.io/<project-name>/rm/census-rm-acceptance-tests:latest .
docker push eu.gcr.io/<project-name>/rm/census-rm-acceptance-tests:latest
```

Then you should be able to run the tests with a similar command to above
```
kubectl run acceptance-tests -it --command --rm --quiet --generator=run-pod/v1 \
--image=eu.gcr.io/<project-name>/rm/census-rm-acceptance-tests:latest --restart=Never \
$(while read env; do echo --env=${env}; done < kubernetes.env) \
--env=SFTP_USERNAME=$(kubectl get secret sftp-credentials -o=jsonpath="{.data.username}" --namespace=${KUBERNETES_NAMESPACE} | base64 --decode) \
--env=SFTP_PASSWORD=$(kubectl get secret sftp-credentials -o=jsonpath="{.data.password}" --namespace=${KUBERNETES_NAMESPACE} | base64 --decode) \
-- /bin/bash -c "sleep 2; behave acceptance_tests/features"
```




