from ariadne import ObjectType, QueryType, gql, make_executable_schema, graphql_sync, load_schema_from_path
from ariadne.asgi import GraphQL
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify
from graphql import parse
from graphql.language.ast import *
import sys
from odgsg_graphql_utils import Resolver_Utils

global ru
global type_defs
global query
# Define types using Schema Definition Language (https://graphql.org/learn/schema/)
# Wrapping string in gql function provides validation and better error traceback


# Resolvers are simple python functions

def Generic_Resolver(_, info):
    #global ru
    #print(schemaAST)
    queryAST = ru.getAST(type_defs, info) 
    #print(queryAST)
    result = ru.DataFetcher(queryAST['fields'][0])
    #print(result)
    return result

# Create an ASGI app using the schema, running in debug mode
#app = GraphQL(schema, debug=True)
app = Flask(__name__)

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

'''
def CalculationList(_, info):
    print('In Calculation')
    result = Generic_Resolver(info)
    return result
    return [
        {"ID": "123", "hasOutputStructure": [{"hasComposition": {"ReducedFormula": "SiO2"}}]  },
        {"ID": "456", "hasOutputStructure": [{"hasComposition": {"ReducedFormula": "SiC"}}]   }
    ]
query.set_field("CalculationList", Generic_Resolver)
'''
def register_queries(query_entries):
    for query_entry in query_entries:
        query.set_field(query_entry, Generic_Resolver)


#main function
if __name__ == "__main__":
    query = QueryType()
    ru = Resolver_Utils()
    schema_file = (str(sys.argv[1])) 
    mapping_file = (str(sys.argv[2]))
    type_defs = load_schema_from_path(schema_file)
    ru.set_mappings(mapping_file)
    ru.set_Phi('o2graphql.json')
    register_queries(ru.getQueryEntries(type_defs))
    schema = make_executable_schema(type_defs, query)
    app.run(debug=True)