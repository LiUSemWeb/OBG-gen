import requests
import csv
import codecs
from contextlib import closing
from generic_resolver.mapping_utils import RML_Mapping
from graphql import parse
import json
import pymongo
from collections import defaultdict
import pandas as pd
from generic_resolver.filter_ast import Filter_AST
import ast
import copy
import datetime



class Resolver_Utils(object):
    def __init__(self, mapping_file, o2graphql_file='o2graphql.json'):
        self.mu = RML_Mapping(mapping_file)
        # self.operator_1 = ['_and', '_or', '_not']
        # self.operator_2 = ['_eq', '_neq', '_gt']
        self.field_exp_symbol = dict()
        self.symbol_field_exp = dict()
        self.schema_ast = dict()
        self.cache = dict()
        self.join_cache = dict()
        self.single_cache = dict()
        self.common_exp_symbols = []
        self.filter_fields_map = dict()
        self.mapping_attr_pred_dict = defaultdict(dict)
        self.filtered_object_iri = dict()
        self.filter_access_data_time = datetime.timedelta()
        self.query_access_data_time = datetime.timedelta()
        self.join_time = datetime.timedelta()
        with open(o2graphql_file) as f:
            # Update may needs here for translate
            self.ontology2GraphQL_schema = json.load(f)
            self.GraphQL_schema2ontology = self.ontology2GraphQL_schema

    def set_symbol_field_maps(self, field_exp_symbol, symbol_field_exp):
        self.field_exp_symbol = field_exp_symbol
        self.symbol_field_exp = symbol_field_exp

    def getJSONData(self, url, iterator=None, ref=None):
        start_time = datetime.datetime.now()
        r = requests.get(url=url)
        end_time = datetime.datetime.now()
        #print('Access data source time after filter', (end_time - start_time))
        self.query_access_data_time += end_time-start_time
        data = r.json()
        if iterator is not None:
            keys = self.parse_iterator(iterator)
            temp_data = data
            for i in range(len(keys)):
                temp_data = temp_data[keys[i]]
            return temp_data
        else:
            return data

    @staticmethod
    def getCSVData(url, ref=None):
        ref_condition, ref_data = [], []
        if ref is not None:
            ref_condition = ref[1]
            ref_data = [record[ref_condition['child']] for record in ref[0]]
        records = []
        result = []
        with closing(requests.get(url, stream=True)) as r:
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

    def getMongoDBData(self, server_info, query, iterator=None, ref=None):
        result = []
        parameters = query.split(';')
        mongodb_client_address = server_info['server']
        database = parameters[2]
        collection_name = parameters[1]
        projection = ast.literal_eval(parameters[0])
        dbclient = pymongo.MongoClient(mongodb_client_address)
        mongodb = dbclient[database]
        mongodb_collection = mongodb[collection_name]
        if ref is None:
            result = list(mongodb_collection.find({}, projection))
            temp_data = result[0]
            keys = self.parse_iterator(iterator)
            for i in range(len(keys)):
                temp_data = temp_data[keys[i]]
            result = temp_data
        return result

    def get_json_data(self, url, iterator, key_attrs, filter_dict=None, constant_data=None, filter_lst_obj_tag=False):
        #filter_lst_obj_tag = False
        group_by_attrs = copy.copy(key_attrs)
        start_time = datetime.datetime.now()
        r = requests.get(url=url)
        end_time = datetime.datetime.now()
        #print('Access data source time for filter', (end_time - start_time))
        self.filter_access_data_time += end_time - start_time
        if filter_dict is not None:
            for key, value in filter_dict.items():
                if value['local_name'] not in key_attrs:
                    key_attrs.append(value['local_name'])
        data = r.json()
        temp_data = data
        if iterator is not None:
            keys = self.parse_iterator(iterator)
            for i in range(len(keys)):
                temp_data = temp_data[keys[i]]
        result = []
        for data_record in temp_data:
            temp_dict = dict()
            for k, v in data_record.items():
                if k in key_attrs:
                    temp_dict[k] = v
            result.append(temp_dict)
        result = pd.json_normalize(result)
        if len(constant_data) >0:
            for (constant_pred, data, data_type) in constant_data:
                kwargs = {constant_pred: data}
                result = result.assign(**kwargs)
        #print('list_obj_flag', filter_lst_obj_tag)
        if filter_dict is not None:
            if filter_lst_obj_tag is False:
                # print('filter')
                # print('shape', result.shape[0])
                result = self.filter_data_frame(result, filter_dict)
                # print(result)
                # print('shape', result.shape[0])
                return result
            else:
                temp_result = self.filter_data_frame_group_by(result, filter_dict, group_by_attrs)
                return temp_result
        else:
            return result

    @staticmethod
    def transform_operator(operator, negation_flag=False):
        if operator == '_eq':
            return '==' if not negation_flag else '!='
        elif operator == '_gt':
            return '>' if not negation_flag else '<='
        elif operator == '_lt':
            return '<' if not negation_flag else '>='
        elif operator == '_in':
            return 'in' if not negation_flag else ' not in'
        elif operator == '_like':
            return 'like'
        elif operator == '_ilike':
            return 'ilike'
        else:
            return operator

    @staticmethod
    def transform_lambda_func(column_name, operator, value, negation_flag=False):
        if operator == '_eq':
            return lambda x: x[column_name].eq(value).any() if not negation_flag else lambda x: x[column_name].ne(value).any()
        elif operator == '_gt':
            return lambda x: x[column_name].gt(value).any() if not negation_flag else lambda x: x[column_name].le(value).any()
        elif operator == '_lt':
            return lambda x: x[column_name].lt(value).any() if not negation_flag else lambda x: x[column_name].ge(value).any()
        elif operator == '_in':
            return lambda x: x[column_name].isin(value).any() if not negation_flag else lambda x: ~x[column_name].isin(value).any()
        else:
            return None

    @staticmethod
    def convert_data_type(column_name, old_type):
        convert_type_dict = dict()
        if old_type == 'String':
            convert_type_dict = {column_name: 'str'}
        if old_type == 'Int':
            convert_type_dict = {column_name: 'int64'}
        if old_type == 'Float':
            convert_type_dict = {column_name: 'float64'}
        return convert_type_dict

    def filter_data_frame(self, df, filter_dict):
        # print('FILTER DICT')
        # print(filter_dict)
        for pred, filter_dict_value in filter_dict.items():
            local_name = filter_dict_value['local_name']
            attr_type = filter_dict_value['attribute_type']
            for atom_filter in filter_dict_value['filter']:
                filter_str = self.generate_filter_str(local_name, df.dtypes[local_name], atom_filter['operator'],
                                                      atom_filter['value'], atom_filter['negation'], attr_type)
                df = df.query(filter_str)
        return df

    def filter_data_frame_group_by(self, df, filter_dict, key_attrs):
        for pred, filter_dict_value in filter_dict.items():
            local_name = filter_dict_value['local_name']
            attr_type = filter_dict_value['attribute_type']
            for atom_filter in filter_dict_value['filter']:
                # filter_str = self.generate_filter_str(local_name, df.dtypes[local_name], atom_filter['operator'],atom_filter['value'], atom_filter['negation'], attr_type)
                filter_lambda_func = self.generate_filter_lambda_func(local_name, df.dtypes[local_name], atom_filter['operator'],atom_filter['value'], atom_filter['negation'], attr_type)
                df = df.groupby(key_attrs).filter(filter_lambda_func)
        return df

    def generate_filter_lambda_func(self, attribute_name, column_type, operator_str, value_str, negation_flag, attr_type):
        graphql_df_operator_map = {}
        filter_str = ''
        lambda_func = None
        if operator_str in ['_in', '_nin']:
            # new_value = ast.literal_eval(value)
            if column_type == 'int64':
                new_value = ast.literal_eval(value_str)
                new_value = [int(x) for x in new_value if x.isnumeric() is True]
                lambda_func = self.transform_lambda_func(attribute_name, operator_str, new_value, negation_flag)
            else:
                new_value = ast.literal_eval(value_str)
                lambda_func = self.transform_lambda_func(attribute_name, operator_str, new_value, negation_flag)
        else:
            if attr_type == 'String' or 'ID':
                if column_type == 'int64':
                    new_value = int(value_str)
                    lambda_func = self.transform_lambda_func(attribute_name, operator_str, new_value, negation_flag)
                else:
                    new_value = str(value_str)
                    lambda_func = self.transform_lambda_func(attribute_name, operator_str, new_value, negation_flag)
            if attr_type == 'Int':
                new_value = int(value_str)
                lambda_func = self.transform_lambda_func(attribute_name, operator_str, new_value, negation_flag)
            if attr_type == 'Float':
                new_value = float(value_str)
                lambda_func = self.transform_lambda_func(attribute_name, operator_str, new_value, negation_flag)
        return lambda_func

    def generate_filter_str(self, attribute_name, column_type, operator_str, value_str, negation_flag, attr_type):
        filter_str = ''
        new_operator = self.transform_operator(operator_str, negation_flag)
        if operator_str in ['_in', '_nin']:
            # new_value = ast.literal_eval(value)
            if column_type == 'int64':
                new_value = ast.literal_eval(value_str)
                new_value = [int(x) for x in new_value if x.isnumeric() is True]
                filter_str = "{column} {operator} {value} ".format(column=attribute_name, operator=new_operator,
                                                                   value=new_value)
            else:
                filter_str = "{column} {operator} {value} ".format(column=attribute_name, operator=new_operator,
                                                                   value=value_str)
        else:
            if attr_type == 'String' or 'ID':
                if column_type == 'int64':
                    new_value = int(value_str)
                    filter_str = "{column} {operator} {value} ".format(column=attribute_name, operator=new_operator,
                                                                       value=new_value)
                else:
                    new_value = str(value_str)
                    filter_str = "{column} {operator} \"{value}\" ".format(column=attribute_name, operator=new_operator,
                                                                           value=new_value)
            if attr_type == 'Int':
                new_value = int(value_str)
                filter_str = "{column} {operator} {value} ".format(column=attribute_name, operator=new_operator,
                                                                   value=new_value)
            if attr_type == 'Float':
                new_value = float(value_str)
                filter_str = "{column} {operator} {value} ".format(column=attribute_name, operator=new_operator,
                                                                   value=new_value)
        return filter_str

    @staticmethod
    def parse_ast(query_ast):
        entity_type = query_ast['type']
        query_fields = []
        for field in query_ast['fields']:
            query_fields.append(field['name'])
        return entity_type, query_fields

    @staticmethod
    def get_sub_ast(query_ast, predicate):
        fields = query_ast['fields']
        new_ast = None
        for field in fields:
            if field['name'] == predicate:
                new_ast = field
                break
        return new_ast

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

    def generate_schema_ast(self, schema):
        if len(self.schema_ast) == 0:
            schema_ast = dict()
            document = parse(schema)
            for definition in document.definitions:
                if definition.kind == 'object_type_definition':
                    schema_ast[definition.name.value] = dict()
                    for wrapped_field in definition.fields:
                        named_type_value, encode_labels = self.parse_field(wrapped_field)
                        if definition.name.value == 'Query':
                            # filter_type = self.parse_query_qrguments(wrapped_field.arguments)
                            self.filter_fields_map[(wrapped_field.name.value, 'filter')] = (named_type_value, encode_labels)
                        else:
                            self.filter_fields_map[(definition.name.value, wrapped_field.name.value)] = (named_type_value, encode_labels)
                        schema_ast[definition.name.value][wrapped_field.name.value] = {'base_type': named_type_value,
                                                                                       'wrapping_label': encode_labels}
                if definition.kind == 'input_object_type_definition':
                    schema_ast[definition.name.value] = dict()
                    for wrapped_field in definition.fields:
                        named_type_value, encode_labels = self.parse_field(wrapped_field)
                        schema_ast[definition.name.value][wrapped_field.name.value] = {'base_type': named_type_value,
                                                                                       'wrapping_label': encode_labels}
            self.schema_ast = schema_ast
            return self.schema_ast
        else:
            return self.schema_ast

    def get_query_entries(self, schema):
        schema_ast = self.generate_schema_ast(schema)
        query_entries = list(schema_ast['Query'].keys())
        return query_entries

    def fill_return_type(self, query_ast, schema_ast, super_type):
        if len(query_ast['fields']) > 0:
            temp_fields = []
            for sub_ast in query_ast['fields']:
                sub_ast['type'] = schema_ast[super_type][sub_ast['name']]['base_type']
                sub_ast['wrapping_label'] = schema_ast[super_type][sub_ast['name']]['wrapping_label']
                new_sub_ast = self.fill_return_type(sub_ast, schema_ast, sub_ast['type'])
                temp_fields.append(new_sub_ast)
            query_ast['fields'] = temp_fields
        return query_ast

    def generate_query_ast(self, schema, query_info):
        schema_ast = self.generate_schema_ast(schema)
        self.schema_ast = schema_ast
        query_field_nodes = query_info.field_nodes
        query_ast = self.parse_query_fields('Query', query_field_nodes)
        query_entry_name = query_ast['fields'][0]['name']
        query_ast['fields'][0]['type'] = schema_ast['Query'][query_entry_name]['base_type']
        query_ast['fields'][0]['wrapping_label'] = schema_ast['Query'][query_entry_name]['wrapping_label']
        # query_ast is changed inside fill_return_type
        self.fill_return_type(query_ast['fields'][0], schema_ast, query_ast['fields'][0]['type'])
        return query_ast

    def get_mappings(self, concept_type):
        return self.mu.get_mappings_by_type(concept_type)

    def get_mappings_by_names(self, mappings_name=[]):
        return self.mu.get_mappings_by_names(mappings_name)

    def get_logical_source(self, mapping):
        return self.mu.get_logical_source_by_mapping(mapping)

    def get_template(self, mapping):
        return self.mu.get_subject_template_by_mapping(mapping)

    def get_predicate_object_maps(self, mapping, predicates):
        return self.mu.get_pom_by_predicates(mapping, predicates)

    def get_constant_value(self, object_map):
        return self.mu.get_constant_value_type(object_map)

    def get_reference_attribute(self, term_map):
        return self.mu.get_reference(term_map)

    @staticmethod
    def get_child_data(temp_result, child_field):
        return [{child_field: record[child_field]} for record in temp_result]

    @staticmethod
    def parse_iterator(iterator):
        iterator_elements = iterator.split('.')
        iterator_elements = list(filter(None, iterator_elements))
        return iterator_elements

    def parse_pom(self, pom):
        return self.mu.parse_pom(pom)

    def parse_rom(self, object_map):
        return self.mu.parse_rom(object_map)

    def phi(self, ontology_term):
        return self.ontology2GraphQL_schema[ontology_term]

    def inverse_phi(self, graphql_term):
        return self.GraphQL_schema2ontology[graphql_term]

    def translate(self, query_fields):
        predicates = []
        for field in query_fields:
            predicates.append(self.inverse_phi(field))
        return predicates

    @staticmethod
    def parse_template(template):
        start_pos = template.index('{')
        end_pos = template.index('}')
        key = template[start_pos + 1: end_pos]
        new_template = template.replace(key, '')
        return key, new_template

    def parse_join_condition(self, join_condition):
        return self.mu.parse_join_condition(join_condition)

    # need to optimize
    def refine_json(self, temp_result, attr_pred_lst, constant, template, root_type_flag=False, mapping_name='', key_attributes= []):
        key, template = self.parse_template(template)
        i = 0
        while i < len(temp_result):
            temp_result[i] ={k: v for k, v in temp_result[i].items() if k in key_attributes}
            for (constant_pred, constant_data, data_type) in constant:
                temp_result[i][constant_pred] = constant_data
            iri = template.format(temp_result[i][key])
            if root_type_flag is True:
                if mapping_name in self.filtered_object_iri.keys() and iri in self.filtered_object_iri[mapping_name] or \
                        self.filtered_object_iri['filter'] is False:
                    temp_result[i]['iri'] = iri
                    for attr_pred_tuple in attr_pred_lst:
                        if '.' in attr_pred_tuple[0]:
                            keys = self.parse_iterator(attr_pred_tuple[0])
                            temp_data = temp_result[i]
                            for i in range(len(keys)):
                                temp_data = temp_data[keys[i]]
                                temp_result[i][attr_pred_tuple[1]] = temp_data
                        else:
                            if attr_pred_tuple[0] in temp_result[i].keys():
                                # record[attr_pred_tuple[1]] = record.pop(attr_pred_tuple[0])
                                temp_result[i][attr_pred_tuple[1]] = temp_result[i][attr_pred_tuple[0]]
                    i += 1
                else:
                    del temp_result[i]
            else:
                temp_result[i]['iri'] = iri
                for attr_pred_tuple in attr_pred_lst:
                    if '.' in attr_pred_tuple[0]:
                        keys = self.parse_iterator(attr_pred_tuple[0])
                        temp_data = temp_result[i]
                        for i in range(len(keys)):
                            temp_data = temp_data[keys[i]]
                            temp_result[i][attr_pred_tuple[1]] = temp_data
                    else:
                        if attr_pred_tuple[0] in temp_result[i].keys():
                            # record[attr_pred_tuple[1]] = record.pop(attr_pred_tuple[0])
                            temp_result[i][attr_pred_tuple[1]] = temp_result[i][attr_pred_tuple[0]]
                i += 1
        '''
        for record in temp_result:
            record['iri'] = template.format(record[key])
            for attr_pred_tuple in attr_pred_lst:
                if '.' in attr_pred_tuple[0]:
                    keys = self.parse_iterator(attr_pred_tuple[0])
                    temp_data = record
                    for i in range(len(keys)):
                        temp_data = temp_data[keys[i]]
                    record[attr_pred_tuple[1]] = temp_data
                else:
                    if attr_pred_tuple[0] in record.keys():
                        #record[attr_pred_tuple[1]] = record.pop(attr_pred_tuple[0])
                        record[attr_pred_tuple[1]] = record[attr_pred_tuple[0]]
        
        '''
        return temp_result

    @staticmethod
    def merge(result, temp_result):
        return result + temp_result

    @staticmethod
    def duplicate_detection_fusion(result):
        return result

    def type_of_object_map(self, object_map):
        return self.mu.type_of_object_map(object_map)

    @staticmethod
    def check_node_type(node):
        if node.kind == 'non_null_type':
            return 'non_null_type'
        if node.kind == 'named_type':
            return 'named_type'
        if node.kind == 'list_type':
            return 'list_type'
        return 0

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

    def get_source_type(self, logical_source):
        return self.mu.get_logical_source_type(logical_source)

    def get_source_request(self, logical_source):
        return self.mu.get_source(logical_source)

    def get_json_iterator(self, logical_source):
        return self.mu.get_json_iterator(logical_source)

    def get_db_source(self, logical_source):
        return self.mu.get_db_source(logical_source)

    def executor(self, logical_source, key_attrs, filter_flag=False, filter_dict=None, ref=None, constant_data=None, filter_lst_obj_tag=False):
        source_type = self.get_source_type(logical_source)
        result = []
        if source_type == 'ql:CSV':
            source_request = self.get_source_request(logical_source)
            # result = self.getCSVData(source_request, ref)
        if source_type == 'ql:JSONPath':
            source_request = self.get_source_request(logical_source)
            iterator = self.get_json_iterator(logical_source)
            # result = self.getJSONData(source_request, iterator, ref)
            if filter_flag is True:
                # data frame here
                #print('print my dilter_dict', filter_dict)
                result = self.get_json_data(source_request, iterator, key_attrs, filter_dict, constant_data, filter_lst_obj_tag)
            else:
                result = self.getJSONData(source_request, iterator, ref)
        if source_type == 'mydb:mongodb':
            iterator = self.get_json_iterator(logical_source)
            server_info, query = self.get_db_source(logical_source)
            result = self.getMongoDBData(server_info, query, iterator)
        return result

    def refine_data_frame(self, df, pred_attr_dict, constant, template, mapping_name):
        key, template = self.parse_template(template)
        new_column_name = mapping_name + '-' + key
        df[new_column_name] = df[key]
        df = df.assign(iri=[template.format(x) for x in df[key]])
        for pred, attr in pred_attr_dict.items():
            if attr in list(df.columns):
                if pred != attr:
                    kwargs = {pred: lambda x: x[attr]}
                    df = df.assign(**kwargs)
        df = df.drop([key], axis=1)
        return df

    @staticmethod
    def generate_filter_asts(filter_fields_map, symbol_exp_dict, conjunctive_exp_lst, entry='CalculationList'):
        filter_asts = []
        common_prefix = set()
        prefix_dict = defaultdict(int)
        single_exp_dict = defaultdict(int)
        repeated_single_exp = set()
        for conjunctive_expression in conjunctive_exp_lst:
            fields_filter_dict = defaultdict(list)
            for exp in conjunctive_expression:
                if exp[0] == '~':
                    cond = symbol_exp_dict[exp[1]]
                    field = cond[0]
                    new_cond = {'operator': cond[1], 'value': cond[2], 'negation': True, 'symbol': exp}
                    fields_filter_dict[field].append(new_cond)
                else:
                    cond = symbol_exp_dict[exp]
                    field = cond[0]
                    new_cond = {'operator': cond[1], 'value': cond[2], 'negation': False, 'symbol': exp}
                    fields_filter_dict[field].append(new_cond)
            field_filters = fields_filter_dict.items()
            field_filters = sorted(field_filters, key=lambda x: len(x[0].split('.')))
            filter_ast = Filter_AST('root')
            # filter_ast.add_child_edge('filter')
            for field_filter in field_filters:
                fields = field_filter[0].split('.')
                root_type = entry
                temp_ast = filter_ast
                for f in fields:
                    if f not in temp_ast.children_edges:
                        name = filter_fields_map[(root_type, f)][0]
                        list_obj_tag = filter_fields_map[(root_type, f)][1]
                        if name not in ['String', 'Int', 'Boolean', 'ID', 'Float']:
                            new_child = temp_ast.add_child(name, f, list_obj_tag)
                            temp_ast = new_child
                        else:
                            temp_ast.add_attribute_filter(f, field_filter[1], name)
                    else:
                        temp_ast = temp_ast.get_sub_tree_by_edge(f)
                    root_type = filter_fields_map[(root_type, f)][0]
            filter_asts.append(filter_ast)
            prefix = filter_ast.get_prefix_expressions()
            prefix_dict[tuple(sorted(prefix))] += 1
            all_exp = filter_ast.get_all_expression()
            for exp in all_exp:
                key = []
                key.append(exp)
                single_exp_dict[tuple(sorted(key))] += 1
        for key, value in prefix_dict.items():
            if value > 1:
                common_prefix.add(key)
        for key, value in single_exp_dict.items():
            if value > 1:
                repeated_single_exp.add(key)
        return filter_asts, common_prefix, repeated_single_exp

    @staticmethod
    def new_filter(super_filters, current_filter):
        super_filters.update(current_filter)
        return super_filters

    def get_cache(self, symbolic_filter):
        if symbolic_filter in self.cache.keys():
            return self.cache[symbolic_filter]
        else:
            return None

    def get_join_cache(self, symbolic_filter):
        if symbolic_filter in self.join_cache.keys():
            return self.join_cache[symbolic_filter]
        else:
            return None

    def get_single_cache(self, symbolic_filter):
        if symbolic_filter in self.single_cache.keys():
            return self.single_cache[symbolic_filter]
        else:
            return None

    def localize_filter(self, entity_type, pred_attr, filter_fields=None, query_fields=None, filter_constant_field=None):
        if len(filter_fields) == 0:
            return
        else:
            localized_filter_fields = defaultdict(dict)
            for key, value in filter_fields.items():
                if key in pred_attr.keys():
                    localized_filter_fields[key]['local_name'] = pred_attr[key]
                    localized_filter_fields[key]['attribute_type'] = self.schema_ast[entity_type][key]['base_type']
                    localized_filter_fields[key]['filter'] = value
                else:
                    if len(filter_constant_field) >0:
                        localized_filter_fields[key]['local_name'] = key
                        localized_filter_fields[key]['attribute_type'] = self.schema_ast[entity_type][key]['base_type']
                        localized_filter_fields[key]['filter'] = value
            return localized_filter_fields

    def filter_data_fetcher(self, entity_type, filter_fields, super_mappings_name, filter_lst_obj_tag=False):
        result = defaultdict()
        if len(super_mappings_name) == 0:
            mappings = self.get_mappings(entity_type)
        else:
            mappings = []
        query_fields = filter_fields.keys()
        predicates = self.translate(query_fields)
        for mapping in mappings:
            mapping_name = mapping['name']
            logical_source = self.get_logical_source(mapping)
            template = self.get_template(mapping)
            # may change if multiple key attributes
            key_attrs = [self.parse_template(template)[0]]
            poms = self.get_predicate_object_maps(mapping, predicates)
            pred_attr = dict()
            constant_data =[]
            filter_constant = []
            for pom in poms:
                predicate, object_map = self.parse_pom(pom)
                if self.type_of_object_map(object_map) == 1:
                    reference_attribute = self.get_reference_attribute(object_map)
                    pred_attr[self.phi(predicate)] = reference_attribute
                    # attr_pred.append((referenceAttribute, self.phi(predicate)))

                if self.type_of_object_map(object_map) == 2:
                    constant_value, constant_datatype = self.get_constant_value(object_map)
                    constant_data.append((predicate, constant_value, constant_datatype))
                    filter_constant.append(predicate)
            localized_filter = self.localize_filter(entity_type, pred_attr, filter_fields, query_fields, filter_constant)
            temp_result = self.executor(logical_source, key_attrs, True, localized_filter, None, constant_data, filter_lst_obj_tag)
            temp_result = self.refine_data_frame(temp_result, pred_attr, constant_data, template, mapping_name)
            if temp_result.empty is not True:
                result[mapping_name] = temp_result
        return result

    @staticmethod
    def symbolic_filter(filter_dict):
        exp = []
        for key, value in filter_dict.items():
            if len(value) == 0:
                exp.append(key)
            else:
                for atom_filter in value:
                    exp.append(atom_filter['symbol'])
        exp = tuple(sorted(exp))
        return exp

    def filter_evaluator(self, filter_ast, cpe, rse, super_filters={}, super_result=None):
        root_node_filter = filter_ast.get_current_filter()
        if len(root_node_filter) == 0:
            root_node_filter = {filter_ast.name + '-ALL': {}}
        new_filter = self.new_filter(super_filters, root_node_filter)
        symbolic_new_filter = self.symbolic_filter(new_filter)
        joined_result = self.get_join_cache(symbolic_new_filter)
        if joined_result is None or len(joined_result) == 0:
            symbolic_root_filter = self.symbolic_filter(root_node_filter)
            temp_result = self.get_single_cache(symbolic_root_filter)
            if temp_result is None or len(temp_result) == 0:
                entity_type = filter_ast.name
                filter_fields = filter_ast.filter_dict
                filter_lst_obj_tag = filter_ast.list_obj_flag
                super_mappings_name = []
                #print('filter fields', filter_fields)
                temp_result = self.filter_data_fetcher(entity_type, filter_fields, super_mappings_name, filter_lst_obj_tag)
                # print('temp_result', temp_result)
                if symbolic_root_filter in rse:
                    self.cache[symbolic_root_filter] = temp_result
            super_node_type = filter_ast.parent.name
            current_node_type = filter_ast.name
            super_field = filter_ast.parent_edge
            if super_field != 'filter':
                # print('Join here')
                super_result = self.filter_join(super_result, temp_result, super_node_type, current_node_type,
                                                super_field)
            else:
                super_result = temp_result
            # check CPE
            if symbolic_new_filter in cpe:
                print('Yes, here')
                self.cache[symbolic_new_filter] = super_result
        else:
            super_result = joined_result
        sub_filter_asts = filter_ast.get_sub_trees()
        for sub_filter_ast in sub_filter_asts:
            self.filter_evaluator(sub_filter_ast, cpe, rse, new_filter, super_result)
        return super_result


    def filter_join(self, super_result, current_node_result, super_node_type, current_node_type, super_field):
        super_mappings = self.get_mappings(super_node_type)
        predicates = self.translate([super_field])
        result2_join = []
        supper_mappings2join= []
        for mapping in super_mappings:
            poms = self.get_predicate_object_maps(mapping, predicates)
            for pom in poms:
                predicate, object_map = self.parse_pom(pom)
                if self.type_of_object_map(object_map) == 3:
                    parent_mapping, join_condition = self.parse_rom(object_map)
                    child_field, parent_field = self.parse_join_condition(join_condition)
                    if parent_mapping['name'] in current_node_result.keys():
                        result2_join.append((mapping['name'], parent_mapping['name'], child_field, parent_field))
                        supper_mappings2join.append(mapping['name'])
        # About these joins
        for mapping_key in super_result.keys():
            if mapping_key in supper_mappings2join:
                for (super_mapping_name, current_mapping_name, super_field, current_field) in result2_join:
                    if super_mapping_name == mapping_key:
                        right_df = current_node_result[current_mapping_name]
                        right_df = right_df.drop(['iri'], axis=1)
                        left_new_column_name = mapping_key + '-' + super_field
                        right_new_column_name = current_mapping_name + '-' + current_field
                        if left_new_column_name not in list(super_result[mapping_key].columns):
                            super_result[mapping_key][left_new_column_name] = super_result[mapping_key][super_field]
                        #super_result[mapping_key] = pd.merge(super_result[mapping_key], right_df, how='inner', left_on=left_new_column_name,right_on=current_field)
                        super_result[mapping_key] = pd.merge(super_result[mapping_key], right_df, how='inner',
                                                             left_on=left_new_column_name, right_on=right_new_column_name)
                        if right_new_column_name not in list(super_result[mapping_key].columns):
                            super_result[mapping_key][right_new_column_name] = super_result[mapping_key][left_new_column_name]
            else:
                for (super_mapping_name, current_mapping_name, super_field, current_field) in result2_join:
                    if super_mapping_name != mapping_key:
                        left_new_column_name = super_mapping_name + '-' + super_field
                        if left_new_column_name in super_result[mapping_key].columns.values.tolist():
                            right_df = current_node_result[current_mapping_name]
                            right_df = right_df.drop(['iri'], axis=1)
                            right_new_column_name = current_mapping_name + '-' + current_field
                            #super_result[mapping_key][left_new_column_name] = super_result[mapping_key][super_field]

                            #super_result[mapping_key] = pd.merge(super_result[mapping_key], right_df, how='inner',left_on=column_name, right_on=current_field)
                            super_result[mapping_key] = pd.merge(super_result[mapping_key], right_df, how='inner',
                                                                 left_on=left_new_column_name, right_on=right_new_column_name)
                            if right_new_column_name not in list(super_result[mapping_key].columns):
                                super_result[mapping_key][right_new_column_name] = super_result[mapping_key][left_new_column_name]
                        else:
                            # print('Join here?')
                            if len(super_result.keys()) > len(supper_mappings2join):
                                # print('Give it empty')
                                super_result[mapping_key] = super_result[mapping_key][0:0]
                    # No case for supper_mapping_name == mapping_key
        return super_result

    def query_evaluator(self, query_ast, mapping=None, ref=None, root_type_flag=False, filtered_root_mappings=[]):
        result, mappings = [], []
        concept_type, query_fields = self.parse_ast(query_ast)
        if mapping is None:
            if len(filtered_root_mappings) > 0:
                mappings = self.get_mappings_by_names(filtered_root_mappings)
            else:
                mappings = self.get_mappings(concept_type)
        else:
            mappings.append(mapping)
        predicates = self.translate(query_fields)
        for mapping in mappings:
            logical_source = self.get_logical_source(mapping)
            template = self.get_template(mapping)
            key_attrs = [self.parse_template(template)[0]]
            temp_result = self.executor(logical_source, None, False, None, ref)
            poms = self.get_predicate_object_maps(mapping, predicates)
            attr_pred, constant_data = [], []
            ref_poms_pred_object_map = []
            result_join = defaultdict(list)
            for pom in poms:
                predicate, object_map = self.parse_pom(pom)
                if self.type_of_object_map(object_map) == 1:
                    reference_attribute = self.get_reference_attribute(object_map)
                    attr_pred.append((reference_attribute, self.phi(predicate)))
                    key_attrs.append(reference_attribute)
                if self.type_of_object_map(object_map) == 2:
                    constant_value, constant_datatype = self.get_constant_value(object_map)
                    constant_data.append((predicate, constant_value, constant_datatype))
                if self.type_of_object_map(object_map) == 3:
                    ref_poms_pred_object_map.append((predicate, object_map))
            if root_type_flag is True:
                temp_result = self.refine_json(temp_result, attr_pred, constant_data, template, True, mapping['name'], key_attrs)
            else:
                temp_result = self.refine_json(temp_result, attr_pred, constant_data, template, False, '', key_attrs)
            for (predicate, object_map) in ref_poms_pred_object_map:
                new_query_ast = self.get_sub_ast(query_ast, self.phi(predicate))
                parent_mapping, join_condition = self.parse_rom(object_map)
                child_field, parent_field = self.parse_join_condition(join_condition)
                child_data = self.get_child_data(temp_result, child_field)
                ref = (child_data, join_condition)
                parent_data = self.query_evaluator(new_query_ast, parent_mapping, ref)
                # result2join.append((parent_data, join_condition, self.phi(predicate), new_query_ast))
                result_join[self.phi(predicate)].append((parent_data, join_condition, new_query_ast['wrapping_label']))
            # if len(result2join) > 0:
                # temp_result = self.old_incremental_join(temp_result, result2join)
            if len(result_join) >0:
                #print('result_join', result_join)
                #print(temp_result)
                temp_result = self.incremental_optimized_join(temp_result, result_join)
            result = self.merge(result, temp_result)
        return self.duplicate_detection_fusion(result)

    # @staticmethod
    def incremental_join(self, temp_result, result_join):
        start_time = datetime.datetime.now()
        result = []
        for pred_key, data_join_lst in result_join.items():
            for (join_data, join_condition, wrapping_label) in data_join_lst:
                for join_record in join_data:
                    for record in temp_result:
                        new_record = record
                        if pred_key not in new_record.keys() and wrapping_label != '0' and wrapping_label != '10':
                            new_record[pred_key] = []
                        if record[join_condition['child']] == join_record[join_condition['parent']]:
                            if wrapping_label == '0' or wrapping_label == '10':
                                new_record[pred_key] = join_record
                            else:
                                new_record[pred_key].append(join_record)
                            # May need to be updated
                            if new_record not in result:
                                result.append(new_record)
        end_time = datetime.datetime.now()
        self.join_time += end_time-start_time
        return result

    def incremental_optimized_join(self, temp_result, result_join):
        start_time = datetime.datetime.now()
        result = []
        for pred_key, data_join_lst in result_join.items():
            for (join_data, join_condition, wrapping_label) in data_join_lst:
                new_formed_join_data = defaultdict()
                for record in join_data:
                    # print(record[join_condition['parent']])
                    new_formed_join_data[record[join_condition['parent']]] = record
                for record in temp_result:
                    new_record = record
                    join_key_value = record[join_condition['child']]
                    if pred_key not in new_record.keys() and wrapping_label != '0' and wrapping_label != '10':
                        new_record[pred_key] = []
                    if wrapping_label == '0' or wrapping_label == '10':
                        new_record[pred_key] = new_formed_join_data[join_key_value]
                    else:
                        new_record[pred_key].append(new_formed_join_data[join_key_value])
                    if new_record not in result:
                        result.append(new_record)
        end_time = datetime.datetime.now()
        self.join_time += end_time-start_time
        return result
    '''
            if len(result2join) > 0:
            for (join_data, join_condition, field, schema_ast) in result2join:
                for join_record in join_data:
                    for record in temp_result:
                        if record[join_condition['child']] == join_record[join_condition['parent']]:
                            new_record = record
                            if schema_ast['wrapping_label'] == '0' or schema_ast['wrapping_label'] == '10':
                                new_record[field] = join_record
                            else:
                                new_record[field] = [join_record]
                            result.append(new_record)
    '''

'''
@staticmethod
    def old_incremental_join(temp_result, result2join):
        result = []
        if len(result2join) > 0:
            for (join_data, join_condition, field, schema_ast) in result2join:
                for join_record in join_data:
                    for record in temp_result:
                        if record[join_condition['child']] == join_record[join_condition['parent']]:
                            new_record = record
                            if schema_ast['wrapping_label'] == '0' or schema_ast['wrapping_label'] == '10':
                                new_record[field] = join_record
                            else:
                                new_record[field] = [join_record]
                            result.append(new_record)
            return result
        else:
            return temp_result
'''