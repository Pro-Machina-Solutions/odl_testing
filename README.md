# odl_testing
A repository to track learning of the [ODL Live](https://odllive.com/) route optimiser to solve rich, continuous vehicle routing problems.

The aim is document how the client side code can be built up in stages to gradually expand the API utilisation as a means to learn and demonstrate [the documentation](https://www.odllive.com/section_common_planning_use_cases.html#section_common_planning_use_cases). Each fixed stage will be formalised as a release with a corresponding example that communicates with the API using the new features.

Note that this is a wrapper that assumes you have a subscription to the service in order to run the examples to completion. However, if you don't have a subscription and want to see what client code might look like in Python, I will ensure that each object is fully documented and that the examples explain the context around what is being tested/demonstrated.

## Installation
The code maintains compatibility with Python >= 3.13. The first step is just to clone the repository (it is not currently on PyPI). Note that this will download the `main` branch of the repo, which will be the most up-to-date code. If you want to see the evolation of the code through each of the examples, it's probably easier to view the releases online:
```
git clone https://github.com/Pro-Machina-Solutions/odl_testing.git
```
Since the repo will be installed locally, you will need to navigate to the top level directory that you just cloned and use:
```
pip install -e .
```
You can omit the `-e` flag if you don't intend to make any changes locally.

If you have a subscription and a local instance of the server running, this library expects a file called `.env` also in the top-level directory. The contents of this file must contain the following credentials:
```
USER_NAME = "XYZ123ABC"
USER_PASS = "myusername"
```

