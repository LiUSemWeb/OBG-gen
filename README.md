# ODGSG: Ontology-Driven GraphQL Server Generation for Data Access and Integration
A framework for using GraphQL in which a global domain ontology drives the generation of a GraphQL server that answers requests by querying the integrated data sources. The core of this framework is an algorithm to generate a GraphQL scheam based on an ontology.

#### The framework of ODGSG
![entities](https://huanyu-li.github.io/figures/odgsg/generic-framework.png "The framework of ODGSG")

#### Getting started

* [graphql_schema_gen.py](https://github.com/huanyu-li/ODGSG/blob/main/graphql_schema_gen.py) is used to
* [mapping_parser.py](https://github.com/huanyu-li/ODGSG/blob/main/mapping_parser.py) is used to ...
* [app.py](https://github.com/huanyu-li/ODGSG/blob/main/app.py) is used to ...
* [ontology.py](https://github.com/huanyu-li/ODGSG/blob/main/ontology.py) is used to ...
* [schema_utils.py](https://github.com/huanyu-li/ODGSG/blob/main/schema_utils.py), [mapping_utils.py](https://github.com/huanyu-li/ODGSG/blob/main/mapping_utils.py), [graphql_utils.py](https://github.com/huanyu-li/ODGSG/blob/main/graphql_utils.py) are used to ...

#### Installation

GraphQL-core 3 can be installed from PyPI using the built-in pip command:

    python -m pip install "graphql-core>=3"

Alternatively, you can also use [pipenv](https://docs.pipenv.org/) for installation in a
virtual environment:

    pipenv install "graphql-core>=3"

#### Usage

```python
iii
```

#### A demo on Heroku of ODGSG for the materials design domain
[ODGSG-Demo](https://odgsg-demo.herokuapp.com)

#### Contact

* [Huanyu Li](https://www.ida.liu.se/~huali50/)
