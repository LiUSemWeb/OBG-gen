from ariadne import ObjectType, QueryType, gql, make_executable_schema, graphql_sync, load_schema_from_path
from ariadne.asgi import GraphQL
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify
from graphql import parse
from graphql.language.ast import *
import sys
import graphql_utils as gu



# Define types using Schema Definition Language (https://graphql.org/learn/schema/)
# Wrapping string in gql function provides validation and better error traceback

type_defs = load_schema_from_path("./schema.graphql")

# Map resolver functions to Query fields using QueryType
query = QueryType()


def Resolver(schema, query_info):
    #schemaAST = gu.getSchemaAST(schema)
    #print(schemaAST)
    print(query_info)
    queryAST = gu.getAST(schema, query_info) 
    return 0
# Resolvers are simple python functions
#@query.field("StructureList")
#@query.field("CompositionList")

#@query.field("people")
def resolve_people(_, info):
    #print('in this resolver', file=sys.stderr)
    #print(info, file=sys.stderr)
    #print(dict.get(info.field_name))
    print('in people')
    print(info)
    print(info.field_nodes[0].name.value)
    print(info.field_nodes[0].selection_set.selections[0].name.value)
    return [
        {"firstName": "John", "lastName": "Doe", "age": 21},
        {"firstName": "Bob", "lastName": "Boberson", "age": 24},
    ]
query.set_field("people", resolve_people)


#@query.field("CalculationList")
def CalculationList(_, info):
    print('In Calculation')
    Resolver(type_defs, info)
    return [
        {"ID": "123", "hasOutputStructure": [{"hasComposition": {"ReducedFormula": "SiO2"}}]  },
        {"ID": "456", "hasOutputStructure": [{"hasComposition": {"ReducedFormula": "SiC"}}]   }
    ]
query.set_field("CalculationList", CalculationList)

# Map resolver functions to custom type fields using ObjectType
person = ObjectType("Person")

@person.field("fullName")
def resolve_person_fullname(person, *_):
    return "%s %s" % (person["firstName"], person["lastName"])


# Create executable GraphQL schema
schema = make_executable_schema(type_defs, query, person)

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


if __name__ == "__main__":
    #app.run(debug=True, PYTHONUNBUFFERED =1, FLASK_ENV='development')
    app.run(debug=True)