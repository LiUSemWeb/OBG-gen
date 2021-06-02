import sys
import datetime
from ariadne import QueryType, make_executable_schema, graphql_sync, load_schema_from_path
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify
from generic_resolver.odgsg_graphql_utils import Resolver_Utils
from generic_resolver.filter_utils import Filter_Utils

global ru
global type_defs
global query


# Define types using Schema Definition Language (https://graphql.org/learn/schema/)
# Wrapping string in gql function provides validation and better error traceback
# Resolvers are simple python functions

def generic_resolver(_, info, **kwargs):
    result = []
    a = datetime.datetime.now()
    # print('info', info)
    filter_condition = kwargs
    if len(filter_condition) > 0:
        fu = Filter_Utils()
        fu.parse_cond(filter_condition)
        dnf_lst = fu.simplify()
        ru.set_symbol_field_maps(fu.field_exp_symbol, fu.symbol_field_exp)
        print('DNF', dnf_lst)
        filter_asts, common_prefix, repeated_single_exp = ru.generate_filter_asts(ru.filter_fields_map,
                                                                                  ru.symbol_field_exp, dnf_lst,
                                                                                  'CalculationList')
        print('CP:', common_prefix)
        print('RSP:', repeated_single_exp)
        for filter_ast in filter_asts:
            filter_df = ru.filter_evaluator(filter_ast.children[0], common_prefix, repeated_single_exp)
            for key, value in filter_df.items():
                object_iri_lst = value['iri'].tolist()
                if len(object_iri_lst) > 0:
                    if key in ru.filtered_object_iri.keys():
                        ru.filtered_object_iri[key] = list(set(ru.filtered_object_iri[key] + object_iri_lst))
                    else:
                        ru.filtered_object_iri[key] = object_iri_lst
        print('filtered_result', ru.filtered_object_iri)
        if len(ru.filtered_object_iri.keys()) > 0:
            ru.filtered_object_iri['filter'] = True
            query_ast = ru.generate_query_ast(type_defs, info)
            # result = ru.DataFetcher(query_ast['fields'][0])
            result = ru.query_evaluator(query_ast['fields'][0], None, None, True, ru.filtered_object_iri.keys())
            b = datetime.datetime.now()
            print('Response Time:', (b - a))
    else:
        ru.filtered_object_iri['filter'] = False
        query_ast = ru.generate_query_ast(type_defs, info)
        # result = ru.DataFetcher(query_ast['fields'][0])
        result = ru.query_evaluator(query_ast['fields'][0], None, None, True)
        b = datetime.datetime.now()
        print('Response Time:', (b - a))
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
        query.set_field(query_entry, generic_resolver)


# main function
if __name__ == "__main__":
    # app.wsgi_app = MoesifMiddleware(app.wsgi_app, moesif_settings)
    query = QueryType()
    schema_file = (str(sys.argv[1]))
    mapping_file = (str(sys.argv[2]))
    type_defs = load_schema_from_path(schema_file)
    ru = Resolver_Utils(mapping_file, 'o2graphql.json')
    # ru.set_mappings(mapping_file)
    # ru.set_Phi()
    register_queries(ru.get_query_entries(type_defs))
    # print('ru', ru.filter_fields_map)
    schema = make_executable_schema(type_defs, query)
    app.run(debug=True)
