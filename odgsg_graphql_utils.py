import requests
import csv
import codecs
from contextlib import closing
from mapping_utils import RML_Mapping
from collections import defaultdict
from graphql import parse
import json
import pymongo
import urllib.parse
import pymongo
import ast




class Resolver_Utils(object):
    '''
    def __init__(self):
        self.ontology_GraphQLschema = {'Calculation': 'Calculation', 'CalculatedProperty':'CalculatedProperty', 'Structure':'Structure', 'Composition':'Composition', 'QuantityValue': 'QuantityValue',
                          'hasOutputStructure': 'hasOutputStructure', 'hasComposition': 'hasComposition', 'hasOutputCalculatedProperty': 'hasOutputCalculatedProperty','quantityValue': 'quantityValue',
                          'ID': 'ID', 'ReducedFormula': 'ReducedFormula', 'AnonymousFormula': 'AnonymousFormula', 'PropertyName': 'PropertyName', 'numericValue': 'numericValue'}
        self.GraphQLschema_Ontology = {'Calculation': 'Calculation', 'CalculatedProperty':'CalculatedProperty', 'Structure':'Structure', 'Composition':'Composition', 'QuantityValue': 'QuantityValue',
                          'hasOutputStructure': 'hasOutputStructure', 'hasComposition': 'hasComposition', 'hasOutputCalculatedProperty': 'hasOutputCalculatedProperty','quantityValue': 'quantityValue',
                          'ID': 'ID', 'ReducedFormula': 'ReducedFormula', 'AnonymousFormula': 'AnonymousFormula', 'PropertyName': 'PropertyName', 'numericValue': 'numericValue'}
        self.scalar_types = ['Int', 'Float', 'String', 'Boolean', 'ID', 'CUSTOM_SCALAR_TYPE']
    '''
    def __init__(self):
        self.ontology_GraphQLschema = dict()
        self.GraphQLschema_Ontology = dict()
        self.mu = None
        self.operator_1 = ['_and', '_or', '_not']
        self.operator_2 = ['_eq', '_neq', '_gt']

    def set_Phi(self, file='o2graphql.json'):
        with open(file) as f:
            self.ontology_GraphQLschema = json.load(f)
            self.GraphQLschema_Ontology = self.ontology_GraphQLschema

    def set_mappings(self, mapping_file):
        self.mu = RML_Mapping(mapping_file)
    
    def parseIterator(self, iterator):
        iterator_elements = iterator.split('.')
        iterator_elements = list(filter(None, iterator_elements))
        return iterator_elements
    
    def getJSONData(self, URL, iterator = None, ref=None):
        r = requests.get(url=URL)
        data = r.json()
        if iterator is not None:
            keys = self.parseIterator(iterator)
            temp_data = data
            for i in range(len(keys)):
                temp_data = temp_data[keys[i]]
            return temp_data
        else:
            return data

    def getCSVData(self, URL, ref = None):
        ref_condition, ref_data = [], []
        if ref is not None:
            ref_condition = ref[1]
            ref_data = [record[ref_condition['child']] for record in ref[0]]
        records = []
        result = []
        with closing(requests.get(URL, stream=True)) as r:
            reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'), delimiter=';')
            for record in reader:
                records.append(record)
        header = records[0]
        num_fields = len(header)
        for record in records[1:]:
            element = dict()
            if ref is not None:
                if record[header.index(ref_condition['parent'])] in ref_data:
                    for i in range(num_fields):
                        element[header[i]] = record[i]
                else:
                    break
            else:
                for i in range(num_fields):
                    element[header[i]] = record[i]
            result.append(element)
        return result
    
    def getMongoDBData(self, server_info, query, iterator = None, ref = None):
        result = []
        parameters = query.split(';')
        mongodb_client_address = server_info['server'] 
        database = parameters[2]
        collection_name = parameters[1]
        projection = ast.literal_eval(parameters[0])
        dbclient = pymongo.MongoClient(mongodb_client_address)
        mongodb = dbclient[database]
        mongodb_collection = mongodb[collection_name]
        if ref == None:
            result = list(mongodb_collection.find({}, projection))
            #print(result['data'])
            temp_data = result[0]
            keys = self.parseIterator(iterator)
            for i in range(len(keys)):
                temp_data = temp_data[keys[i]]
            result = temp_data
        return result

    def parseAST(self, AST):
        concept_type = AST['type']
        queryFields = []
        for field in AST['fields']:
            queryFields.append(field['name'])
        return concept_type, queryFields

    def getSubAST(self, AST, predicate):
        fields = AST['fields']
        newAST = None
        for field in fields:
            if field['name'] == predicate:
                newAST = field
                break
        return newAST

    def getMappings(self, concept_type):
        return self.mu.getMappingsByType(concept_type)

    def getLogicalSource(self, mapping):
        return self.mu.getLogicalSourceByMapping(mapping)    

    def getTemplate(self, mapping):
        return self.mu.getSubjectTemplateByMapping(mapping)


    def Phi(self, ontology_term):
        return self.ontology_GraphQLschema[ontology_term]

    def Phi_inverse(self, GraphQL_term):
        return self.GraphQLschema_Ontology[GraphQL_term]

    def Translate(self, queryFields):
        predicates = []
        for field in queryFields:
            predicates.append(self.Phi_inverse(field))
        return predicates

    def Execute(self, logicalSource, ref = None):
        source_type = self.mu.getLSType(logicalSource)
        result = []
        if source_type == 'ql:CSV':
            source_request = self.mu.getSource(logicalSource)
            result = self.getCSVData(source_request, ref)
        if source_type == 'ql:JSONPath':
            source_request = self.mu.getSource(logicalSource)
            iterator = self.mu.getJSONIterator(logicalSource)
            result = self.getJSONData(source_request, iterator, ref)
        if source_type == 'mydb:mongodb':
            iterator = self.mu.getJSONIterator(logicalSource)
            server_info, query = self.mu.getDBSource(logicalSource)
            #print('mongodb', server_info, query)
            result = self.getMongoDBData(server_info, query, iterator)
            #print(result)
        return result

    def getPredicateObjectMap(self, mapping, predicates):
        return self.mu.getPredicateObjectMapByPred(mapping, predicates)

    def parsePOM(self, pom):
        return self.mu.parsePOM(pom)

    def parseROM(self, objectMap):
        return self.mu.parseROM(objectMap)

    def getReference(self, termMap):
        return self.mu.getReference(termMap)

    def parseJoinCondition(self, joinCondition):
        return self.mu.parseJoinCondition(joinCondition)

    def getChildData(self, tempResult, childField):
        return [ {childField: record[childField]} for record in tempResult ]

    def parseTemplate(self, template):
        start_pos = template.index('{')
        end_pos = template.index('}')
        key = template[start_pos + 1: end_pos]
        newtemplate = template.replace(key,'')
        return key, newtemplate

    # need to update
    def Refine(self, tempResult, attr_pred_lst, constant, template):
        key, template = self.parseTemplate(template)
        for record in tempResult:
            record['iri'] = template.format(record[key])
            for attr_pred_tuple in attr_pred_lst:
                if '.' in attr_pred_tuple[0]:
                    keys = self.parseIterator(attr_pred_tuple[0])
                    temp_data = record
                    #print(temp_data)
                    for i in range(len(keys)):
                        temp_data = temp_data[keys[i]]
                    #del record[keys[0]]
                    record[attr_pred_tuple[1]] = temp_data
                else:
                    if attr_pred_tuple[0] in record.keys():
                        #record[attr_pred_tuple[1]] = record.pop(attr_pred_tuple[0])
                        record[attr_pred_tuple[1]] = record[attr_pred_tuple[0]]
        return tempResult

    def IncrementalJoin(self, tempResult, result2join):
        result = []
        if len(result2join) > 0: 
            for (joinData, joinCondition, field, AST) in result2join:
                for join_record in joinData: 
                    for record in tempResult:
                        #print(joinCondition)
                        #print(record)
                        #print(join_record)
                        if record[joinCondition['child']] == join_record[joinCondition['parent']]:
                            new_record = record
                            # if field returns a list
                            # Update may need here if we null allows
                            if AST['wrapping_label'] == '0' or AST['wrapping_label'] == '10':
                                new_record[field] = join_record
                            else:
                                new_record[field] = [join_record]
                            result.append(new_record)
            return result
        else: 
            return tempResult

    def Merge(self, result, tempResult):
        return result + tempResult

    def DuplicateDetectionFusion(self, result):
        return result

    def TypeOfObjectMap(self, objectMap):
        return self.mu.TypeOfObjectMap(objectMap)

    def DataFetcher(self, AST, mapping = None, ref= None):
        result, mappings = [], []
        concept_type, queryFields = self.parseAST(AST)
        if mapping is None:
            mappings = self.getMappings(concept_type)
        else:
            mappings.append(mapping)
        predicates = self.Translate(queryFields)
        for mapping in mappings:
            logicalSource = self.getLogicalSource(mapping)
            template = self.getTemplate(mapping)
            tempResult = self.Execute(logicalSource, ref)
            poms = self.getPredicateObjectMap(mapping, predicates)
            attr_pred, result2join, constant = [], [], []
            for pom in poms:
                predicate, objectMap = self.parsePOM(pom)
                if self.TypeOfObjectMap(objectMap) == 1:
                    referenceAttribute = self.getReference(objectMap)
                    attr_pred.append((referenceAttribute, self.Phi(predicate)))
                if self.TypeOfObjectMap(objectMap) == 2:
                    print('Constant')
                if self.TypeOfObjectMap(objectMap) == 3:
                    newAST = self.getSubAST(AST, self.Phi(predicate))
                    parentMapping, joinCondition = self.parseROM(objectMap)
                    childField, parentField = self.parseJoinCondition(joinCondition)
                    childData = self.getChildData(tempResult, childField)
                    ref = (childData, joinCondition)
                    parentData = self.DataFetcher(newAST, parentMapping, ref)
                    result2join.append((parentData, joinCondition, self.Phi(predicate), newAST))
            tempResult = self.Refine(tempResult, attr_pred, constant, template)
            tempResult = self.IncrementalJoin(tempResult, result2join)
            result = self.Merge(result, tempResult)
        return self.DuplicateDetectionFusion(result)

    def check_node_type(self, Node):
        if Node.kind == 'non_null_type':
            return 'non_null_type'
        if Node.kind == 'named_type':
            return 'named_type'
        if Node.kind == 'list_type':
            return 'list_type'
        return 0

    def parse_field(self, field):
        named_type_value = ''
        encode_labels = ''
        if 'type' in field.keys:
            # named_type: 0, list_type: 2, non_null_type 1
            if self.check_node_type(field.type) == 'non_null_type':
                value, labels = self.parse_field(field.type)
                named_type_value = value
                encode_labels = '1' + labels
            elif self.check_node_type(field.type) == 'list_type':
                value, labels = self.parse_field(field.type)
                named_type_value = value
                encode_labels = '2' + labels
            else:
                named_type_value = field.type.name.value
                encode_labels = '0'
        return named_type_value, encode_labels

    def getSchemaAST(self, schema):
        schema_ast = dict()
        filter_ast = dict()
        document = parse(schema)
        for definition in document.definitions:
            if definition.kind == 'object_type_definition':
                schema_ast[definition.name.value] = dict()
                for wrapped_field in definition.fields:
                    named_type_value, encode_labels = self.parse_field(wrapped_field)
                    schema_ast[definition.name.value][wrapped_field.name.value] = {'base_type': named_type_value, 'wrapping_label': encode_labels}
            if definition.kind == 'input_object_type_definition':
                #print(definition.name.value)
                schema_ast[definition.name.value] = dict()
                for wrapped_field in definition.fields:
                    named_type_value, encode_labels = self.parse_field(wrapped_field)
                    schema_ast[definition.name.value][wrapped_field.name.value] = {'base_type': named_type_value, 'wrapping_label': encode_labels}
        #print(filter_ast)
        return schema_ast
    def checkinputtype(self, schema):
        document = parse(schema)
        print('Input')
        print(document)
        for definition in document.definitions:
            print(definition.name.value, definition.kind)
        return 0
    def getQueryEntries(self, schema):
        query_entries = []
        schema_AST = self.getSchemaAST(schema)
        query_entries = list(schema_AST['Query'].keys())
        return query_entries

    def getAST(self, schema, query_info, filter_condition):
        queryAST = dict()
        schemaAST = self.getSchemaAST(schema)
        root = query_info.field_name
        queryFieldsNodes = query_info.field_nodes
        queryAST = self.parse_query_fields('Query',queryFieldsNodes, filter_condition)
        #self.parse_filter_condition(queryAST,filter_condition)
        query_entry_name = queryAST['fields'][0]['name']
        queryAST['fields'][0]['type'] = schemaAST['Query'][query_entry_name]['base_type']
        queryAST['fields'][0]['wrapping_label'] = schemaAST['Query'][query_entry_name]['wrapping_label']
        newAST = self.fill_return_type(queryAST['fields'][0], schemaAST, queryAST['fields'][0]['type'])
        print('queryAST', queryAST)
        return queryAST

    @staticmethod
    def get_filter_field(bool_exp_list, filed):
        for bool_exp in bool_exp_list:
            return 0
        return 0

    def fill_return_type(self, queryAST, schemaAST, parentType):
        if len(queryAST['fields']) > 0:
            temp_fields = []
            for subAST in queryAST['fields']:
                #subAST['name']

                subAST['type'] = schemaAST[parentType][subAST['name']]['base_type']
                subAST['wrapping_label'] = schemaAST[parentType][subAST['name']]['wrapping_label']
                new_subAST = self.fill_return_type(subAST, schemaAST, subAST['type'])
                temp_fields.append(new_subAST)
            queryAST['fields'] = temp_fields
        return queryAST

    @staticmethod
    def check_filter_type(filter_condition):
        new_filter = dict()
        new_filter['_and'] = []
        if len(filter_condition) is 1:
            keys = filter_condition.keys()
            if '_and' in keys or '_or' in keys:
                new_filter = filter_condition
            else:
                new_filter['_and'].append(filter_condition)
        else:
            for key, value in filter_condition.items():
                new_filter['_and'].append({key:value})
        return new_filter

    def parse_query_fields(self, root_name, query_field_notes, filter_condition):
        result = dict()
        result['name'] = root_name
        result['type'] = ''
        fields = []
        for qfn in query_field_notes:
            if qfn.selection_set is not None:
                next_level_qfns = qfn.selection_set.selections
                temp_result = self.parse_query_fields(qfn.name.value, next_level_qfns, filter_condition)
                fields.append(temp_result)
            else:
                field = {'name': qfn.name.value, 'type': '', 'fields': []}
                fields.append(field)
        result['fields'] = fields
        return result

    def parse_filter_condition(self, queryAST, filter_condition):
        for (filter_field, filter_type) in filter_condition['filter'].items():
            if filter_field in self.operator_1:
                print(filter_field)
            else:
                print('-')
        print('asd')
        print('qast', queryAST)
        print('fc', filter_condition)
        return 0