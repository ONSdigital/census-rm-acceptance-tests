

# census-rm-acceptance-tests

[![Build Status](https://travis-ci.com/ONSdigital/census-rm-acceptance-tests.svg?branch=master)](https://travis-ci.com/ONSdigital/census-rm-acceptance-tests)


Python Behave BDD tests for RM Census.

## Run the tests locally against census-rm-docker-dev
1. Clone [census-rm-docker-dev](https://github.com/ONSdigital/census-rm-docker-dev) and run `make up` to start the required services
1. Set Pub/Sub emulator-related environment variables (you should only need to do this once in your .bash_profile)
   This will force your docker-dev version to use the Emulator
   
    ```bash
       export PUBSUB_EMULATOR_HOST=localhost:8538
    ```

1. Run:
    ```bash
    make test
    ```

## Run tests against a GCP project

Run the `run_gke.sh` bash script with the environment variables (defined in [the table below](#script-environment-variables)).

### Examples

NB: assumes infrastructure and services exist in respective projects.

To run the acceptance tests (`latest` image in GCR) in a pod in census-rm-ci:
```bash
./run_gke.sh
```
To run a locally-modified version of the acceptance tests in a pod in a dev GCP project (builds and pushes the docker image to the project's GCR):
```bash
BUILD=true ENV=test-env ./run_gke.sh
```
To run the acceptance tests using the `latest` image from the census-rm-ci GCR in a pod in a dev GCP project (otherwise defaults to the image in the project's GCR):
```bash
IMAGE=ci ENV=test-env ./run_gke.sh
```
Build and push a locally-modified version of the acceptance tests and then run in a pod in another dev GCP project:
```bash
BUILD=true IMAGE="eu.gcr.io/census-rm-at/rm/census-rm-acceptance-tests:latest" ENV=test-env ./run_gke.sh
```

### Script Environment variables

| Name                  | Description                                                                                                                                                                                                  | Example                                  | Default              | Required |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|----------------------|----------|
| `ENV`                 | The environment to run the tests in and against, it will try to use an existing project of the form `census-rm-<ENV>`. If not present, the script will use the current k8s context.                                                                                                  | `ENV=test-env`                           | None                 | no      |
| `IMAGE`              | The path to the acceptance tests Docker image to use in the k8s pod (lazy option `ci` to use the default master image).                                                                                                                | `IMAGE="eu.gcr.io/census-rm-test-env/rm/census-rm-acceptance-tests:latest"`                    | `eu.gcr.io/census-rm-$ENV/rm/census-rm-acceptance-tests:latest`                 | no       |
| `BUILD`          | A boolean (`true` or not set string) to toggle the build and push of the acceptance tests as a Docker image.                                                                                                                  | `IMAGE=true`                        | None              | no       |
| `NAMESPACE`          | The k8s namespace to run the acceptance tests as a pod in.                                                                                                                  | `NAMESPACE=default`                        | None              | no       |


### Alternatively

First make sure that your gcloud (cli) is pointing at the correct project e.g.:

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
--env=SFTP_USERNAME=$(kubectl get secret sftp-credentials -o=jsonpath="{.data.username}" | base64 --decode) \
--env=SFTP_PASSWORD=$(kubectl get secret sftp-credentials -o=jsonpath="{.data.password}" | base64 --decode) \
--env=REDIS_SERVICE_HOST=$(kubectl get configmap redis-config -o=jsonpath="{.data.redis-host}") \
--env=REDIS_SERVICE_PORT=$(kubectl get configmap redis-config -o=jsonpath="{.data.redis-port}") \
-- /bin/bash -c "sleep 2; behave acceptance_tests/features"
```

This will deploy the the image to a container in k8s and run it, streaming back the logs.
You should see the output of the tests in your terminal as if you were running them locally.


####  Testing a new branch of acceptance tests

If you are testing a new branch of the acceptance-tests themselves you will need to build an image yourself 
and push it to your gcr and then reference that.  
Go to the gcr container api enabler (https://console.cloud.google.com/flows/enableapi?apiid=containerregistry.googleapis.com)
Choose your project and enable it

Build the image locally and push it to gcr:
```
docker build -t eu.gcr.io/<project-name>/rm/census-rm-acceptance-tests:latest .
docker push eu.gcr.io/<project-name>/rm/census-rm-acceptance-tests:latest
```

Then you should be able to run the tests with a similar command to above:
```
kubectl run acceptance-tests -it --command --rm --quiet --generator=run-pod/v1 \
--image=eu.gcr.io/<project-name>/rm/census-rm-acceptance-tests:latest --restart=Never \
$(while read env; do echo --env=${env}; done < kubernetes.env) \
--env=SFTP_USERNAME=$(kubectl get secret sftp-credentials -o=jsonpath="{.data.username}" | base64 --decode) \
--env=SFTP_PASSWORD=$(kubectl get secret sftp-credentials -o=jsonpath="{.data.password}" | base64 --decode) \
--env=REDIS_SERVICE_HOST=$(kubectl get configmap redis-config -o=jsonpath="{.data.redis-host}") \
--env=REDIS_SERVICE_PORT=$(kubectl get configmap redis-config -o=jsonpath="{.data.redis-port}") \
-- /bin/bash -c "sleep 2; behave acceptance_tests/features"
```
