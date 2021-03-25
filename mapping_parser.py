import sys
import json
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
joinCondition_dict = defaultdict()
child_dict = defaultdict()
parent_dict = defaultdict()

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
        #obj = remove_prefix(obj.toPython())
        triples[pred][subj].append(obj)
        file.writelines('{} {} {}\n'.format(subj, pred, obj))
        if pred == 'class':
            obj = remove_prefix(obj.toPython())
            class_dict[subj] = obj
        if pred == 'constant':
            obj = remove_prefix(obj.toPython())
            constant_dict[subj] = obj
        if pred == 'datatype':
            obj = remove_prefix(obj.toPython())
            datatype_dict[subj] = obj
        if pred == 'iterator':
            obj = remove_prefix(obj.toPython())
            iterator_dict[subj] = obj
        if pred == 'logicalSource':
            obj = remove_prefix(obj.toPython())
            logicalSource_dict[subj] = obj
        if pred == 'objectMap':
            obj = remove_prefix(obj.toPython())
            objectMap_dict[subj] = obj
        if pred == 'parentTriplesMap':
            obj = remove_prefix(obj.toPython())
            parentTriplesMap_dict[subj] = obj
        if pred == 'predicate':
            obj = remove_prefix(obj.toPython())
            predicate_dict[subj] = obj
        if pred == 'predicateObjectMap':
            obj = remove_prefix(obj.toPython())
            predicateObjectMap_dict[subj].append(obj)
        if pred == 'reference':
            obj = remove_prefix(obj.toPython())
            reference_dict[subj] = obj
        if pred == 'referenceFormulation':
            obj = remove_prefix(obj.toPython())
            referenceFormulation_dict[subj] = obj
        if pred == 'source':
            source_dict[subj] = obj.toPython()
        if pred == 'subjectMap':
            obj = remove_prefix(obj.toPython())
            subjectMap_dict[subj] = obj
        if pred == 'template':
            #obj = remove_prefix(obj.toPython())
            templateMap_dict[subj] = obj.toPython()
        if pred == 'joinCondition':
            obj = remove_prefix(obj.toPython())
            joinCondition_dict[subj] = obj
        if pred == 'child':
            obj = remove_prefix(obj.toPython())
            child_dict[subj] = obj
        if pred == 'parent':
            obj = remove_prefix(obj.toPython())
            parent_dict[subj] = obj
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

def generateLogicalSourceList():
    logicalSource_lst = []
    for (key, value) in source_dict.items():
        if key in iterator_dict.keys():
            iterator_str = iterator_dict[key]
        else:
            iterator_str = ''
        ls_record = {'name': key, 'source': value, 'referenceFormulation': 'ql:' + referenceFormulation_dict[key], 'iterator': iterator_str}
        logicalSource_lst.append(ls_record)
    return  logicalSource_lst

def generateMappingList():
    mappings_lst = []
    for (key, value) in logicalSource_dict.items():
        mapping_dict = dict()
        # render 'name' and 'logicalSource' fields
        mapping_dict['name'] = key
        mapping_dict['logicalSource'] = value
        # render 'subjectMap' field
        subjecMap_key = subjectMap_dict[key]
        template = templateMap_dict[subjecMap_key]
        classOf = class_dict[subjecMap_key]
        poms_lst = []
        for pom_anonymou_name in predicateObjectMap_dict[key]:
            pom_dict = dict()
            pom_dict['predicate'] = predicate_dict[pom_anonymou_name]
            om_anonymous_name = objectMap_dict[pom_anonymou_name]
            if om_anonymous_name in reference_dict.keys():
                reference_field = reference_dict[om_anonymous_name]
                data_type = datatype_dict[om_anonymous_name]
                pom_dict['objectMap'] = {'reference': reference_field, 'datatype': data_type}
            if om_anonymous_name in constant_dict.keys():
                #this if block is not yet tested
                constant_value = constant_dict[om_anonymous_name]
                pom_dict['objectMap'] = {'constant': constant_value}
            if om_anonymous_name in parentTriplesMap_dict.keys():
                parentMapping_name = parentTriplesMap_dict[om_anonymous_name]
                jc_anonymous_name = joinCondition_dict[om_anonymous_name]
                child_filed = child_dict[jc_anonymous_name]
                parent_field = parent_dict[jc_anonymous_name]
                pom_dict['objectMap'] = {'parentTriplesMap': parentMapping_name, 'joinCondition': {'child': child_filed, 'parent': parent_field}}
            poms_lst.append(pom_dict)
        mapping_dict['subjectMap'] = {'template': template, 'class': classOf}
        mapping_dict['predicateObjectMap'] = poms_lst
        mappings_lst.append(mapping_dict)
    return mappings_lst

def write_json(mapping):
    with open('mappings.json', 'w') as fp:
        json.dump(mapping, fp)

if __name__ == '__main__':
    g = parse_mapping(str(sys.argv[1])) 
    #data, interface_field_dict = read_graphql_schema('schema.graphql')
    #print(interface_field_dict)
    #resolver_gen(interface_field_dict)
    #print(class_dict)
    #print(subjectMap_dict)
    logicalSource_lst = generateLogicalSourceList()
    mappings_lst = generateMappingList()
    #print(logicalSource_lst)
    #print(mappings_lst)
    rml_mapping = {'sources': logicalSource_lst, 'mappings': mappings_lst}
    write_json(rml_mapping)
    
    #print(predicate_dict)
    #print(predicateObjectMap_dict)
        