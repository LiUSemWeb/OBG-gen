import sys
import datetime
from ariadne import QueryType, make_executable_schema, graphql_sync, load_schema_from_path, InterfaceType, ObjectType
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify
from generic_resolver.odgsg_graphql_utils import Resolver_Utils

global ru
global type_defs
global query


thing = InterfaceType("Thing")


@thing.type_resolver
def resolve_search_result_type(obj, *_):
    # print(obj)
    if 'calculation' in obj['iri']:
        return 'Calculation'
    if 'structure' in obj['iri']:
        return 'Structure'



# Define types using Schema Definition Language (https://graphql.org/learn/schema/)
# Wrapping string in gql function provides validation and better error traceback
# Resolvers are simple python functions


def resolver(_, info, **kwargs):
    result = ru.generic_resolver_func(info, kwargs)
    return result


# Create an ASGI app using the schema, running in debug mode
# app = GraphQL(schema, debug=True)
app = Flask("__name__")


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    # On GET request serve GraphQL Playground
    # You don't need to provide Playground if you don't want to
    # but keep on mind this will not prohibit clients from
    # exploring your API using desktop GraphQL Playground app.
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    # GraphQL queries are always sent as POST
    data = request.get_json()
    # Note: Passing the request to the context is optional.
    # In Flask, the current request is always accessible as flask.request
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code


moesif_settings = {
    'APPLICATION_ID': 'eyJhcHAiOiIxOTg6MTM2NyIsInZlciI6IjIuMCIsIm9yZyI6Ijg4OjE4NjgiLCJpYXQiOjE2MTcyMzUyMDB9.-5RPUC5FFb4QTUCWSoII35La-cQWp7VYZ-y27ewVh4Q',
    'CAPTURE_OUTGOING_REQUESTS': False,  # Set to True to also capture outgoing calls to 3rd parties.
}


def register_object_type_queries(query_entries):
    for query_entry in query_entries:
        query.set_field(query_entry, resolver)


def register_interface_type_queries(query_entries):
    for query_entry in query_entries:
        query.set_field(query_entry, resolver)


# main function
if __name__ == "__main__":
    # app.wsgi_app = MoesifMiddleware(app.wsgi_app, moesif_settings)
    start_time = datetime.datetime.now()
    query = QueryType()
    schema_file = (str(sys.argv[1]))
    mapping_file = (str(sys.argv[2]))
    o2g_file = (str(sys.argv[3]))
    type_defs = load_schema_from_path(schema_file)
    ru = Resolver_Utils(mapping_file, o2g_file)
    end_time = datetime.datetime.now()
    print('Prepare time', end_time - start_time)
    object_type_query_entries, interface_type_query_entries = ru.get_query_entries(type_defs)
    register_object_type_queries(object_type_query_entries)
    register_interface_type_queries(interface_type_query_entries)
    schema = make_executable_schema(type_defs, [query, thing])
    # schema = make_executable_schema(type_defs, [query])
    app.run(debug=True)
