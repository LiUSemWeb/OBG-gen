import sys
from collections import defaultdict
from rdflib import Graph
from graphql import build_schema, is_object_type, get_named_type, is_interface_type, assert_valid_schema, is_input_type, is_union_type
from graphql import is_scalar_type, is_wrapping_type, is_list_type



triples = defaultdict(lambda: defaultdict(list))

class_dict = defaultdict()
constant_dict = defaultdict()
datatype_dict = defaultdict()
iterator_dict = defaultdict()
logicalSource_dict = defaultdict()
objectMap_dict = defaultdict()
parentTriplesMap_dict = defaultdict()
predicate_dict = defaultdict()
predicateObjectMap_dict = defaultdict(list)
reference_dict = defaultdict()
referenceFormulation_dict = defaultdict()
source_dict = defaultdict()
subjectMap_dict = defaultdict()
templateMap_dict = defaultdict()

def print_info():
    print(class_dict, '\n', constant_dict, '\n', datatype_dict, '\n', subjectMap_dict)

def read_file(file_name):
    content = ''
    with open(file_name) as f:
        content = f.read()
    return content

def remove_prefix(s):
    if 'http' in s:
        if '#' in s:
            return s.split('#')[1]
        else:
            return s.split('/')[-1]
    else:
        return s

def parse_mapping(mapping_file = 'venue-mapper.ttl', format = 'n3'):
    g = Graph()
    file = open('all_triples.txt', 'w')
    g.parse(mapping_file, format=format)
    for subj, pred, obj in g:
        subj = remove_prefix(subj.toPython())
        pred = remove_prefix(pred.toPython())
        obj = remove_prefix(obj.toPython())
        triples[pred][subj].append(obj)
        file.writelines('{} {} {}\n'.format(subj, pred, obj))
        if pred == 'class':
            class_dict[subj] = obj
        if pred == 'constant':
            constant_dict[subj] = obj
        if pred == 'datatype':
            datatype_dict[subj] = obj
        if pred == 'iterator':
            iterator_dict[subj] = obj
        if pred == 'logicalSource':
            logicalSource_dict[subj] = obj
        if pred == 'objectMap':
            objectMap_dict[subj] = obj
        if pred == 'parentTriplesMap':
            parentTriplesMap_dict[subj] = obj
        if pred == 'predicate':
            predicate_dict[subj] = obj
        if pred == 'predicateObjectMap':
            predicateObjectMap_dict[subj].append(obj)
        if pred == 'reference':
            reference_dict[subj] = obj
        if pred == 'referenceFormulation':
            referenceFormulation_dict[subj] = obj
        if pred == 'source':
            source_dict[subj] = obj
        if pred == 'subjectMap':
            subjectMap_dict[subj] = obj
        if pred == 'template':
            templateMap_dict[subj] = obj
    #print_info()

    return g

def is_query_type(_type):
    return is_object_type(_type) and _type.name == 'Query'

def camelCase(s):
    return s[0].lower() + s[1:]

def schema_render(schema):
    #interface_field_dict = defaultdict(list)
    interface_field_dict = defaultdict(lambda: defaultdict())
    data = {'interfaces': [], 'types': [], 'query_fields': []}
    for type_name, _type in schema.type_map.items():
        if is_interface_type(_type):
            data['interfaces'].append(type_name)
            for field_name, field_type in _type.fields.items():
                #print(field_name, field_type.type, type(field_type), is_list_type(field_type.type))
                #interface_field_dict[type_name].append((field_name,field_type))
                interface_field_dict[type_name][field_name] = field_type
        if is_query_type(_type):
            t = {
                'Name': type_name,
                'name': camelCase(type_name),
                'fields': []
            }
            for field_name, field_type in _type.fields.items():
                #if is_schema_defined_object_type(field_type) or is_interface_type(field_type):
                t['fields'].append(field_name)
                data['query_fields'].append(field_name)
            data['types'].append(t)
    data['interfaces'].sort()
    data['types'].sort(key=lambda x: x['name'])
    return data, interface_field_dict

def read_graphql_schema(schema_file):
    schema_str = read_file(schema_file)
    schema = build_schema(schema_str)
    return schema_render(schema)

def reference(logical_source, path):
    print('reference: ' + logical_source, path)
    return 0

def resolver_gen(interface_field_dict):
    #key is the mapping name, value is the anonymous
    for schema_type in interface_field_dict.keys():
        print('function set_' + schema_type + '(){')
        for (key, value) in subjectMap_dict.items():
            if class_dict[value] == schema_type:
                #print(key, logicalSource_dict[key], predicateObjectMap_dict[key])
                #print(logicalSource_dict[key])
                for object_map_key in predicateObjectMap_dict[key]:
                    #print(key, objectMap_dict[object_map_key])
                    # predicateObject is constant
                    if objectMap_dict[object_map_key] in constant_dict.keys():
                        #check datatype
                        if datatype_dict[objectMap_dict[object_map_key]] == 'string':
                            print('\t' + predicate_dict[object_map_key] + ': \'' + constant_dict[objectMap_dict[object_map_key]] + '\',')
                    # predicateObject is reference
                    if objectMap_dict[object_map_key] in reference_dict.keys():
                        #print('reference: ' + predicate_dict[object_map_key], reference_dict[objectMap_dict[object_map_key]])
                        #reference(logicalSource_dict[key], reference_dict[objectMap_dict[object_map_key]])
                        print('\t' + predicate_dict[object_map_key] + ': ' + reference_dict[objectMap_dict[object_map_key]], ',')
                    # predicateObject is pointing to another mapping
                    if objectMap_dict[object_map_key] in parentTriplesMap_dict.keys():
                        #print('parentsTriplesMap: ' + predicate_dict[object_map_key], parentTriplesMap_dict[objectMap_dict[object_map_key]])
                        parentTriplesMap_key = subjectMap_dict[parentTriplesMap_dict[objectMap_dict[object_map_key]]]
                        print('\t' + predicate_dict[object_map_key] + ': set_' + class_dict[parentTriplesMap_key] + '(),')
        print('}')
        print('---------------------------------------------------------------')
    return 0




if __name__ == '__main__':
    g = parse_mapping(str(sys.argv[1])) 
    #data, interface_field_dict = read_graphql_schema('schema.graphql')
    #print(interface_field_dict)
    #resolver_gen(interface_field_dict)
    #print(class_dict)
    #print(subjectMap_dict)
    #print(logicalSource_dict)
    #print(predicate_dict)
    #print(predicateObjectMap_dict)
        