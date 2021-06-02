# ODGSG: Ontology-Driven GraphQL Server Generation for Data Access and Integration
A framework for using GraphQL in which a global domain ontology drives the generation of a GraphQL server that answers requests by querying the integrated data sources. The core of this framework is an algorithm to generate a GraphQL scheam based on an ontology.

## The Framework of ODGSG
### GraphQL Server Generation
![entities](https://huanyu-li.github.io/figures/odgsg/generic-framework.png "The framework of ODGSG")

* (c): Ontology-based GraphQL schema generation
* (d): Semantic mappings-based GraphQL resolvers generation


## Getting Started

* [/schema_generator/graphql_schema_gen.py](https://github.com/huanyu-li/ODGSG/blob/main/schema_generator/graphql_schema_gen.py) takes an ontology as the input and then outputs a GraphQL schema; 
   
  [/schema_generator/ontology.py](https://github.com/huanyu-li/ODGSG/blob/main/schema_generator/ontology.py) is used to parse an OWL ontology; 
  
  [/schema_generator/schema_utils.py](https://github.com/huanyu-li/ODGSG/blob/main/schema_generator/schema_utils.py) defines helper functions used to generate the GraphQL schema.
* [/mapping_parser/mapping_parser.py](https://github.com/huanyu-li/ODGSG/blob/main/mapping_parser/mapping_parser.py) takes a RML mapping file (in turtle format) as the input and then outputs mappings and logical sources into a json file;

  
* [app.py](https://github.com/huanyu-li/ODGSG/blob/main/app.py) is used to set up the GraphQL server using [Ariadne](https://ariadnegraphql.org);

  [/generic_resolver/odgsg_graphql_utils.py](https://github.com/huanyu-li/ODGSG/blob/main/generic_resolver/odgsg_graphql_utils.py) defines helper functions used to generating the generic resolver function;
    
  [/generic_resolver/mapping_utils.py](https://github.com/huanyu-li/ODGSG/blob/main/generic_resolver/mapping_utils.py) defines the helper functions used to read parsed RML mappings;
  
  [/generic_resolver/filter_utils.py](https://github.com/huanyu-li/ODGSG/blob/main/generic_resolver/filter_utils.py) defines the helper functions used parse filtering conditions;
  
  [/generic_resolver/filter_ast.py](https://github.com/huanyu-li/ODGSG/blob/main/generic_resolver/filter_ast.py) is used to define the abstract syntax tree to represent filtering conditions entailed with a GraphQL query.
  


## Installation

* TO UPDATE

GraphQL-core 3 can be installed from PyPI using the built-in pip command:
	
	pip install rdflib
    python -m pip install "graphql-core>=3"

    pip install ariadne

## Usage

* TO UPDATE

Generate GraphQL schema from an ontology and output a schema.graphql file in current folder:

	python ./schema_generator/graphql_schema_gen.py ./schema_generator/domain_ontologies/mdofull.ttl

Parse a RML mapping file and output a mappings.json file in current folder:

	python mapping_parser.py ./semantic_mappings/rml_mapping.ttl

Run GraphQL server:

	export FLASK_ENV=development
	python app.py ./schema.graphql ./mappings.json

	* Serving Flask app "app" (lazy loading)
	* Environment: development
	* Debug mode: on
	* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
	* Restarting with stat
	* Debugger is active!
	* Debugger PIN: 540-041-748

Then the GraphQL server can be accessed via http://127.0.0.1:5000/graphql.

## A demo on Heroku of ODGSG for the materials design domain
* TO UPDATE
[ODGSG-Demo](https://odgsg-demo.herokuapp.com)
