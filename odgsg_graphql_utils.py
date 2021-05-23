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


class AST(object):
    def __init__(self, name, children = None, parent = None, parent_edge = None, filter_lst = None):
        #data in the form of list of (field name: symbol (with negation or not))
        self.name = name
        self.children = children or []
        self.parent = parent
        self.parent_edge = parent_edge
        self.children_edges = []
        self.filter_lst = filter_lst or {}

    def add_child(self, child_name, edge):
        new_child = AST(child_name, parent=self, parent_edge=edge)
        self.children.append(new_child)
        self.children_edges.append(edge)
        return new_child

    def add_child_edge(self, child_edge):
        self.children_edges.append(child_edge)

    def add_attribute_filter(self, attr_symbol, filter_lst):
        self.filter_lst[attr_symbol] = filter_lst

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
        if len(self.filter_lst) > 0:
            return self.filter_lst
        else:
            return None
    def getCurrentExpSymbols(self):
        exp_symbols = set()
        current_filter = self.getCurrentFilter()
        if current_filter is not None:
            for key, value in current_filter.items():
                for exp in value:
                    exp_symbols.add(exp['symbol'])
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
        self.field_exp_symbol = dict()
        self.symbol_field_exp = dict()
        self.schemaAST = dict()
        self.intermediate_store = dict()
        self.common_exp_symbols = []
        self.filter_fields_map = dict()

    def set_symbol_field_maps(self, field_exp_symbol, symbol_field_exp):
        self.field_exp_symbol = field_exp_symbol
        self.symbol_field_exp = symbol_field_exp
        #print(self.field_exp_symbol)
        #print(self.symbol_field_exp)

    '''
    def set_common_exp_symbols(self, common_exp_symbols):
        self.common_exp_symbols = list(common_exp_symbols)
    '''

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
                    current_filter_dict.append({'field': cond[0], 'operator': cond[1], 'value': cond[2], 'negation': True})
                    if field_seq[-1] not in filter_fields:
                        filter_fields.append(field_seq[-1])
                else:
                    new_conjunctive_expression.append(symbol)
                    sub_filter.append(('not',cond))
                    sub_filter_dict.append({'field': cond[0], 'operator': cond[1], 'value': cond[2], 'negation': True})
            else:
                cond = self.symbol_field_exp[symbol]
                field_seq = cond[0].split('.')
                if len(field_seq) is level + 1:
                    current_filter.append(cond)
                    current_filter_dict.append({'field': cond[0], 'operator': cond[1], 'value': cond[2], 'negation': False})
                    if field_seq[-1] not in filter_fields:
                        filter_fields.append(field_seq[-1])
                else:
                    new_conjunctive_expression.append(symbol)
                    sub_filter.append(cond)
                    sub_filter_dict.append({'field': cond[0], 'operator': cond[1], 'value': cond[2], 'negation': False})
        print('current_filter_dict', current_filter_dict)
        print(current_filter)
        return current_filter, sub_filter, filter_fields, new_conjunctive_expression
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

    def fetcher(self, AST, conjunctive_expression = None, mapping = None, ref= None, level= 1):
        result, mappings = [], []
        concept_type, queryFields = self.parseAST(AST)
        current_filter, sub_filter, filter_fields, new_conjunctive_expression = self.get_filter_fields(conjunctive_expression, concept_type, level)
        queryFields += filter_fields
        queryFields = list(set(queryFields))
        if mapping is None:
            mappings = self.getMappings(concept_type)
        else:
            mappings.append(mapping)
        predicates = self.Translate(queryFields)
        #print('-----')
        print('tuple current filter', tuple(current_filter))
        #print('intermediate_Result', self.intermediate_store)
        self.intermediate_store[(('filter.ID', '_eq', '1'), ('not', ('filter.ID', '_eq', '2')))] ={'test':'test_result'}
        if tuple(current_filter) not in self.intermediate_store.keys() or len(current_filter) is 0:
            #not intermediate result
            #print()
            for mapping in mappings:
                logicalSource = self.getLogicalSource(mapping)
                template = self.getTemplate(mapping)
                tempResult = self.Execute(logicalSource, ref)
                poms = self.getPredicateObjectMap(mapping, predicates)
                attr_pred = []
                pred_attr = dict()
                referencing_poms = []
                for pom in poms:
                    predicate, objectMap = self.parsePOM(pom)
                    if self.TypeOfObjectMap(objectMap) == 1:
                        referenceAttribute = self.getReference(objectMap)
                        attr_pred.append((referenceAttribute, self.Phi(predicate)))
                        pred_attr[self.Phi(predicate)] = referenceAttribute
                    if self.TypeOfObjectMap(objectMap) == 2:
                        print('Constant')
                    if self.TypeOfObjectMap(objectMap) == 3:
                        referencing_poms.append(pom)
                localized_filter = self.localize_filter(current_filter, pred_attr)
                tempResult = self.Execute(logicalSource, ref, localized_filter)
                filter_flag = True
                if filter_flag is False:
                    print('filter by yourself')
                if current_filter in self.common_exp_symbols:
                    self.intermediate_store[current_filter].append(tempResult)
                tempResult = self.Refine(tempResult, attr_pred, None, template)
                #tempResult = self.IncrementalJoiner(referencing_poms, new_conjunctive_expression,AST, tempResult, level + 1)
        else:
            #exist intermediate result
            #tempResult = self.intermediate_store[current_filter]
            print('else current filter', current_filter)
            print('sub filter', sub_filter)
            print(queryFields)
            tempResult = []
            if len(sub_filter) >0:
                for mapping in mappings:
                    poms = self.getPredicateObjectMap(mapping, predicates)
                    referencing_poms = []
                    for pom in poms:
                        predicate, objectMap = self.parsePOM(pom)
                        if self.TypeOfObjectMap(objectMap) == 3:
                            referencing_poms.append(pom)
                    #tempResult = self.IncrementalJoin(referencing_poms, new_conjunctive_expression, AST, tempResult)
            result.append(tempResult)
        return result


    def IncrementalJoiner(self, referencingPoms, conjunctive_expression, AST, tempResult, level=1):
        for rpom in referencingPoms:
            predicate, objectMap = self.parsePOM(rpom)
            subAST = self.getSubAST(AST, self.Phi(predicate))
            subFilter = ''
            refMapping, joinCondition = self.parseROM(objectMap)
            childField, parentField = self.parseJoinCondition(joinCondition)
            childData = self.getChildData(tempResult, childField)
            ref = (childData, joinCondition)
            parentData = self.fetcher(subAST, conjunctive_expression, refMapping, ref, level)
            newFilter = ''
            if newFilter in self.intermediate_store.keys():
                #join
                self.intermediate_store[newFilter].append(tempResult)
            else:
                tempResult = self.intermediate_store[newFilter]
        return tempResult

    def FilterEvaluator(self):
        return 0
    def QueryEvaluator(self):
        return 0
    def Data_Fetcher(self):
        return 0
    def Joiner(self):
        return 0

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
                    new_cond = {'field': field.split('.')[-1], 'operator': cond[1], 'value': cond[2], 'negation': True,
                                'symbol': exp}
                    fields_filter_dict[field].append(new_cond)
                else:
                    cond = symbol_exp_dict[exp]
                    field = cond[0]
                    new_cond = {'field': field.split('.')[-1], 'operator': cond[1], 'value': cond[2], 'negation': False,
                                'symbol': exp}
                    fields_filter_dict[field].append(new_cond)
            field_filters = fields_filter_dict.items()
            # print(field_filters)
            field_filters = sorted(field_filters, key=lambda f: len(f[0].split('.')))
            filter_ast = AST('root')
            # filter_ast.add_child_edge('filter')
            for field_filter in field_filters:
                #print(field_filter)
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
