# ODGSG: Ontology-Driven GraphQL Server Generation for Data Access and Integration
A framework for using GraphQL in which a global domain ontology drives the generation of a GraphQL server that answers requests by querying the integrated data sources. The core of this framework is an algorithm to generate a GraphQL scheam based on an ontology.

## The Framework of ODGSG
### GraphQL Server Generation
![entities](https://huanyu-li.github.io/figures/odgsg/generic-framework.png "The framework of ODGSG")

* (c): Ontology-based GraphQL schema generation
* (d): Semantic mappings-based GraphQL resolvers generation


## Getting Started

* [/schema_generator/graphql_schema_gen.py](https://github.com/huanyu-li/ODGSG/blob/main/schema_generator/graphql_schema_gen.py) takes an ontology as the input and then outputs a GraphQL schema; 
* [/mapping_parser/mapping_parser.py](https://github.com/huanyu-li/ODGSG/blob/main/mapping_parser/mapping_parser.py) takes a RML mapping file (in turtle format) as the input and then outputs mappings and logical sources into a json file;
* [app.py](https://github.com/huanyu-li/ODGSG/blob/main/app.py) is used to set up the GraphQL server using [Ariadne](https://ariadnegraphql.org).


## Installation

* Following packages are needed:

[//]: # "python -m pip install \"graphql-core>=3\""
[//]: # "GraphQL-core 3 can be installed from PyPI using the built-in pip command:"
	
	pip install PyYAML
	pip install rdflib
    pip install graphql-core 
    pip install ariadne
    pip install Flask
    pip install pymongo
    

* Successfully installed messages:



    --------------------------
    Successfully installed PyYAML-5.4.1
    Successfully installed isodate-0.6.0 rdflib-5.0.0
    Successfully installed graphql-core-3.1.5
    Successfully installed ariadne-0.13.0 starlette-0.14.2 typing-extensions-3.10.0.0
    Successfully installed Flask-2.0.1 Jinja2-3.0.1 MarkupSafe-2.0.1 Werkzeug-2.0.1 click-8.0.1 itsdangerous-2.0.1
    Successfully installed pymongo-3.11.4

## Usage

 Generate GraphQL schema from an ontology and output a schema.graphql file in current folder:


	python ./schema_generator/graphql_schema_gen.py ./schema_generator/domain_ontologies/mdofull.ttl

Parse a RML mapping file and output a mappings.json file in current folder:

	python ./mapping_parser/mapping_parser.py ./mapping_parser/semantic_mappings/1K-mapping.ttl

Run GraphQL server:

	export FLASK_ENV=development
	python app.py ./schema.graphql ./mappings-temp.json

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
