### A real case evaluation in the materials design domain

#### To set up the relational data sources

**Step 1**: To create the tables of the database.

	sourcec ./db/md_schema.sql 

**Step 2**: To populate the tables with data.

	sourcec ./db/md_data.sql 

**Note**: We assume that the account and password of the database are configured in the RML semantic mappings [file](../../mapping_parser/semantic_mappings/mdo-mappings-mysql-1K.ttl#L26-L27).


**Step 3**: After setting up the mysql databases, you can direct to the home folder of the project and running the following commands.


	python ./schema_generator/graphql_schema_gen.py ./schema_generator/mdo.ttl
	python ./mapping_parser/mapping_parser.py ./mapping_parser/semantic_mappings/mdo-mappings-mysql-1K.ttl

**Step 4**: Set up the GraphQL server.

[//]: # "export FLASK_ENV=development"

    python app.py ./schema_generator/mdo-schema.graphql ./schema_generator/mdo2graphql.json ./mapping_parser/mdo-mappings-mysql-1K.json 