## Getting Started

* [graphql_schema_gen.py](./graphql_schema_gen.py) takes an ontology as the input and then outputs a GraphQL schema; 
* [ontology.py](./ontology.py) is used to parse an OWL ontology;  

## Usage
**Pre-Step (c)**: Generate GraphQL schema from an ontology and output _**(*)-schema.graphql**_ and _**(*)2graphql.json**_ files in current folder.


	python ./graphql_schema_gen.py ./mdo.ttl
