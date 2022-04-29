### A synthetic evaluation in the university domain based on LinGBM

#### To set up the relational data sources

**Step 1**: To create the tables of the database.

	sourcec ./db/uni_schema.sql 

**Step 2**: To populate the tables with data.

	sourcec ./db/uni_data.sql 

**Note**: We assume that the account and password of the database are configured in the RML semantic mappings [file](../../mapping_parser/semantic_mappings/university-mapping-mysql-sf4.ttl#L26-L27).


**Step 3**: After setting up the mysql databases, you can direct to the home folder of the project and running the following commands.


	python ./mapping_parser/mapping_parser.py ./mapping_parser/semantic_mappings/university-mapping-mysql-sf4.ttl

**Step 3**: Set up the GraphQL server.

[//]: # "export FLASK_ENV=development"

    python app-uni.py ./schema_generator/university-schema.graphql ./schema_generator/mdo2graphql.json ./mapping_parser/university-mapping-mysql-sf4.json 