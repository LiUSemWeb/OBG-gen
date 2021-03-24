from ariadne import gql
from graphql import parse

def checkNodeType(Node):
    if Node.kind == 'non_null_type':
        return 'non_null_type'
    if Node.kind == 'named_type':
        return 'named_type'
    if Node.kind == 'list_type':
        return 'list_type'
    return 0

def parseField(field):
    named_type_value = ''
    encode_labels = ''
    if 'type' in field.keys:
        if checkNodeType(field.type) == 'non_null_type':
            value, labels = parseField(field.type)
            named_type_value = value
            encode_labels = '1' + labels
        elif checkNodeType(field.type) == 'list_type':
            value, labels = parseField(field.type)
            named_type_value = value
            encode_labels = '2' + labels
        else:
            named_type_value = field.type.name.value
            encode_labels = '0'
    return named_type_value, encode_labels

def getSchemaAST(schema):
    schema_ast = dict()
    document = parse(schema)
    for definition in document.definitions:
        schema_ast[definition.name.value] = dict()
        for wrapped_field in definition.fields:
            named_type_value, encode_labels = parseField(wrapped_field)
            schema_ast[definition.name.value][wrapped_field.name.value] = {'base_type': named_type_value, 'wrapping_label': encode_labels}
    return schema_ast

def getAST(schema, query_info):
    queryAST = dict()
    schemaAST = getSchemaAST(schema)
    root = query_info.field_name
    queryFieldsNodes = query_info.field_nodes
    queryAST = parseQueryFields('Query',queryFieldsNodes)
    print(queryAST)
    query_entry_name = queryAST['fields'][0]['name']
    queryAST['fields'][0]['type'] = schemaAST['Query'][query_entry_name]['base_type']
    newAST = fillQueryAST(queryAST['fields'][0], schemaAST, 'Calculation')
    print(newAST)
    return queryAST


def fillQueryAST(queryAST, schemaAST, parentType):
    if len(queryAST['fields']) > 0:
        temp_fields = []
        for subAST in queryAST['fields']:
            subAST['type'] = schemaAST[parentType][subAST['name']]['base_type']
            new_subAST = fillQueryAST(subAST, schemaAST, subAST['type'])
            temp_fields.append(new_subAST)
        queryAST['fields'] = temp_fields
    return queryAST

def parseQueryFields(root_name, query_field_notes):
    result = dict()
    result['name'] = root_name
    result['type'] = ''
    fields = []
    for qfn in query_field_notes:
        if qfn.selection_set is not None:
            next_level_qfns = qfn.selection_set.selections
            #print(qfn.name.value)
            temp_result = parseQueryFields(qfn.name.value, next_level_qfns)
            fields.append(temp_result)
        else:
            field = {'name': qfn.name.value, 'type': '', 'fields': []}
            #print(qfn.name.value)
            fields.append(field)
    result['fields'] = fields
    return result



