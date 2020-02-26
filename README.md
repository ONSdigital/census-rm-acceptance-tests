

# census-rm-acceptance-tests

[![Build Status](https://travis-ci.com/ONSdigital/census-rm-acceptance-tests.svg?branch=master)](https://travis-ci.com/ONSdigital/census-rm-acceptance-tests)


Python Behave BDD tests for RM Census.

## Run the tests locally against census-rm-docker-dev
1. Clone [census-rm-docker-dev](https://github.com/ONSdigital/census-rm-docker-dev) and run `make up` to start the required services
1. Set Pub/Sub emulator-related environment variables, this will force your docker-dev version to use the GCP pubsub Emulator
   
    ```bash
       export PUBSUB_EMULATOR_HOST=localhost:8538
    ```
    
    You can put this in your .bash_profile or in a gitignored .env file 

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
To run the acceptance tests against a different branch of the QID batch runner:
```bash
QID_BATCH_BRANCH=<branch> ./run_gke.sh
```

### Script Environment variables

| Name                  | Description                                                                                                                                                                                                  | Example                                  | Default              | Required |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|----------------------|----------|
| `ENV`                 | The environment to run the tests in and against, it will try to use an existing project of the form `census-rm-<ENV>`. If not present, the script will use the current k8s context.                                                                                                  | `ENV=test-env`                           | None                 | no      |
| `IMAGE`              | The path to the acceptance tests Docker image to use in the k8s pod (lazy option `ci` to use the default master image).                                                                                                                | `IMAGE="eu.gcr.io/census-rm-test-env/rm/census-rm-acceptance-tests:latest"`                    | `eu.gcr.io/census-rm-$ENV/rm/census-rm-acceptance-tests:latest`                 | no       |
| `BUILD`          | A boolean (`true` or not set string) to toggle the build and push of the acceptance tests as a Docker image.                                                                                                                  | `IMAGE=true`                        | None              | no       |
| `NAMESPACE`          | The k8s namespace to run the acceptance tests as a pod in.                                                                                                                  | `NAMESPACE=default`                        | None              | no       |


### Alternatively

Deploy the acceptance test pod using kubectl apply:
```bash
kubectl apply acceptance_tests_pod.yml
```
Then run the acceptance tests with the kubectl exec command:
```bash
kubectl exec -it acceptance-tests -- /bin/bash -c "sleep 2; behave acceptance_tests/features --tags=~@local-docker"
```
