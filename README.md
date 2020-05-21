

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
   
### Regression Tests
A subset of the tests are tagged with `@regression` to prevent them running in order to speed up testing.
Run the full set of tests with

```shell script
make regression_test
````

### Smoke tests
A subset of the tests have been tagged with `@smoke` to quickly test most domains of RM.

Run them locally with 
```shell script
make smoke_test
```

## Run tests against a GCP project

Run the `run_gke.sh` bash script with the environment variables (defined in [the table below](#script-environment-variables)).

NB: assumes infrastructure and services exist in respective projects.

To run the acceptance tests (`latest` image in GCR) in a pod in census-rm-ci:
```bash
./run_gke.sh
```
To run a locally-modified version of the acceptance tests in a pod you will have to build and tag the image, push it to the GCR and change the image in [acceptance_tests_pod.yml](./acceptance_tests_pod.yml) to point to your modified image
```shell script
IMAGE_TAG=<YOUR_TAG>
make build
docker tag eu.gcr.io/census-rm-ci/rm/census-rm-acceptance-tests:latest eu.gcr.io/census-rm-ci/rm/census-rm-acceptance-tests:$IMAGE_TAG
docker push eu.gcr.io/census-rm-ci/rm/census-rm-acceptance-tests:$IMAGE_TAG
```

Then run the tests with the run GKE script

### Smoke tests
Run only the tagged smoke tests in a GCP environment with
```bash
ENV=your-test-env SMOKE=true ./run_gke.sh
```

### Regression tests
A subset of the print file tests have been marked as `@regression` to prevent them to speed up the test run.
To include them in a test run against a GCP environment use
```bash
ENV=your-test-env REGRESSION=true ./run_gke.sh
```

### Script Environment variables

| Name                  | Description                                                                                                                                                                                                  | Example                                  | Default              | Required |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|----------------------|----------|
| `ENV`                 | The environment to run the tests in and against, it will try to use an existing project of the form `census-rm-<ENV>`. If not present, the script will use the current k8s context.                                                                                                  | `ENV=test-env`                           | None                 | no      |
| `NAMESPACE`          | The k8s namespace to run the acceptance tests as a pod in.                |                                                                                                  | `NAMESPACE=default`                        | None              | no       |
| `SMOKE`              | A boolean, set to `true` to only run the tagged smoke tests | `SMOKE=true` | `false` | no |
| `REGRESSION`         | A boolean, set to `true` to enable the regression tests     | `REGRESSION=true` | 'false` | no | 

### Alternatively

Deploy the acceptance test pod using kubectl apply:
```bash
kubectl apply acceptance_tests_pod.yml
```
Then run the acceptance tests with the kubectl exec command:
```bash
kubectl exec -it acceptance-tests -- /bin/bash -c "sleep 2; behave acceptance_tests/features --tags=~@local-docker"
```
