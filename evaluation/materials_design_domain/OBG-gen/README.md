### Running OBG-gen 

**Pre-step**: We have already provided the schema based on MDO and the parsed semantic mappings, so you do not have to run schema generator and mapping parser.

	#python ./schema_generator/graphql_schema_gen.py ./schema_generator/mdo.ttl
	#python ./mapping_parser/mapping_parser.py ./mapping_parser/semantic_mappings/mdo-mappings-mysql-1K.ttl

**Step 1**: Set up the GraphQL server.

[//]: # "export FLASK_ENV=development"

    python app.py ./schema_generator/mdo-schema.graphql ./schema_generator/mdo2graphql.json ./mapping_parser/mdo-mappings-mysql-1K.json 

Simply change the mapping files, then you can either run OBG-gen-rdb or OBG-mix over different sizes datasets.'

* Mappings for OBG-gen-rdb
	* [mdo-mappings-mysql-1K.json](../../../mapping_parser/mdo-mappings-mysql-1K.json)
	* [mdo-mappings-mysql-2K.json](../../../mapping_parser/mdo-mappings-mysql-2K.json)
	* [mdo-mappings-mysql-4K.json](../../../mapping_parser/mdo-mappings-mysql-4K.json)
	* [mdo-mappings-mysql-8K.json](../../../mapping_parser/mdo-mappings-mysql-8K.json)
	* [mdo-mappings-mysql-16K.json](../../../mapping_parser/mdo-mappings-mysql-16K.json)
	* [mdo-mappings-mysql-32K.json](../../../mapping_parser/mdo-mappings-mysql-32K.json)
	

* Mappings for OBG-gen-mix
	* [mdo-mappings-mix-1K.json](../../../mapping_parser/mdo-mappings-mix-1K.json)
	* [mdo-mappings-mix-2K.json](../../../mapping_parser/mdo-mappings-mix-2K.json)
	* [mdo-mappings-mix-4K.json](../../../mapping_parser/mdo-mappings-mix-4K.json)
	* [mdo-mappings-mix-8K.json](../../../mapping_parser/mdo-mappings-mix-8K.json)
	* [mdo-mappings-mix-16K.json](../../../mapping_parser/mdo-mappings-mix-16K.json)
	* [mdo-mappings-mix-32K.json](../../../mapping_parser/mdo-mappings-mix-32K.json)