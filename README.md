# census-rm-acceptance-tests

Python Behave BDD tests for RM.

### Deploy the Behave tests to Kubernetes

> kubectl run acceptance-tests --image rjweeks/census-rm-acceptance-tests --namespace=response-management-dev -it --rm /bin/bash

### Run the tests

> cd acceptance_tests
> behave

### Build the Docker image

> docker build -t rjweeks/census-rm-acceptance-tests .

### Push the Docker image

> docker push rjweeks/census-rm-acceptance-tests

