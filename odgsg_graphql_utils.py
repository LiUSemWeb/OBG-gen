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
from collections import defaultdict
from sympy.logic.boolalg import to_dnf
from sympy.logic.inference import satisfiable
import pandas as pd
from pandas import json_normalize


class FilterAST(object):
    def __init__(self, name, children = None, parent = None, parent_edge = None, filter_dict = None):
        #data in the form of list of (field name: symbol (with negation or not))
        self.name = name
        self.children = children or []
        self.parent = parent
        self.parent_edge = parent_edge
        self.children_edges = []
        self.filter_dict = filter_dict or {}
        self.parent_edge_chain = ''

    def add_child(self, child_name, edge):
        new_child = FilterAST(child_name, parent=self, parent_edge=edge)
        new_child.parent_edge_chain = self.parent_edge_chain + '.' + edge
        self.children.append(new_child)
        self.children_edges.append(edge)
        return new_child

    def add_child_edge(self, child_edge):
        self.children_edges.append(child_edge)

    def add_attribute_filter(self, attr_symbol, filter_dict):
        self.filter_dict[attr_symbol] = filter_dict

    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return not self.children

    def getSubTrees(self):
        return self.children

    def getSubTree(self, edge):
        return_child = None
        for child in self.children:
            if child.parent_edge == edge:
                return_child = child
                break
        return return_child

    def getCurrentFilter(self):
        if len(self.filter_dict) > 0:
            return self.filter_dict
        else:
            return {}
    def getCurrentExpSymbols(self):
        exp_symbols = set()
        current_filter = self.getCurrentFilter()
        if current_filter is not None:
            for key, value in current_filter.items():
                for exp in value:
                    exp_symbols.add(exp['symbol'])
        else:
            if self.name is not 'root':
                exp_symbols.add(self.name + '-ALL')
        return exp_symbols

    def getPrefixExps(self):
        if len(self.children) > 0:
            exp_symbols = self.getCurrentExpSymbols()
            for child in self.children:
                child_prefix_exp_symbols = child.getPrefixExps()
                exp_symbols = set.union(exp_symbols, child_prefix_exp_symbols)
            return exp_symbols
        else:
            return set()

    def getAllExps(self):
        exp_symbols = self.getCurrentExpSymbols()
        for child in self.children:
            child_prefix_exp_symbols = child.getAllExps()
            exp_symbols = set.union(exp_symbols, child_prefix_exp_symbols)
        return exp_symbols


class ResolverUtils(object):
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
    def __init__(self, mapping_file, o2graphql_file = 'o2graphql.json'):
        self.mu = RML_Mapping(mapping_file)
        self.operator_1 = ['_and', '_or', '_not']
        self.operator_2 = ['_eq', '_neq', '_gt']
        self.field_exp_symbol = dict()
        self.symbol_field_exp = dict()
        self.schemaAST = dict()
        self.cache = dict()
        self.common_exp_symbols = []
        self.filter_fields_map = dict()
        self.mapping_attr_pred_dict = defaultdict(dict)
        self.filtered_object_iri = dict()
        with open(o2graphql_file) as f:
            self.ontology_GraphQLschema = json.load(f)
            self.GraphQLschema_Ontology = self.ontology_GraphQLschema

    def set_symbol_field_maps(self, field_exp_symbol, symbol_field_exp):
        self.field_exp_symbol = field_exp_symbol
        self.symbol_field_exp = symbol_field_exp

    
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

    def Execute(self, logicalSource, ref = None, filter = None):
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
            result = self.getMongoDBData(server_info, query, iterator)
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
    def RefineJSON(self, tempResult, attr_pred_lst, constant, template, root_type = False, mapping_name = ''):
        key, template = self.parseTemplate(template)
        i=0
        while i < len(tempResult):
            iri = template.format(tempResult[i][key])
            if root_type is True:
                if iri in self.filtered_object_iri[mapping_name]:
                    tempResult[i]['iri'] = iri
                    for attr_pred_tuple in attr_pred_lst:
                        if '.' in attr_pred_tuple[0]:
                            keys = self.parseIterator(attr_pred_tuple[0])
                            temp_data = tempResult[i]
                            for i in range(len(keys)):
                                temp_data = temp_data[keys[i]]
                                tempResult[i][attr_pred_tuple[1]] = temp_data
                        else:
                            if attr_pred_tuple[0] in tempResult[i].keys():
                                # record[attr_pred_tuple[1]] = record.pop(attr_pred_tuple[0])
                                tempResult[i][attr_pred_tuple[1]] = tempResult[i][attr_pred_tuple[0]]
                    i+=1
                else:
                    del tempResult[i]
            else:
                tempResult[i]['iri'] = iri
                for attr_pred_tuple in attr_pred_lst:
                    if '.' in attr_pred_tuple[0]:
                        keys = self.parseIterator(attr_pred_tuple[0])
                        temp_data = tempResult[i]
                        for i in range(len(keys)):
                            temp_data = temp_data[keys[i]]
                            tempResult[i][attr_pred_tuple[1]] = temp_data
                    else:
                        if attr_pred_tuple[0] in tempResult[i].keys():
                            # record[attr_pred_tuple[1]] = record.pop(attr_pred_tuple[0])
                            tempResult[i][attr_pred_tuple[1]] = tempResult[i][attr_pred_tuple[0]]
                i += 1
        '''
        for record in tempResult:
            record['iri'] = template.format(record[key])
            for attr_pred_tuple in attr_pred_lst:
                if '.' in attr_pred_tuple[0]:
                    keys = self.parseIterator(attr_pred_tuple[0])
                    temp_data = record
                    for i in range(len(keys)):
                        temp_data = temp_data[keys[i]]
                    record[attr_pred_tuple[1]] = temp_data
                else:
                    if attr_pred_tuple[0] in record.keys():
                        #record[attr_pred_tuple[1]] = record.pop(attr_pred_tuple[0])
                        record[attr_pred_tuple[1]] = record[attr_pred_tuple[0]]
        
        '''
        #print('length', len(tempResult))
        return tempResult

    def IncrementalJoin(self, tempResult, result2join):
        result = []
        if len(result2join) > 0: 
            for (joinData, joinCondition, field, AST) in result2join:
                for join_record in joinData: 
                    for record in tempResult:
                        if record[joinCondition['child']] == join_record[joinCondition['parent']]:
                            new_record = record
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
            tempResult = self.RefineJSON(tempResult, attr_pred, constant, template)
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
        if len(self.schemaAST) == 0:
            schema_ast = dict()
            #filter_ast = dict()
            document = parse(schema)
            for definition in document.definitions:
                if definition.kind == 'object_type_definition':
                    schema_ast[definition.name.value] = dict()
                    for wrapped_field in definition.fields:
                        named_type_value, encode_labels = self.parse_field(wrapped_field)
                        if definition.name.value == 'Query':
                            #filter_type = self.parseQueryArguments(wrapped_field.arguments)
                            self.filter_fields_map[(wrapped_field.name.value, 'filter')] = named_type_value
                        else:
                            self.filter_fields_map[(definition.name.value, wrapped_field.name.value)] = named_type_value
                        schema_ast[definition.name.value][wrapped_field.name.value] = {'base_type': named_type_value,
                                                                                       'wrapping_label': encode_labels}
                if definition.kind == 'input_object_type_definition':
                    # print(definition.name.value)
                    schema_ast[definition.name.value] = dict()
                    for wrapped_field in definition.fields:
                        named_type_value, encode_labels = self.parse_field(wrapped_field)
                        schema_ast[definition.name.value][wrapped_field.name.value] = {'base_type': named_type_value,
                                                                                       'wrapping_label': encode_labels}
            # print(filter_ast)
            self.schemaAST = schema_ast
            return self.schemaAST
        else:
            return self.schemaAST

    def parseQueryArguments(self, arguments):
        filter_type = ''
        for argu in arguments:
            if argu.name.value == 'filter':
                filter_type = argu.type.name.value
                break
        return filter_type

    def getQueryEntries(self, schema):
        query_entries = []
        schema_AST = self.getSchemaAST(schema)
        query_entries = list(schema_AST['Query'].keys())
        return query_entries

    def getAST(self, schema, query_info):
        queryAST = dict()
        schemaAST = self.getSchemaAST(schema)
        self.schemaAST = schemaAST
        root = query_info.field_name
        queryFieldsNodes = query_info.field_nodes
        queryAST = self.parse_query_fields('Query',queryFieldsNodes)
        query_entry_name = queryAST['fields'][0]['name']
        queryAST['fields'][0]['type'] = schemaAST['Query'][query_entry_name]['base_type']
        queryAST['fields'][0]['wrapping_label'] = schemaAST['Query'][query_entry_name]['wrapping_label']
        newAST = self.fill_return_type(queryAST['fields'][0], schemaAST, queryAST['fields'][0]['type'])
        #print('queryAST', queryAST)
        return queryAST

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

    def parse_query_fields(self, root_name, query_field_notes):
        result = dict()
        result['name'] = root_name
        result['type'] = ''
        fields = []
        for qfn in query_field_notes:
            if qfn.selection_set is not None:
                next_level_qfns = qfn.selection_set.selections
                temp_result = self.parse_query_fields(qfn.name.value, next_level_qfns)
                fields.append(temp_result)
            else:
                field = {'name': qfn.name.value, 'type': '', 'fields': []}
                fields.append(field)
        result['fields'] = fields
        return result

    def get_filter_fields(self, conjunctive_expression, current_type, level):
        current_filter = []
        current_filter_dict = []
        sub_filter = []
        sub_filter_dict = []
        filter_fields = []
        new_conjunctive_expression = []
        #print('schemaAST[current_type]', self.schemaAST[current_type])
        print('current_type', current_type)
        for symbol in conjunctive_expression:
            if symbol[0] is '~':
                cond = self.symbol_field_exp[symbol[1:]]
                field_seq = cond[0].split('.')
                if len(field_seq) is level + 1:
                    current_filter.append(('not',cond))
                    #current_filter_dict.append({'field': cond[0], 'operator': cond[1], 'value': cond[2], 'negation': True})
                    current_filter_dict.append({'operator': cond[1], 'value': cond[2], 'negation': True})
                    if field_seq[-1] not in filter_fields:
                        filter_fields.append(field_seq[-1])
                else:
                    new_conjunctive_expression.append(symbol)
                    sub_filter.append(('not',cond))
                    #sub_filter_dict.append({'field': cond[0], 'operator': cond[1], 'value': cond[2], 'negation': True})
                    sub_filter_dict.append({'operator': cond[1], 'value': cond[2], 'negation': True})
            else:
                cond = self.symbol_field_exp[symbol]
                field_seq = cond[0].split('.')
                if len(field_seq) is level + 1:
                    current_filter.append(cond)
                    #current_filter_dict.append({'field': cond[0], 'operator': cond[1], 'value': cond[2], 'negation': False})
                    current_filter_dict.append({'operator': cond[1], 'value': cond[2], 'negation': False})
                    if field_seq[-1] not in filter_fields:
                        filter_fields.append(field_seq[-1])
                else:
                    new_conjunctive_expression.append(symbol)
                    sub_filter.append(cond)
                    #sub_filter_dict.append({'field': cond[0], 'operator': cond[1], 'value': cond[2], 'negation': False})
                    sub_filter_dict.append({'operator': cond[1], 'value': cond[2], 'negation': False})
        print('current_filter_dict', current_filter_dict)
        print(current_filter)
        return current_filter, sub_filter, filter_fields, new_conjunctive_expression

    def Executor(self, logicalSource, key_attrs, filter_flag= False, filter = None, ref = None):
        source_type = self.mu.getLSType(logicalSource)
        result = []
        if source_type == 'ql:CSV':
            source_request = self.mu.getSource(logicalSource)
            #result = self.getCSVData(source_request, ref)
        if source_type == 'ql:JSONPath':
            source_request = self.mu.getSource(logicalSource)
            iterator = self.mu.getJSONIterator(logicalSource)
            #result = self.getJSONData(source_request, iterator, ref)
            if filter_flag is True:
                result = self.get_json_data(source_request, iterator, key_attrs, filter)
            else:
                result = self.getJSONData(source_request, iterator, ref)
        if source_type == 'mydb:mongodb':
            iterator = self.mu.getJSONIterator(logicalSource)
            server_info, query = self.mu.getDBSource(logicalSource)
            result = self.getMongoDBData(server_info, query, iterator)
        return result

    def get_json_data(self, URL, iterator, key_attrs, filter=None):
        r = requests.get(url=URL)
        if filter is not None:
            for key, value in filter.items():
                if value['local_name'] not in key_attrs:
                    key_attrs.append(value['local_name'])
        data = r.json()
        temp_data = data
        if iterator is not None:
            keys = self.parseIterator(iterator)
            for i in range(len(keys)):
                temp_data = temp_data[keys[i]]
        result = []
        for data_record in temp_data:
            temp_dict = dict()
            for k,v in data_record.items():
                if k in key_attrs:
                    temp_dict[k] = v
            result.append(temp_dict)
        return result
    '''
    def refine(self, temp_result, pred_attr_dict, constant, template):
        key, template = self.parseTemplate(template)
        for record in temp_result:
            record['iri'] = template.format(record[key])
            for pred, attr in pred_attr_dict.items():
                if '.' in attr:
                    keys = self.parseIterator(attr)
                    temp_data = record
                    for i in range(len(keys)):
                        temp_data = temp_data[keys[i]]
                    record[pred] = temp_data
                else:
                    if attr in record.keys():
                        record[pred] = record[attr]
        return temp_result
    '''

    def RefineDataFrame(self, df, pred_attr_dict, constant, template):
        key, template = self.parseTemplate(template)
        df = df.assign(iri = [template.format(x) for x in df[key]])
        for pred, attr in pred_attr_dict.items():
            if attr in list(df.columns):
                if pred != attr:
                    kwargs = {pred : lambda x:  x[attr] }
                    df = df.assign(**kwargs)
        return df

    def localize_filter(self, filter, pred_attr):
        localized_filter = []
        #current filter [('filter.ID', '_eq', '1'), ('not', ('filter.ID', '_eq', '2'))]
        for i in range(len(filter)):
            if filter[i][0] is 'not':
                key = filter[i][1][0].split('.')[-1]
                temp_filter = list(filter[i][1])
                temp_filter[0] = pred_attr[key]
                localized_filter.append(['not'] + temp_filter)
            else:
                temp_filter = list(filter[i])
                key = filter[i][0].split('.')[-1]
                temp_filter[0] = pred_attr[key]
                localized_filter.append(temp_filter)
        return localized_filter

    def generateFilterASTs(self, filter_fields_map, symbol_exp_dict, conjunctive_exp_lst, entry='CalculationList'):
        filter_ASTs = []
        common_prefix = frozenset()
        repeated_single_exp = set()
        all_ast_exp = set()
        for conjunctive_expression in conjunctive_exp_lst:
            fields_filter_dict = defaultdict(list)
            for exp in conjunctive_expression:
                if exp[0] is '~':
                    cond = symbol_exp_dict[exp[1]]
                    field = cond[0]
                    #new_cond = {'field': field.split('.')[-1], 'operator': cond[1], 'value': cond[2], 'negation': True,'symbol': exp}
                    new_cond = {'operator': cond[1], 'value': cond[2], 'negation': True, 'symbol': exp}
                    fields_filter_dict[field].append(new_cond)
                else:
                    cond = symbol_exp_dict[exp]
                    field = cond[0]
                    #new_cond = {'field': field.split('.')[-1], 'operator': cond[1], 'value': cond[2], 'negation': False, 'symbol': exp}
                    new_cond = {'operator': cond[1], 'value': cond[2], 'negation': False, 'symbol': exp}
                    fields_filter_dict[field].append(new_cond)
            field_filters = fields_filter_dict.items()
            field_filters = sorted(field_filters, key=lambda f: len(f[0].split('.')))
            filter_ast = FilterAST('root')
            # filter_ast.add_child_edge('filter')
            for field_filter in field_filters:
                fields = field_filter[0].split('.')
                root_type = entry
                ast = filter_ast
                for f in fields:
                    if f not in filter_ast.children_edges:
                        name = filter_fields_map[(root_type, f)]
                        if name not in ['String']:
                            new_child = ast.add_child(name, f)
                            ast = new_child
                        else:
                            ast.add_attribute_filter(f, field_filter[1])
                    else:
                        temp = ast.getSubTree(f)
                        ast = ast.getSubTree(f)
                    root_type = filter_fields_map[(root_type, f)]
            filter_ASTs.append(filter_ast)
            prefix = filter_ast.getPrefixExps()
            common_prefix -= frozenset(prefix)
            all_exp = filter_ast.getAllExps()
            repeated_single_exp = set.union(repeated_single_exp, all_ast_exp.intersection(all_exp))
            all_ast_exp = set.union(all_ast_exp, all_exp)
        return filter_ASTs, common_prefix, repeated_single_exp

    def newFilter(self, super_filters, current_filter):
        print(super_filters)
        super_filters.update(current_filter)
        return super_filters

    def getCache(self, filter_exp):
        return

    def localize(self, pred_attr, filter_fields = None, query_fields = None):
        if len(filter_fields) == 0:
            #print('pred_attr', pred_attr)
            query_fields = []
            return
        else:
            localized_filter_fields = defaultdict(dict)
            #print('attr_pred', attr_pred)
            #print('filter_fields', filter_fields)
            for key, value in filter_fields.items():
                localized_filter_fields[key]['local_name'] = pred_attr[key]
                localized_filter_fields[key]['filter'] = value
            return localized_filter_fields

    def data_fetcher(self, type, filter_fields, super_mappings_name):
        result = defaultdict()
        if len(super_mappings_name) == 0:
            mappings = self.getMappings(type)
            #print('mappings',mappings)
        else:
            mappings = []
        query_fields = filter_fields.keys()
        predicates = self.Translate(query_fields)
        for mapping in mappings:
            mapping_name = mapping['name']
            logical_source = self.getLogicalSource(mapping)
            template = self.getTemplate(mapping)
            #may change if multiple key attributes
            key_attrs = [self.parseTemplate(template)[0]]
            poms = self.getPredicateObjectMap(mapping, predicates)
            pred_attr = dict()
            for pom in poms:
                predicate, object_map = self.parsePOM(pom)
                if self.TypeOfObjectMap(object_map) == 1:
                    reference_attribute = self.getReference(object_map)
                    pred_attr[self.Phi(predicate)] = reference_attribute
                    #attr_pred.append((referenceAttribute, self.Phi(predicate)))
                if self.TypeOfObjectMap(object_map) == 2:
                    print('Constant')
            localized_filter = self.localize(pred_attr, filter_fields, query_fields)
            temp_result = pd.json_normalize(self.Executor(logical_source, key_attrs, True, localized_filter))
            #temp_result = self.refine(temp_result, pred_attr, None, template)
            temp_result = self.RefineDataFrame(temp_result, pred_attr, None, template)
            result[mapping_name] = temp_result
        return result

    def checkCPE(self, filter, CPE):
        exp_symbols = set()
        if len(filter) >0:
            for key, value in filter.items():
                for exp in value:
                    exp_symbols.add(exp['symbol'])
            if exp_symbols in CPE:
                return True
            else:
                return False
        else:
            return False

    def checkRSE(self, filter, RSE):
        exp_symbols = set()
        if len(filter) > 0:
            for key, value in filter.items():
                for exp in value:
                    exp_symbols.add(exp['symbol'])
            return
        else:
            return False

    def FilterEvaluator(self, filter_AST, CPE, RSE, super_filters ={}, super_result=None):
        root_node_filter = filter_AST.getCurrentFilter()
        #print('root_filter', root_node_filter)
        if len(root_node_filter) == 0:
            root_node_filter = {filter_AST.name + '-ALL':{}}
        new_filter = self.newFilter(super_filters, root_node_filter)
        joined_result = self.getCache(new_filter)
        if joined_result is None:
            temp_result = self.getCache(root_node_filter)
            if temp_result is None:
                type = filter_AST.name
                filter_fields = filter_AST.filter_dict
                #print('type', type)
                #print('filter_fields', filter_fields)
                super_mappings_name = []
                temp_result = self.data_fetcher(type, filter_fields, super_mappings_name)
                if self.checkRSE(root_node_filter, RSE) == True:
                    self.cache[root_node_filter] = temp_result
            super_node_type = filter_AST.parent.name
            current_node_type = filter_AST.name
            super_field = filter_AST.parent_edge
            #print('tempResult here', current_node_type)
            if super_field != 'filter':
                print('Join here')
                super_result = self.Join(super_result, temp_result, super_node_type, current_node_type, super_field)
            else:
                super_result = temp_result
            if self.checkCPE(new_filter, CPE) == True:
                self.cache[new_filter] = super_result

        else:
            super_result = joined_result
        sub_filter_ASTs = filter_AST.getSubTrees()
        for ast in sub_filter_ASTs:
            self.FilterEvaluator(ast, CPE, RSE, new_filter, super_result)
        return super_result

    def Join(self, super_result, current_node_result, super_node_type, current_node_type, super_field):
        super_mappings = self.getMappings(super_node_type)
        predicates = self.Translate([super_field])
        for mapping in super_mappings:
            poms = self.getPredicateObjectMap(mapping, predicates)
            for pom in poms:
                predicate, object_map = self.parsePOM(pom)
                if self.TypeOfObjectMap(object_map) == 3:
                    parent_mapping, join_condition = self.parseROM(object_map)
                    child_field, parent_field = self.parseJoinCondition(join_condition)
                    right_df = current_node_result[parent_mapping['name']].drop(['iri'], axis=1)
                    for key in super_result.keys():
                        if child_field in list(super_result[key].columns):
                            super_result[key] = right_df.join(super_result[key].set_index([child_field], verify_integrity = True), on= [parent_field], how='left')
        return super_result

    def InnerJoin(self):
        return

    def QueryEvaluator(self, AST, mapping = None, ref= None, root_type = False):
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
            key_attr = self.parseTemplate(template)[0]
            tempResult = self.Executor(logicalSource, None, False, None, ref)
            poms = self.getPredicateObjectMap(mapping, predicates)
            attr_pred, result2join, constant = [], [], []
            ref_poms_pred_object_map = []
            for pom in poms:
                predicate, objectMap = self.parsePOM(pom)
                if self.TypeOfObjectMap(objectMap) == 1:
                    referenceAttribute = self.getReference(objectMap)
                    attr_pred.append((referenceAttribute, self.Phi(predicate)))
                if self.TypeOfObjectMap(objectMap) == 2:
                    print('Constant')
                if self.TypeOfObjectMap(objectMap) == 3:
                    ref_poms_pred_object_map.append((predicate, objectMap))

            if root_type is True:
                tempResult = self.RefineJSON(tempResult, attr_pred, constant, template, True, mapping['name'])
            else:
                tempResult = self.RefineJSON(tempResult, attr_pred, constant, template)

            for (predicate, objectMap) in ref_poms_pred_object_map:
                newAST = self.getSubAST(AST, self.Phi(predicate))
                parentMapping, joinCondition = self.parseROM(objectMap)
                childField, parentField = self.parseJoinCondition(joinCondition)
                childData = self.getChildData(tempResult, childField)
                ref = (childData, joinCondition)
                parentData = self.QueryEvaluator(newAST, parentMapping, ref)
                result2join.append((parentData, joinCondition, self.Phi(predicate), newAST))
            tempResult = self.IncrementalJoin(tempResult, result2join)
            result = self.Merge(result, tempResult)
        return self.DuplicateDetectionFusion(result)

    def filter(self, tempresult):
        return
