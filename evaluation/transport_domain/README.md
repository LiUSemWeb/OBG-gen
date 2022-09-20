### A synthetic evaluation in the transport domain based on GTFS-Madrid-Bench

#### To set up the relational data sources

**Step**: To create the tables of the database and populate the tables with data (for scale factor 1).

	source ./db/gtfs_schema_data.sql 


**Note**: We assume that the account and password of the database are configured in the RML semantic mappings [file](../../mapping_parser/semantic_mappings/gtfs-rdb.rml.ttl#L26-L27).


**Step 3**: After setting up the mysql databases, you can direct to the home folder of the project and running the following commands.


	python ./mapping_parser/mapping_parser.py ./mapping_parser/semantic_mappings/gtfs-rdb.rml.ttl

**Step 3**: Set up the GraphQL server.

[//]: # "export FLASK_ENV=development"

    python app.py ./schema_generator/gtfs.graphql ./schema_generator/gtfs2graphql.json ./mapping_parser/gtfs-rdb.json 
