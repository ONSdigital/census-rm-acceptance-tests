# census-rm-acceptance-tests

Python Behave BDD tests for RM Census.

### Run the tests
1. Clone [census-rm-docker-dev](https://github.com/ONSdigital/census-rm-kubernetes) and run `make up` to start the required services  
1. Run:
```bash 
make acceptance_sequential_tests

or

make acceptance_parallel_tests 
```