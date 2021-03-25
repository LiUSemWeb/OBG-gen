# ODGSG: Ontology-Driven GraphQL Server Generation for Data Access and Integration
A framework for using GraphQL in which a global domain ontology drives the generation of a GraphQL server that answers requests by querying the integrated data sources. The core of this framework is an algorithm to generate a GraphQL scheam based on an ontology.

## The Framework of ODGSG
### GraphQL Server Generation
* (c): Ontology-based GraphQL schema generation
* (d): Semantic mappings-based GraphQL resolvers generation
![entities](https://huanyu-li.github.io/figures/odgsg/generic-framework.png "The framework of ODGSG")

## Getting Started

* [graphql_schema_gen.py](https://github.com/huanyu-li/ODGSG/blob/main/graphql_schema_gen.py) takes an ontology as the input and then outputs a GraphQL schema.
* [mapping_parser.py](https://github.com/huanyu-li/ODGSG/blob/main/mapping_parser.py) takes a RML mapping file (in turtle format) as the input and then outputs mappings and logical sources into a json file.
* [app.py](https://github.com/huanyu-li/ODGSG/blob/main/app.py) is used to set up the GraphQL server using [Ariadne](https://ariadnegraphql.org).
* [ontology.py](https://github.com/huanyu-li/ODGSG/blob/main/ontology.py) is used to parse an OWL ontology.
* [schema_utils.py](https://github.com/huanyu-li/ODGSG/blob/main/schema_utils.py), [mapping_utils.py](https://github.com/huanyu-li/ODGSG/blob/main/mapping_utils.py), [graphql_utils.py](https://github.com/huanyu-li/ODGSG/blob/main/graphql_utils.py) define helper functions used to generating GraphQL schema, extracting mappings' structures, and generating resolvers, respectively.

## Installation

GraphQL-core 3 can be installed from PyPI using the built-in pip command:

    python -m pip install "graphql-core>=3"

Alternatively, you can also use [pipenv](https://docs.pipenv.org/) for installation in a
virtual environment:

    pipenv install "graphql-core>=3"

## Usage

```python
iii
```

## A demo on Heroku of ODGSG for the materials design domain
[ODGSG-Demo](https://odgsg-demo.herokuapp.com)

## Contact

* [Huanyu Li](https://www.ida.liu.se/~huali50/)
