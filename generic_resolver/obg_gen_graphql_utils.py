import requests
import csv
import codecs
from contextlib import closing
from generic_resolver.mapping_utils import RML_Mapping
import json
from collections import defaultdict
import pandas as pd
import ast
import copy
from sqlalchemy import create_engine, text
import multiprocessing as mp


class Resolver_Utils(object):
    def __init__(self, mapping_file, o2graphql_file):
        self.mu = RML_Mapping(mapping_file)
        self.field_exp_symbol = dict()
        self.symbol_field_exp = dict()
        self.schema_ast = dict()
        self.join_cache = dict()
        self.single_cache = dict()
        self.filter_fields_map = dict()
        self.filtered_object_iri = dict()
        self.filtered_object_columns = defaultdict(defaultdict)
        self.sql_flag = False
        self.interfaces = []
        self.interface_query_entries = []
        with open(o2graphql_file) as f:
            # Update may needs here for translate
            self.ontology2GraphQL_schema = json.load(f)
            self.GraphQL_schema2ontology = self.ontology2GraphQL_schema

    '''
        This function passes the maps between symbols and expressions from Filter_Utils object to Resolver_Utils object.
    '''
    def set_symbol_field_maps(self, field_exp_symbol, symbol_field_exp):
        self.field_exp_symbol, self.symbol_field_exp = field_exp_symbol, symbol_field_exp

    '''
        This function gets the data from json source in query evaluation phase. 
            source_request: supposed to be the url to the json data;
            iterator: the iterating pattern to the json data;
            ref: referencing data based on the semantic mapping.
        return data in json 
    '''
    def get_json_data_without_filter(self, source_request, iterator=None, ref=None):
        data = None
        if source_request[0:4] == 'http':
            r = requests.get(url=source_request)
            data = r.json()
        else:
            with open(source_request) as f:
                data = json.load(f)
        if iterator is not None:
            keys = self.parse_iterator(iterator)
            temp_data = data
            for i in range(len(keys)):
                temp_data = temp_data[keys[i]]
            if ref is not None:
                ref_field_name = ref[1]
                ref_field_values = ref[0]
                temp_data = [x for x in temp_data if x[ref_field_name] in ref_field_values]
            return temp_data
        else:
            return data

    '''
        This function gets the data from csv source in query evaluation phase. 
            url: supposed to be the url to the json data;
            ref: referencing data based on the semantic mapping.
        return data in json 
    '''
    @staticmethod
    def get_csv_data_without_filter(url, ref=None):
        result, ref_field_name, ref_field_values = [], '', []
        if ref is not None:
            ref_field_name = ref[1]
            ref_field_values = ref[0]
        with closing(requests.get(url, stream=True)) as r:
            reader = csv.DictReader(codecs.iterdecode(r.iter_lines(), 'utf-8'), delimiter=';')
            i = 0
            for record in reader:
                i += 1
                if ref is not None:
                    if record[ref_field_name] in ref_field_values:
                        result.append(record)
                else:
                    result.append(record)
        return result

    '''
        This function gets the data from csv source in filter evaluation phase. 
            url: supposed to be the url to the json data;
            key_attrs: 
            filter_dict: filter expression dictionary;
            constant data: constant data based on semantic mappings;
            filter_lst_obj_tag: True means objects in a list.
        return data in pandas dataframe 
    '''
    def get_csv_data_with_filter(self, url, key_attrs, filter_dict=None, constant_data=None, filter_lst_obj_tag=False):
        group_by_attrs = copy.copy(key_attrs)
        result = []
        with closing(requests.get(url, stream=True)) as r:
            reader = csv.DictReader(codecs.iterdecode(r.iter_lines(), 'utf-8'), delimiter=';')
            result = [row for row in reader]
        result = pd.json_normalize(result)
        if len(constant_data) > 0:
            for (constant_pred, data, data_type) in constant_data:
                kwargs = {constant_pred: data}
                result = result.assign(**kwargs)
        if filter_dict is not None:
            if filter_lst_obj_tag is False:
                # no need group by here
                result = self.filter_data_frame(result, filter_dict)
                return result
            else:
                temp_result = self.filter_data_frame_group_by(result, filter_dict, group_by_attrs)
                return temp_result
        else:
            return result

    @staticmethod
    def convert_lst_strings(columns_lst, delimiter):
        lst_strings = ''
        col_num = len(columns_lst)
        k = 0
        for col in columns_lst:
            lst_strings += '`{column}`'.format(column=col)
            k += 1
            if k < col_num:
                lst_strings += '{delimiter} '.format(delimiter=delimiter)
        return lst_strings

    '''
        Parsing the database config defined in the semantic mapping.
    '''
    @staticmethod
    def parse_db_config(db_source):
        server_address = db_source['server']
        hostname_port_schema = server_address.split('://')[1]
        [hostname_port, schema_name] = hostname_port_schema.split('/')
        [hostname, port] = hostname_port.split(':')
        return hostname, port, schema_name, db_source['username'], db_source['password']

    '''
        Generate where statement
    '''
    def generate_where_statement(self, mapping_name):
        in_statement = ''
        filtered_object_columns = self.filtered_object_columns
        if mapping_name in filtered_object_columns.keys():
            column_value = filtered_object_columns.get(mapping_name)
            key, value = list(column_value.items())[0]
            value = list(set(value))
            in_statement = '`{column}` in ({value})'.format(column=key, value=str(value)[1:-1])
        return in_statement

    @staticmethod
    def generate_ref_sql_statement(ref):
        sql_statement = ''
        if ref is not None:
            values = str(ref[0])[1:-1]
            column_name = ref[1]
            if len(values) > 0:
                sql_statement = '`{column}` in ({values})'.format(column=column_name, values=values)
            else:
                sql_statement = ''
        return sql_statement

    '''
        This function gets the data from mysql source in query evaluation phase. 
            key_columns: ;
            db_source: database config in the semantic mapping;
            table_name: name of the table defined in logical source in the semantic mapping;
            query: sql query declared in logical source in the semantic mapping;
            mapping_name:
            ref: referencing data based on the semantic mapping.
        return data in json 
    '''
    def get_mysql_data_without_filter(self, key_columns, db_source,
                                      table_name, query, mapping_name='', ref=None):
        hostname, port, schema_name, db_username, db_password = self.parse_db_config(db_source)
        db_connection_str = 'mysql+pymysql://{user}:{password}@{server}:{port}/{db}'.format(user=db_username,
                                                                                            password=db_password,
                                                                                            server=hostname,
                                                                                            port=port,
                                                                                            db=schema_name)
        sql_query_str = ''
        if len(query) == 0:
            if len(table_name) > 0:
                filtered_object_columns = self.filtered_object_columns
                if key_columns is not None:
                    select_cols = self.convert_lst_strings(key_columns, ',')
                    if mapping_name in filtered_object_columns.keys():
                        where_statement = self.generate_where_statement(mapping_name)
                        sql_query_str = 'SELECT {select_cols} FROM `{table}` WHERE {where_statement}'.format(select_cols=select_cols, table=table_name, where_statement=where_statement)
                        self.sql_flag = True
                    else:
                        if ref is not None:
                            ref_statement = self.generate_ref_sql_statement(ref)
                        else:
                            ref_statement = ''
                        if len(ref_statement) > 0:
                            sql_query_str = 'SELECT {select_cols} FROM `{table}` WHERE {where_statement}}'.format(select_cols=select_cols, table=table_name, where_statement=ref_statement)
                        else:
                            sql_query_str = 'SELECT {select_cols} FROM `{table}`'.format(select_cols=select_cols, table=table_name)
                else:
                    if mapping_name in filtered_object_columns.keys():
                        where_statement = self.generate_where_statement(mapping_name)
                        sql_query_str = 'SELECT * FROM `{table}` WHERE {where_statement}'.format(table=table_name, where_statement=where_statement)
                        self.sql_flag = True
                    else:
                        if ref is not None:
                            ref_statement = self.generate_ref_sql_statement(ref)
                        else:
                            ref_statement = ''
                        if len(ref_statement) > 0:
                            sql_query_str = 'SELECT * FROM `{table}` WHERE {where_statement}'.format(table=table_name, where_statement=ref_statement)
                        else:
                            sql_query_str = 'SELECT * FROM `{table}`'.format(table=table_name)
        else:
            # for future update
            filtered_object_columns = self.filtered_object_columns
            select_statement = '({query_statement}) AS NEW_TABLE'.format(query_statement=query)
            if key_columns is not None:
                select_cols = self.convert_lst_strings(key_columns, ',')
                if mapping_name in filtered_object_columns.keys():
                    where_statement = self.generate_where_statement(mapping_name)
                    sql_query_str = 'SELECT {select_cols} FROM {select_statement} WHERE {where_statement}'.format(
                        select_cols=select_cols, select_statement=select_statement, where_statement=where_statement)
                    self.sql_flag = True
                else:
                    if ref is not None:
                        ref_statement = self.generate_ref_sql_statement(ref)
                    else:
                        ref_statement = ''
                    if len(ref_statement) > 0:

                        sql_query_str = 'SELECT {select_cols} FROM {select_statement} WHERE {where_statement}}'.format(
                            select_cols=select_cols, select_statement=select_statement, where_statement=ref_statement)
                    else:
                        sql_query_str = 'SELECT {select_cols} FROM {select_statement}'.format(select_cols=select_cols,
                                                                                     select_statement=select_statement)
            else:
                if mapping_name in filtered_object_columns.keys():
                    where_statement = self.generate_where_statement(mapping_name)
                    sql_query_str = 'SELECT * FROM {select_statement} WHERE {where_statement}'.format(select_statement=select_statement,
                                                                                             where_statement=where_statement)
                    self.sql_flag = True
                else:
                    if ref is not None:
                        ref_statement = self.generate_ref_sql_statement(ref)
                    else:
                        ref_statement = ''
                    if len(ref_statement) > 0:
                        sql_query_str = 'SELECT * FROM {select_statement} WHERE {where_statement}'.format(select_statement=select_statement,
                                                                                                 where_statement=ref_statement)
                    else:
                        sql_query_str = 'SELECT * FROM {select_statement}'.format(select_statement=select_statement)
        df = pd.read_sql_query(text(sql_query_str), db_connection_str)
        result = df.to_dict(orient='records')
        return result

    '''
        This function gets the data from mysql source in filter evaluation phase. 
            key_columns: 
            filter_dict: filter expression dictionary;
            constant data: constant data based on semantic mappings;
            filter_lst_obj_tag: True means objects in a list;
            db_source: database config in the semantic mapping;
            table_name: name of the table defined in logical source in the semantic mapping;
            query: sql query declared in logical source in the semantic mapping.
        return data in json
    '''
    def get_mysql_data_with_filter(self, key_columns, filter_dict, constant_data, filter_lst_obj_tag, db_source, table_name, query):
        hostname, port, schema_name, db_username, db_password = self.parse_db_config(db_source)
        db_connection_str = 'mysql+pymysql://{user}:{password}@{server}:{port}/{db}'.format(user=db_username,
                                                                                            password=db_password,
                                                                                            server=hostname,
                                                                                            port=port,
                                                                                            db=schema_name)
        constant_preds = []
        if constant_data is not None:
            for (constant_pred, data, data_type) in constant_data:
                constant_preds.append(constant_pred)
        sql_query_str = ''
        constant_pred_filter = dict()
        sql_pred_filter = dict()
        if filter_dict is not None:
            for pred, filter_dict_value in filter_dict.items():
                if filter_dict_value['local_name'] not in key_columns and pred not in constant_preds:
                    # key_columns.append(filter_dict_value['local_name'])
                    pass
                if pred in constant_preds:
                    constant_pred_filter[pred] = filter_dict_value
                else:
                    sql_pred_filter[pred] = filter_dict_value
            if filter_lst_obj_tag is False:
                filter_str = ''
                sql_filter_columns_num = len(sql_pred_filter)
                i = 0
                for pred, filter_dict_value in sql_pred_filter.items():
                    local_name = filter_dict_value['local_name']
                    attr_type = filter_dict_value['attribute_type']
                    atom_filter_num = len(filter_dict_value['filter'])
                    j = 0
                    for atom_filter in filter_dict_value['filter']:
                        filter_str += self.generate_mysql_filter_str(local_name, atom_filter['operator'],
                                                                     atom_filter['value'], atom_filter['negation'],
                                                                     attr_type)
                        j += 1
                        if j < atom_filter_num:
                            filter_str += ' AND '
                    i += 1
                    if i < sql_filter_columns_num:
                        filter_str += ' AND '
                select_cols = self.convert_lst_strings(key_columns, ',')
                if len(table_name) > 0:
                    sql_query_str = 'SELECT {select_cols} FROM `{table}` WHERE {filter}'.format(select_cols=select_cols, table=table_name, filter=filter_str)
                if len(query) > 0:
                    select_statement = '({query_statement}) AS NEW_TABLE'.format(query_statement=query)
                    sql_query_str = 'SELECT {select_cols} FROM {select_statement} WHERE {filter}'.format(select_cols=select_cols, select_statement=select_statement, filter=filter_str)
            else:
                having_str = ''
                sql_filter_columns_num = len(sql_pred_filter)
                i = 0
                for pred, filter_dict_value in sql_pred_filter.items():
                    local_name = filter_dict_value['local_name']
                    attr_type = filter_dict_value['attribute_type']
                    atom_filter_num = len(filter_dict_value['filter'])
                    j = 0
                    for atom_filter in filter_dict_value['filter']:
                        having_str += self.generate_mysql_having_statement(local_name, atom_filter['operator'],
                                                                           atom_filter['value'], atom_filter['negation'],
                                                                           attr_type)
                        j += 1
                        if j < atom_filter_num:
                            having_str += ' AND '
                    i += 1
                    if i < sql_filter_columns_num:
                        having_str += ' AND '
                group_by_cols = self.convert_lst_strings(key_columns, ',')

                if len(table_name) > 0:
                    sql_query_str = 'SELECT {select_cols} FROM `{table}` GROUP BY {group_cols} HAVING {having_statement}'.format(select_cols=group_by_cols, table=table_name, group_cols=group_by_cols, having_statement=having_str)
                if len(query) > 0:
                    select_statement = '({query_statement}) AS NEW_TABLE'.format(query_statement=query)
                    sql_query_str = 'SELECT {select_cols} FROM {select_statement} GROUP BY {group_cols}  HAVING {having_statement}'.format(select_cols=group_by_cols, select_statement=select_statement, group_cols=group_by_cols, having_statement = having_str)
        else:
            if filter_lst_obj_tag is False:
                sql_query_str = 'SELECT * FROM `{table}`'.format(table=table_name)
            else:
                sql_query_str = 'SELECT * FROM `{table}`'.format(table=table_name)
        df = pd.read_sql_query(text(sql_query_str), db_connection_str)
        if len(constant_data) > 0:
            for (constant_pred, data, data_type) in constant_data:
                kwargs = {constant_pred: data}
                df = df.assign(**kwargs)
            if filter_lst_obj_tag is False:
                df = self.filter_data_frame(df, constant_pred_filter)
            else:
                key_columns += constant_preds
                df = self.filter_data_frame_group_by(df, constant_pred_filter, key_columns)
        return df

    '''
        This function gets the data from json source in filter evaluation phase. 
            url: supposed to be the url to the json data;
            iterator: the iterating pattern to the json data;
            key_attrs: 
            filter_dict: filter expression dictionary;
            constant data: constant data based on semantic mappings;
            filter_lst_obj_tag: True means objects in a list.
        return data in json
    '''
    def get_json_data_with_filter(self, url, iterator, key_attrs, filter_dict=None, constant_data=None, filter_lst_obj_tag=False):
        group_by_attrs = copy.copy(key_attrs)
        if filter_dict is not None:
            for key, value in filter_dict.items():
                if value['local_name'] not in key_attrs:
                    key_attrs.append(value['local_name'])
                    if '.' in value['local_name']:
                        prefix_attr = value['local_name'].split('.')[0]
                        if prefix_attr not in key_attrs:
                            key_attrs.append(prefix_attr)

        if url[0:4] == 'http':
            r = requests.get(url=url)
            data = r.json()
        else:
            with open(url) as f:
                data = json.load(f)

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
        if len(constant_data) > 0:
            for (constant_pred, data, data_type) in constant_data:
                kwargs = {constant_pred: data}
                result = result.assign(**kwargs)
        if filter_dict is not None:
            if filter_lst_obj_tag is False:
                # no need group by here
                result = self.filter_data_frame(result, filter_dict)
                return result
            else:
                temp_result = self.filter_data_frame_group_by(result, filter_dict, group_by_attrs)
                return temp_result
        else:
            return result

    '''
           This function gets the data from OPTIMADE endpoint,
           which can be further extended to any API requests with filter expressions. 
               url: supposed to be the url to the json data;
               iterator: the iterating pattern to the json data;
               key_attrs: 
               filter_dict: filter expression dictionary;
               constant data: constant data based on semantic mappings;
               filter_lst_obj_tag: True means objects in a list.
           return data in json
       '''
    def get_optimade_data_with_filter(self, url, iterator, key_attrs, filter_dict=None, constant_data=None, filter_lst_obj_tag=False):
        constant_preds = []
        if constant_data is not None:
            for (constant_pred, data, data_type) in constant_data:
                constant_preds.append(constant_pred)
        constant_pred_filter = dict()
        sql_pred_filter = dict()
        if filter_dict is not None:
            for pred, filter_dict_value in filter_dict.items():
                if filter_dict_value['local_name'] not in key_attrs and pred not in constant_preds:
                    # key_columns.append(filter_dict_value['local_name'])
                    pass
                if pred in constant_preds:
                    constant_pred_filter[pred] = filter_dict_value
                else:
                    sql_pred_filter[pred] = filter_dict_value
            if filter_lst_obj_tag is False:
                filter_str = ''
                sql_filter_columns_num = len(sql_pred_filter)
                i = 0
                for pred, filter_dict_value in sql_pred_filter.items():
                    if '.' in filter_dict_value['local_name']:
                        local_name = filter_dict_value['local_name'].split('.')[-1]
                    else:
                        local_name = filter_dict_value['local_name']
                    attr_type = filter_dict_value['attribute_type']
                    atom_filter_num = len(filter_dict_value['filter'])
                    j = 0
                    for atom_filter in filter_dict_value['filter']:
                        filter_str += self.generate_optimade_filter_str(local_name, atom_filter['operator'],
                                                                     atom_filter['value'], atom_filter['negation'],
                                                                     attr_type)
                        j += 1
                        if j < atom_filter_num:
                            filter_str += '+AND+'
                    i += 1
                    if i < sql_filter_columns_num:
                        filter_str += '+AND+'
                if url[0:4] == 'http':
                    filter_url = url +'?'+ filter_str
                    r = requests.get(url=filter_url)
                    data = r.json()
            else:
                if url[0:4] == 'http':
                    r = requests.get(url=url)
                    data = r.json()
        else:
            if url[0:4] == 'http':
                r = requests.get(url=url)
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
        if len(constant_data) > 0:
            for (constant_pred, data, data_type) in constant_data:
                kwargs = {constant_pred: data}
                result = result.assign(**kwargs)
            if filter_lst_obj_tag is False:
                result = self.filter_data_frame(result, constant_pred_filter)
            else:
                key_attrs += constant_preds
                result = self.filter_data_frame_group_by(result, constant_pred_filter, key_attrs)
        return result


    @staticmethod
    def transform_operator_mysql(operator, negation_flag=False):
        if operator == '_eq':
            return '=' if not negation_flag else '!='
        elif operator == '_gt':
            return '>' if not negation_flag else '<='
        elif operator == '_lt':
            return '<' if not negation_flag else '>='
        elif operator == '_in':
            return 'in' if not negation_flag else 'not in'
        elif operator == '_nin':
            return 'not in' if not negation_flag else 'in'
        elif operator == '_like':
            return 'like'
        elif operator == '_ilike':
            return 'ilike'
        else:
            return operator

    @staticmethod
    def transform_operator_optimade(operator, negation_flag=False):
        if operator == '_eq':
            return '=' if not negation_flag else '!='
        elif operator == '_gt':
            return '>' if not negation_flag else '<='
        elif operator == '_lt':
            return '<' if not negation_flag else '>='
        else:
            return operator
        '''
         elif operator == '_in':
            return 'in' if not negation_flag else 'not in'
        elif operator == '_nin':
            return 'not in' if not negation_flag else 'in'
        elif operator == '_like':
            return 'like'
        elif operator == '_ilike':
            return 'ilike'
        '''


    @staticmethod
    def direct_transform_operator(operator):
        if operator == '_eq':
            return '='
        elif operator == '_gt':
            return '>'
        elif operator == '_egt':
            return '>='
        elif operator == '_lt':
            return '<'
        elif operator == '_elt':
            return '<='
        elif operator == '_in':
            return 'in'
        elif operator == '_nin':
            return 'not in'
        elif operator == '_like':
            return 'like'
        elif operator == '_ilike':
            return 'ilike'
        else:
            return operator

    @staticmethod
    def transform_operator_df(operator, negation_flag=False):
        if operator == '_eq':
            return '==' if not negation_flag else '!='
        elif operator == '_gt':
            return '>' if not negation_flag else '<='
        elif operator == '_lt':
            return '<' if not negation_flag else '>='
        elif operator == '_in':
            return 'in' if not negation_flag else 'not in'
        elif operator == '_nin':
            return 'not in' if not negation_flag else 'in'
        elif operator == '_like':
            return 'like'
        elif operator == '_ilike':
            return 'ilike'
        else:
            return operator

    '''
        Generate the lambda function based on the operator
    '''
    @staticmethod
    def transform_lambda_func(column_name, operator, value, negation_flag=False):
        if operator == '_eq':
            if negation_flag is False:
                return lambda x: x[column_name].eq(value).any()
            else:
                return lambda x: x[column_name].ne(value).any()
        elif operator == '_neq':
            if negation_flag is False:
                return lambda x: x[column_name].neq(value).any()
            else:
                return lambda x: x[column_name].neq(value).all()
        elif operator == '_gt':
            if negation_flag is False:
                return lambda x: x[column_name].gt(value).any()
            else:
                return lambda x: x[column_name].le(value).any()
        elif operator == '_egt':
            if negation_flag is False:
                return lambda x: x[column_name].ge(value).any()
            else:
                return lambda x: x[column_name].lt(value).any()
        elif operator == '_lt':
            if negation_flag is False:
                return lambda x: x[column_name].lt(value).any()
            else:
                return lambda x: x[column_name].ge(value).any()
        elif operator == '_le':
            if negation_flag is False:
                return lambda x: x[column_name].le(value).any()
            else:
                return lambda x: x[column_name].gt(value).any()
        elif operator == '_in':
            if negation_flag is False:
                return lambda x: x[column_name].isin(value).any()
            else:
                return lambda x: ~x[column_name].isin(value).any()
        elif operator == '_nin':
            if negation_flag is False:
                return lambda x: ~x[column_name].isin(value).any()
            else:
                return lambda x: x[column_name].isin(value).all()
        elif operator == '_like':
            if negation_flag is False:
                return lambda x: x[column_name].str.match(value).any()
            else:
                return lambda x: ~x[column_name].str.match(value).any()
        elif operator == '_nlike':
            if negation_flag is False:
                return lambda x: ~x[column_name].str.match(value).any()
            else:
                return lambda x: x[column_name].str.match(value).all()
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

    '''
        Filter operation on pandas data frame
    '''
    def filter_data_frame(self, df, filter_dict):
        for pred, filter_dict_value in filter_dict.items():
            local_name = filter_dict_value['local_name']
            attr_type = filter_dict_value['attribute_type']
            for atom_filter in filter_dict_value['filter']:
                filter_str = self.generate_df_filter_str(local_name, df.dtypes[local_name], atom_filter['operator'],
                                                         atom_filter['value'], atom_filter['negation'], attr_type)
                if attr_type == 'Int':
                    if df.dtypes[local_name] != 'int64':
                        df = df.astype({local_name: int})
                elif attr_type == 'Float':
                    if df.dtypes[local_name] != 'float64':
                        df = df.astype({local_name: float})
                else:
                    pass
                if atom_filter['operator'] not in ['_like', '_nlike']:
                    df = df.query(filter_str)
                else:
                    if atom_filter['negation'] is True:
                        df = df[df[local_name].str.match(filter_str) == False]
                    else:
                        df = df[df[local_name].str.match(filter_str) == True]
        return df

    '''
        Filter and group by operations on pandas data frame
    '''
    def filter_data_frame_group_by(self, df, filter_dict, key_attrs):
        for pred, filter_dict_value in filter_dict.items():
            local_name = filter_dict_value['local_name']
            attr_type = filter_dict_value['attribute_type']
            for atom_filter in filter_dict_value['filter']:
                filter_lambda_func = self.generate_filter_lambda_func(local_name, df.dtypes[local_name],
                                                                      atom_filter['operator'], atom_filter['value'],
                                                                      atom_filter['negation'], attr_type)
                if attr_type == 'Int':
                    if df.dtypes[local_name] != 'int64':
                        df = df.astype({local_name: int})
                elif attr_type == 'Float':
                    if df.dtypes[local_name] != 'float64':
                        df = df.astype({local_name: float})
                else:
                    pass
                df = df.groupby(key_attrs).filter(filter_lambda_func)
        return df

    '''
        Generate the regex expression for pandas dataframe, to answer 'like', 'nlike' in the GraphQL query
    '''
    @staticmethod
    def generate_regex_str(pattern_str):
        if pattern_str[0] != '%':
            pattern_str = '^' + pattern_str
        if pattern_str[-1] != '%':
            pattern_str = pattern_str + '$'
        pattern_str = pattern_str.replace('_', '.')
        pattern_str = pattern_str.replace('%', '.*')
        return pattern_str

    '''
        Generate the filter lambda function for pandas dataframe, given the atomic filter representation, 
        futhermore will be used for group by operation
    '''
    def generate_filter_lambda_func(self, attribute_name, column_type, operator_str, value_str, negation_flag, attr_type):
        lambda_func = None
        if operator_str in ['_in', '_nin']:
            if column_type == 'int64':
                new_value = ast.literal_eval(value_str)
                new_value = [int(x) for x in new_value if x.isnumeric() is True]
                lambda_func = self.transform_lambda_func(attribute_name, operator_str, new_value, negation_flag)
            else:
                new_value = ast.literal_eval(value_str)
                lambda_func = self.transform_lambda_func(attribute_name, operator_str, new_value, negation_flag)
        elif operator_str in ['_like', '_nlike']:
            new_value =self.generate_regex_str(value_str)
            lambda_func = self.transform_lambda_func(attribute_name, operator_str, new_value, negation_flag)
        else:
            if attr_type == 'String' or attr_type == 'ID':
                if column_type == 'int64':
                    new_value = int(value_str)
                    lambda_func = self.transform_lambda_func(attribute_name, operator_str, new_value, negation_flag)
                else:
                    new_value = str(value_str)
                    lambda_func = self.transform_lambda_func(attribute_name, operator_str, new_value, negation_flag)
            elif attr_type == 'Int':
                new_value = int(value_str)
                lambda_func = self.transform_lambda_func(attribute_name, operator_str, new_value, negation_flag)
            elif attr_type == 'Float':
                new_value = float(value_str)
                lambda_func = self.transform_lambda_func(attribute_name, operator_str, new_value, negation_flag)
            else:
                pass
        return lambda_func

    '''
        Generate the filter string for pandas dataframe, given the atomic filter representation
    '''
    def generate_df_filter_str(self, attribute_name, column_type, operator_str, value_str, negation_flag, attr_type):
        filter_str = ''
        column_name = '`{column}`'.format(column=attribute_name)
        new_operator = self.transform_operator_df(operator_str, negation_flag)
        if operator_str in ['_in', '_nin']:
            if column_type == 'int64':
                new_value = ast.literal_eval(value_str)
                new_value = [int(x) for x in new_value if x.isnumeric() is True]
                filter_str = "{column} {operator} {value} ".format(column=column_name, operator=new_operator,
                                                                   value=new_value)
            else:
                filter_str = "{column} {operator} {value} ".format(column=column_name, operator=new_operator,
                                                                   value=value_str)
        elif operator_str in ['_like', '_nlike']:
            filter_str = self.generate_regex_str(value_str)
        else:
            if attr_type == 'String' or 'ID':
                if column_type == 'int64':
                    new_value = int(value_str)
                    filter_str = "{column} {operator} {value} ".format(column=column_name, operator=new_operator,
                                                                       value=new_value)
                else:
                    new_value = str(value_str)
                    filter_str = "{column} {operator} \"{value}\" ".format(column=column_name, operator=new_operator,
                                                                           value=new_value)
            elif attr_type == 'Int':
                new_value = int(value_str)
                filter_str = "{column} {operator} {value} ".format(column=column_name, operator=new_operator,
                                                                   value=new_value)
            elif attr_type == 'Float':
                new_value = float(value_str)
                filter_str = "{column} {operator} {value} ".format(column=column_name, operator=new_operator,
                                                                   value=new_value)
            else:
                pass
        return filter_str

    '''
        Generate the having statement for MYSQL, given the atomic filter representation
    '''
    def generate_mysql_having_statement(self, column_name, operator_str, value_str, negation_flag, attr_type):
        having_str = ''
        new_operator = self.direct_transform_operator(operator_str)
        if operator_str in ['_in', '_nin']:
            values = value_str[1:-1]
            if negation_flag is True:
                having_str = 'sum(`{column}` {operator} ({values})) = 0'.format(column=column_name, operator=new_operator, values=values)
            else:
                having_str = 'sum(`{column}` {operator} ({values})) > 0'.format(column=column_name, operator=new_operator, values=values)
        else:
            if attr_type == 'String' or attr_type == 'ID':
                new_value = str(value_str)
                if negation_flag is True:
                    having_str = 'sum(`{column}` {operator} \'{value}\') = 0'.format(column=column_name,
                                                                                    operator=new_operator,
                                                                                    value=new_value)
                else:
                    having_str = 'sum(`{column}` {operator} \'{value}\') > 0'.format(column=column_name,
                                                                                    operator=new_operator,
                                                                                    value=new_value)
            elif attr_type == 'Int':
                new_value = int(value_str)
                if negation_flag is True:
                    having_str = 'sum(`{column}` {operator} {value}) = 0'.format(column=column_name,
                                                                                operator=new_operator,
                                                                                value=new_value)
                else:
                    having_str = 'sum(`{column}` {operator} {value}) > 0'.format(column=column_name,
                                                                                operator=new_operator,
                                                                                value=new_value)
            elif attr_type == 'Float':
                new_value = float(value_str)
                if negation_flag is True:
                    having_str = 'sum(`{column}` {operator} {value}) = 0'.format(column=column_name,
                                                                                operator=new_operator,
                                                                                value=new_value)
                else:
                    having_str = 'sum(`{column}` {operator} {value}) > 0'.format(column=column_name,
                                                                                 operator=new_operator,
                                                                                 value=new_value)
            else:
                pass
        return having_str

    '''
        Generate the filter string for MYSQL, given the atomic filter representation
    '''
    def generate_mysql_filter_str(self, column_name, operator_str, value_str, negation_flag, attr_type):
        filter_str = ''
        new_operator = self.transform_operator_mysql(operator_str, negation_flag)
        if operator_str in ['_in', '_nin']:
            values = value_str[1:-1]
            filter_str = '`{column}` {operator} ({values})'.format(column=column_name, operator=new_operator, values=values)
        else:
            if attr_type == 'String' or attr_type == 'ID':
                new_value = str(value_str)
                filter_str = '`{column}` {operator} \'{value}\''.format(column=column_name, operator=new_operator,
                                                                    value=new_value)
            elif attr_type == 'Int':
                new_value = int(value_str)
                filter_str = '`{column}` {operator} {value}'.format(column=column_name, operator=new_operator,
                                                                    value=new_value)
            elif attr_type == 'Float':
                new_value = float(value_str)
                filter_str = '`{column}` {operator} {value}'.format(column=column_name, operator=new_operator,
                                                                    value=new_value)
            else:
                pass
        return filter_str


        '''
            Generate the filter string for OPTIMADE, given the atomic filter representation
        '''

    def generate_optimade_filter_str(self, column_name, operator_str, value_str, negation_flag, attr_type):
        filter_str = ''
        new_operator = self.transform_operator_optimade(operator_str, negation_flag)
        if operator_str in ['_in', '_nin']:
            values = value_str[1:-1]
            filter_str = '{column}{operator}({values})'.format(column=column_name, operator=new_operator,
                                                                   values=values)
        else:
            if attr_type == 'String' or attr_type == 'ID':
                new_value = str(value_str)
                filter_str = '{column}{operator}\"{value}\"'.format(column=column_name, operator=new_operator,
                                                                        value=new_value)
            elif attr_type == 'Int':
                new_value = int(value_str)
                filter_str = '{column}{operator}{value}'.format(column=column_name, operator=new_operator,
                                                                    value=new_value)
            elif attr_type == 'Float':
                new_value = float(value_str)
                filter_str = '{column}{operator}{value}'.format(column=column_name, operator=new_operator,
                                                                    value=new_value)
            else:
                pass
        return filter_str
    '''
        Get the sub-AST of a query AST
    '''
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
        named_type_value, encode_labels = '', ''
        if 'type' in field.keys:
            # named_type: 0, list_type: 2, non_null_type 1
            node_type = self.check_node_type(field.type)
            if node_type == 'non_null_type':
                value, labels = self.parse_field(field.type)
                named_type_value = value
                encode_labels = '1' + labels
            elif node_type == 'list_type':
                value, labels = self.parse_field(field.type)
                named_type_value = value
                encode_labels = '2' + labels
            else:
                named_type_value = field.type.name.value
                encode_labels = '0'
        return named_type_value, encode_labels

    '''
        Generate the AST of GraphQL schema
    '''
    def generate_schema_ast(self, schema):
        from graphql import parse
        if len(self.schema_ast) == 0:
            schema_ast = dict()
            document = parse(schema)
            for definition in document.definitions:
                if definition.kind == 'object_type_definition':
                    schema_ast[definition.name.value] = dict()
                    for wrapped_field in definition.fields:
                        named_type_value, encode_labels = self.parse_field(wrapped_field)
                        if definition.name.value == 'Query':
                            self.filter_fields_map[(wrapped_field.name.value, 'filter')] = (named_type_value, encode_labels)

                        else:
                            self.filter_fields_map[(definition.name.value, wrapped_field.name.value)] = (named_type_value, encode_labels)
                            interface_names = [x.name.value for x in definition.interfaces]
                            for interface_name in interface_names:
                                schema_ast[interface_name]['sub_types'].append(definition.name.value)
                        schema_ast[definition.name.value][wrapped_field.name.value] = {
                            'base_type': named_type_value,
                            'wrapping_label': encode_labels}
                elif definition.kind == 'input_object_type_definition':
                    schema_ast[definition.name.value] = dict()
                    for wrapped_field in definition.fields:
                        named_type_value, encode_labels = self.parse_field(wrapped_field)
                        schema_ast[definition.name.value][wrapped_field.name.value] = {'base_type': named_type_value,
                                                                                       'wrapping_label': encode_labels}
                elif definition.kind == 'interface_type_definition':
                    self.interfaces.append(definition.name.value)
                    schema_ast[definition.name.value] = dict()
                    schema_ast[definition.name.value]['sub_types'] = []
                    for wrapped_field in definition.fields:
                        named_type_value, encode_labels = self.parse_field(wrapped_field)
                        schema_ast[definition.name.value][wrapped_field.name.value] = {'base_type': named_type_value,
                                                                                       'wrapping_label': encode_labels}
                else:
                    pass

            self.schema_ast = schema_ast
            return self.schema_ast
        else:
            return self.schema_ast

    '''
        Get all the query entries based on GraphQL schema
    '''
    def get_query_entries(self, schema):
        schema_ast = self.generate_schema_ast(schema)
        object_type_query_entries, interface_type_query_entries = [], []
        for query_name_key, query_entry_schema in schema_ast['Query'].items():
            if query_entry_schema['base_type'] in self.interfaces:
                interface_type_query_entries.append(query_name_key)
            else:
                object_type_query_entries.append(query_name_key)
        self.interface_query_entries = interface_type_query_entries
        return object_type_query_entries, interface_type_query_entries

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

    '''
        Generate multiple query ASTs in which the GraphQL query is to traversal an interface
    '''
    def generate_query_asts(self, query_info):
        schema_ast = self.schema_ast
        query_field_nodes = query_info.field_nodes
        query_ast = self.parse_query_fields('Query', query_field_nodes)
        inline_query_asts = query_ast['fields']
        for inline_query_ast in inline_query_asts:
            inline_fragment_type = inline_query_ast['type']
            self.fill_return_type(inline_query_ast, schema_ast, inline_fragment_type)
        return inline_query_asts

    '''
        Generate the AST of the GraphQL query
    '''
    def generate_query_ast(self, query_info):
        schema_ast = self.schema_ast
        query_field_nodes = query_info.field_nodes
        query_ast = self.parse_query_fields('Query', query_field_nodes)
        query_entry_name = query_ast['fields'][0]['name']
        if len(query_ast['fields'][0]['type']) == 0:
            query_ast['fields'][0]['type'] = schema_ast['Query'][query_entry_name]['base_type']
        query_ast['fields'][0]['wrapping_label'] = schema_ast['Query'][query_entry_name]['wrapping_label']
        # query_ast is changed inside fill_return_type
        self.fill_return_type(query_ast['fields'][0], schema_ast, query_ast['fields'][0]['type'])
        return query_ast

    @staticmethod
    def parse_iterator(iterator):
        iterator_elements = iterator.split('.')
        iterator_elements = list(filter(None, iterator_elements))
        return iterator_elements

    def phi(self, ontology_term):
        return self.ontology2GraphQL_schema[ontology_term]

    def inverse_phi(self, graphql_term):
        return self.GraphQL_schema2ontology[graphql_term]

    @staticmethod
    def parse_template(template):
        start_pos = template.index('{')
        end_pos = template.index('}')
        key = template[start_pos + 1: end_pos]
        new_template = template.replace(key, '')
        return key, new_template

    '''
        Refine json data with field names according to the ontology and add iri column
    '''
    def refine_json(self, temp_result, attr_pred_lst, constant, template, root_type_flag=False, mapping_name='', key_attributes=[], filtered_object_iri=None):
        key, template = self.parse_template(template)
        i = 0
        while i < len(temp_result):
            if len(constant) > 0:
                for (constant_pred, constant_data, data_type) in constant:
                    temp_result[i][constant_pred] = constant_data
            iri = template.format(temp_result[i][key])
            if root_type_flag is True:
                if mapping_name in filtered_object_iri.keys() and iri in filtered_object_iri[mapping_name] or \
                        filtered_object_iri['filter'] is False:
                    temp_result[i]['iri'] = iri
                    if len(attr_pred_lst) > 0:
                        for attr_pred_tuple in attr_pred_lst:
                            if '.' in attr_pred_tuple[0]:
                                keys = self.parse_iterator(attr_pred_tuple[0])
                                temp_data = temp_result[i]
                                for j in range(len(keys)):
                                    temp_data = temp_data[keys[j]]
                                    temp_result[i][attr_pred_tuple[1]] = temp_data
                            else:
                                if attr_pred_tuple[0] in temp_result[i].keys():
                                    temp_result[i][attr_pred_tuple[1]] = temp_result[i][attr_pred_tuple[0]]
                    i += 1
                else:
                    del temp_result[i]
            else:
                temp_result[i]['iri'] = iri
                if len(attr_pred_lst) > 0:
                    for attr_pred_tuple in attr_pred_lst:
                        if '.' in attr_pred_tuple[0]:
                            keys = self.parse_iterator(attr_pred_tuple[0])
                            temp_data = temp_result[i]
                            for j in range(len(keys)):
                                temp_data = temp_data[keys[j]]
                                temp_result[i][attr_pred_tuple[1]] = temp_data
                        else:
                            if attr_pred_tuple[0] in temp_result[i].keys():
                                temp_result[i][attr_pred_tuple[1]] = temp_result[i][attr_pred_tuple[0]]
                i += 1
        return temp_result

    @staticmethod
    def check_node_type(node):
        if node.kind == 'non_null_type':
            return 'non_null_type'
        elif node.kind == 'named_type':
            return 'named_type'
        elif node.kind == 'list_type':
            return 'list_type'
        else:
            pass
        return 0

    def parse_query_fields(self, root_name, query_field_notes):
        resolve_type = ''
        result = dict()
        result['name'] = root_name
        result['type'] = ''
        fields = []
        for qfn in query_field_notes:
            if qfn.kind == 'inline_fragment':
                break
            else:
                if qfn.selection_set is not None:
                    next_level_qfns = qfn.selection_set.selections
                    inline_fragment_selections = []
                    query_selections = []
                    for selection in next_level_qfns:
                        if selection.kind == 'inline_fragment':
                            inline_fragment_selections.append(selection)
                        else:
                            query_selections.append(selection)
                    if len(query_selections) > 0:
                        temp_result = self.parse_query_fields(qfn.name.value, query_selections)
                        fields.append(temp_result)
                    if len(inline_fragment_selections) > 0:
                        for inline_fragment_selection in inline_fragment_selections:
                            resolve_type = inline_fragment_selection.type_condition.name.value
                            inline_next_level_qfns = inline_fragment_selection.selection_set.selections
                            temp_result = self.parse_query_fields(qfn.name.value, inline_next_level_qfns)
                            temp_result['type'] = resolve_type
                            fields.append(temp_result)
                else:
                    field = {'name': qfn.name.value, 'type': '', 'fields': []}
                    fields.append(field)
        result['fields'] = fields
        return result

    '''
        The entry to access underlying data sources
    '''
    def executor(self, logical_source, key_attrs, filter_flag=False, filter_dict=None, ref=None, constant_data=None, filter_lst_obj_tag=False, mapping_name=''):
        source_type = self.mu.get_logical_source_type(logical_source)
        result = []
        if source_type == 'ql:CSV':
            if 'table' in logical_source.keys() or 'query' in logical_source.keys():
                db_source, table_name, query = self.mu.get_db_source(logical_source)
                if filter_flag is True:
                    result = self.get_mysql_data_with_filter(key_attrs, filter_dict,
                                                             constant_data, filter_lst_obj_tag, db_source, table_name, query)
                else:
                    result = self.get_mysql_data_without_filter(key_attrs, db_source, table_name, query, mapping_name, ref)

            else:
                source_request = self.mu.get_source(logical_source)
                if filter_flag is True:
                    result = self.get_csv_data_with_filter(source_request, key_attrs, filter_dict,
                                                           constant_data, filter_lst_obj_tag)
                else:
                    result = self.get_csv_data_without_filter(source_request, ref)
        elif source_type == 'ql:JSONPath':
            source_request = self.mu.get_source(logical_source)
            iterator = self.mu.get_json_iterator(logical_source)
            if filter_flag is True:
                # data frame here
                # group_by_mysql_attrs = copy.copy(key_attrs)
                #result = self.get_json_data_with_filter(source_request, iterator, key_attrs, filter_dict, constant_data, filter_lst_obj_tag)
                result = self.get_optimade_data_with_filter(source_request, iterator, key_attrs, filter_dict, constant_data,
                                                        filter_lst_obj_tag)

            else:
                result = self.get_json_data_without_filter(source_request, iterator, ref)
        else:
            pass
        return result

    '''
        Refine data frame's column names and add iri column
    '''
    def refine_data_frame(self, df, pred_attr_dict, template, mapping_name):
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

    '''
        Generate ASTs of filter expression in DNF
    '''
    @staticmethod
    def generate_filter_asts(filter_fields_map, symbol_exp_dict, conjunctive_exp_lst, entry=''):
        from generic_resolver.filter_ast import Filter_AST
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
            for field_filter in field_filters:
                fields = field_filter[0].split('.')
                root_type = entry
                temp_ast = filter_ast
                for f in fields:
                    if f not in temp_ast.children_edges:
                        name = filter_fields_map[(root_type, f)][0]
                        if f == 'filter':
                            list_obj_tag = '0'
                        else:
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

    '''
        Combine super filter and current node filter
    '''
    @staticmethod
    def new_filter(super_filters, current_filter):
        super_filters.update(current_filter)
        return super_filters

    def get_join_cache(self, symbolic_filter):
        join_cache = self.join_cache
        if symbolic_filter in join_cache.keys():
            return join_cache[symbolic_filter]
        else:
            return None

    def get_single_cache(self, symbolic_filter):
        single_cache = self.single_cache
        if symbolic_filter in single_cache.keys():
            return single_cache[symbolic_filter]
        else:
            return None

    '''
        Transform filter expressions based on underlying data sources' terminologies
    '''
    def localize_filter(self, entity_type, pred_attr, filter_fields=None, filter_constant_field=None):
        schema_ast = self.schema_ast
        if len(filter_fields) == 0:
            return
        else:
            localized_filter_fields = defaultdict(dict)
            for key, value in filter_fields.items():
                if key in pred_attr.keys():
                    localized_filter_fields[key]['local_name'] = pred_attr[key]
                    localized_filter_fields[key]['attribute_type'] = schema_ast[entity_type][key]['base_type']
                    localized_filter_fields[key]['filter'] = value
                else:
                    if len(filter_constant_field) > 0:
                        localized_filter_fields[key]['local_name'] = key
                        localized_filter_fields[key]['attribute_type'] = schema_ast[entity_type][key]['base_type']
                        localized_filter_fields[key]['filter'] = value
            return localized_filter_fields

    '''
        Fetching data from underlying data sources for a node in AST, in the filter evaluation phase
            entity_type: the type of the node in AST;
            filter_fields: the fields have filter expressions for the node of the AST;
            supper_mappings_name: mapping names of mappings that declare the super node;
            filter_lst_obj_tag:
    '''
    def filter_data_fetcher(self, entity_type, filter_fields, super_mappings_name, filter_lst_obj_tag=False):
        result = dict()
        if len(super_mappings_name) == 0:
            mappings = self.mu.get_mappings_by_type(entity_type)
        else:
            mappings = self.mu.get_mappings_by_names([super_mappings_name])
        query_fields = filter_fields.keys()
        predicates = [self.inverse_phi(field) for field in query_fields]
        for mapping in mappings:
            mapping_name = mapping['name']
            logical_source = self.mu.get_logical_source_by_mapping(mapping)
            template = self.mu.get_subject_template_by_mapping(mapping)
            # may change if multiple key attributes
            key_attrs = [self.parse_template(template)[0]]
            poms = self.mu.get_poms_by_predicates(mapping, predicates)
            pred_attr = dict()
            constant_data = []
            filter_constant = []
            for pom in poms:
                predicate, object_map = self.mu.parse_pom(pom)
                phi_predicate = self.phi(predicate)
                object_map_type = self.mu.type_of_object_map(object_map)
                if object_map_type == 1:
                    reference_attribute = self.mu.get_reference(object_map)
                    pred_attr[phi_predicate] = reference_attribute
                elif object_map_type == 2:
                    constant_value, constant_datatype = self.mu.get_constant_value_type(object_map)
                    constant_data.append((phi_predicate, constant_value, constant_datatype))
                    filter_constant.append(phi_predicate)
                else:
                    pass
            localized_filter = self.localize_filter(entity_type, pred_attr, filter_fields, filter_constant)
            temp_result = self.executor(logical_source, key_attrs, True, localized_filter, None, constant_data, filter_lst_obj_tag)
            if temp_result.empty is not True:
                temp_result = self.refine_data_frame(temp_result, pred_attr, template, mapping_name)
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

    '''
        Filter Evaluation
            filter_ast: the abstract syntax tree of the filter expression;
            cpe: common prefix expressions;
            rse: repeated single expressions;
            super_filters: filter structure of the super tree;
            super_result: the result of super tree;
            supper_mapping_name: the mapping name of super node.
    '''
    def filter_evaluator(self, filter_ast, cpe, rse, super_filters={}, super_result=None, super_mapping_name=''):
        root_node_filter = filter_ast.get_current_filter()
        if len(root_node_filter) == 0:
            root_node_filter = {filter_ast.name + '-ALL': {}} # For type without filter provided expilicitly
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
                temp_result = self.filter_data_fetcher(entity_type, filter_fields, super_mapping_name, filter_lst_obj_tag)
                if symbolic_root_filter in rse:
                    self.single_cache[symbolic_root_filter] = copy.copy(temp_result)
            super_node_type = filter_ast.parent.name
            # current_node_type = filter_ast.name
            super_field = filter_ast.parent_edge
            if super_field != 'filter':
                if len(temp_result) == 0:
                    super_result = dict()
                else:
                    super_result = self.filter_join(super_result, temp_result, super_node_type, super_field)
            else:
                super_result = temp_result
            # check CPE
            if symbolic_new_filter in cpe:
                self.join_cache[symbolic_new_filter] = copy.copy(super_result)
        else:
            super_result = joined_result
        sub_filter_asts = filter_ast.get_sub_trees()
        for sub_filter_ast in sub_filter_asts:
            if len(super_result) > 0:
                super_result = self.filter_evaluator(sub_filter_ast, cpe, rse, new_filter, super_result)
        return super_result

    '''
        Join function in filter evaluation phase
    '''
    def filter_join(self, super_result, current_node_result, super_node_type, super_field):
        super_mappings = self.mu.get_mappings_by_type(super_node_type)
        predicates = [self.inverse_phi(field) for field in [super_field]]
        result2join = []
        supper_mappings2join = []
        for mapping in super_mappings:
            poms = self.mu.get_poms_by_predicates(mapping, predicates)
            for pom in poms:
                predicate, object_map = self.mu.parse_pom(pom)
                if self.mu.type_of_object_map(object_map) == 3:
                    parent_mapping, join_condition = self.mu.parse_rom(object_map)
                    child_field, parent_field = self.mu.parse_join_condition(join_condition)
                    if parent_mapping['name'] in current_node_result.keys():
                        result2join.append((mapping['name'], parent_mapping['name'], child_field, parent_field))
                        supper_mappings2join.append(mapping['name'])
        for mapping_key in super_result.keys():
            if mapping_key in supper_mappings2join:
                for (super_mapping_name, current_mapping_name, super_field, current_field) in result2join:
                    if super_mapping_name == mapping_key:
                        right_df = current_node_result[current_mapping_name]
                        right_df = right_df.drop(['iri'], axis=1)
                        left_new_column_name = mapping_key + '-' + super_field
                        right_new_column_name = current_mapping_name + '-' + current_field
                        if left_new_column_name not in list(super_result[mapping_key].columns):
                            super_result[mapping_key][left_new_column_name] = super_result[mapping_key][super_field]
                        super_result[mapping_key].set_index(left_new_column_name)  # set index
                        if right_new_column_name not in list(right_df.columns):
                            right_df[right_new_column_name] = right_df[current_field]
                        right_df.set_index(right_new_column_name)
                        super_result[mapping_key] = pd.merge(super_result[mapping_key], right_df, how='inner',
                                                             left_on=left_new_column_name,
                                                             right_on=right_new_column_name)
                        if right_new_column_name not in list(super_result[mapping_key].columns):
                            super_result[mapping_key][right_new_column_name] = super_result[mapping_key][left_new_column_name]
            else:
                for (super_mapping_name, current_mapping_name, super_field, current_field) in result2join:
                    if super_mapping_name != mapping_key:
                        left_new_column_name = super_mapping_name + '-' + super_field
                        if left_new_column_name in super_result[mapping_key].columns.values.tolist():
                            right_df = current_node_result[current_mapping_name]
                            right_df = right_df.drop(['iri'], axis=1)
                            right_new_column_name = current_mapping_name + '-' + current_field
                            super_result[mapping_key].set_index(left_new_column_name)  # set index
                            if right_new_column_name not in list(right_df.columns):
                                right_df[right_new_column_name] = right_df[current_field]
                            right_df.set_index(right_new_column_name)
                            super_result[mapping_key] = pd.merge(super_result[mapping_key], right_df, how='inner',
                                                                 left_on=left_new_column_name, right_on=right_new_column_name)
                            if right_new_column_name not in list(super_result[mapping_key].columns):
                                super_result[mapping_key][right_new_column_name] = super_result[mapping_key][left_new_column_name]
                        else:
                            if len(super_result.keys()) > len(supper_mappings2join):
                                super_result[mapping_key] = super_result[mapping_key][0:0]  # give it as empty
        return super_result

    def get_interface_sub_types(self, interface_name):
        sub_types = self.schema_ast[interface_name]['sub_types']
        return sub_types

    '''
        Query evaluation function
            query_ast: the abstract syntax tree of the GraphQL query
            mapping:
            ref:
            root_type_flag:
            filtered_root_mappings:
    '''
    def query_evaluator(self, query_ast, mapping=None, ref=None, root_type_flag=False, filtered_root_mappings=[]):
        result, mappings = [], []
        concept_type = query_ast['type']
        query_fields = [field['name'] for field in query_ast['fields']]
        if mapping is None:
            if len(filtered_root_mappings) > 0:
                filtered_root_mappings = [x for x in filtered_root_mappings if x != 'filter']
                mappings = self.mu.get_mappings_by_names(filtered_root_mappings)
            else:
                if concept_type in self.interfaces:
                    mappings = []
                    sub_types = self.get_interface_sub_types(concept_type)
                    for sub_type in sub_types:
                        mappings += self.mu.get_mappings_by_type(sub_type)
                else:
                    mappings = self.mu.get_mappings_by_type(concept_type)
        else:
            mappings.append(mapping)
        predicates = [self.inverse_phi(field) for field in query_fields]

        for mapping in mappings:
            logical_source = self.mu.get_logical_source_by_mapping(mapping)
            template = self.mu.get_subject_template_by_mapping(mapping)
            key_attrs = [self.parse_template(template)[0]]
            poms = self.mu.get_poms_by_predicates(mapping, predicates)
            attr_pred, constant_data = [], []
            ref_poms_pred_object_map = []
            result_join = defaultdict(list)
            for pom in poms:
                predicate, object_map = self.mu.parse_pom(pom)
                phi_predicate = self.phi(predicate)
                object_map_type = self.mu.type_of_object_map(object_map)
                if object_map_type == 3:
                    ref_poms_pred_object_map.append((phi_predicate, object_map))
                elif object_map_type == 1:
                    reference_attribute = self.mu.get_reference(object_map)
                    attr_pred.append((reference_attribute, phi_predicate))
                    key_attrs.append(reference_attribute)
                elif object_map_type == 2:
                    constant_value, constant_datatype = self.mu.get_constant_value_type(object_map)
                    constant_data.append((phi_predicate, constant_value, constant_datatype))
                else:
                    print('Unknown object map type')
            if root_type_flag is True:
                temp_result = self.executor(logical_source, None, False, None, ref, None, False, mapping['name'])
            else:
                temp_result = self.executor(logical_source, None, False, None, ref, None, False, '')

            if root_type_flag is True and self.sql_flag is False:
                temp_result = self.refine_json(temp_result, attr_pred, constant_data, template, True,
                                               mapping['name'], key_attrs, self.filtered_object_iri)
            else:
                temp_result = self.refine_json(temp_result, attr_pred, constant_data, template, False,'', key_attrs)

            self.sql_flag = False
            for (phi_predicate, object_map) in ref_poms_pred_object_map:
                new_query_ast = self.get_sub_ast(query_ast, phi_predicate)
                parent_mapping, join_condition = self.mu.parse_rom(object_map)
                child_field, parent_field = self.mu.parse_join_condition(join_condition)
                child_data = [{child_field: record[child_field]} for record in temp_result]
                ref_data = [x[child_field] for x in child_data]
                ref_data = list(set(ref_data))
                new_ref = (ref_data, parent_field)
                parent_data = self.query_evaluator(new_query_ast, parent_mapping, new_ref)
                new_ref = None
                result_join[phi_predicate].append((parent_data, join_condition, new_query_ast['wrapping_label']))
            if len(result_join) > 0:
                temp_result = self.incremental_optimized_join(temp_result, result_join)
            result += temp_result
        return result

    @staticmethod
    def join_base(temp_result, pred_key, data_join_lst):
        result = []
        for (join_data, join_condition, wrapping_label) in data_join_lst:
            new_formed_join_data = defaultdict(list)
            for record in join_data:
                # following copy field
                modified_field_name = join_condition['parent'] + 'ORIGINAL'
                if modified_field_name in record.keys():  # check if the data at the right side of the join contains a modified field
                    new_formed_join_data[record[modified_field_name]].append(record)
                else:
                    new_formed_join_data[record[join_condition['parent']]].append(record)
            for record in temp_result:
                new_record = record
                join_key_value = record[join_condition['child']]
                if pred_key not in new_record.keys() and wrapping_label != '0' and wrapping_label != '10':
                    new_record[pred_key] = []
                else:
                    if pred_key in new_record.keys():
                        new_field = pred_key + 'ORIGINAL'
                        # following copy field's data is used in case the original data has the same field name
                        # as the predicate stated in the mapping
                        new_record[new_field] = new_record[pred_key]
                if wrapping_label == '0' or wrapping_label == '10':
                    if len(new_formed_join_data[join_key_value]) > 0:
                        new_record[pred_key] = new_formed_join_data[join_key_value][0]
                else:
                    new_record[pred_key] += new_formed_join_data[join_key_value]
                if new_record not in result:
                    result.append(new_record)
        return result

    def incremental_multi_join(self, temp_result, result_join):
        result = []
        pool = mp.Pool(processes=4)
        mp_join_results = [pool.apply(self.join_base, args=(temp_result, pred_key, data_join_lst)) for pred_key, data_join_lst in result_join.items()]
        for mjr in mp_join_results:
            for e in mjr:
                if e not in result:
                    result.append(e)
        pool.close()
        return result

    @staticmethod
    def incremental_optimized_join(temp_result, result_join):
        result = []
        for pred_key, data_join_lst in result_join.items():
            for (join_data, join_condition, wrapping_label) in data_join_lst:
                new_formed_join_data = defaultdict(list)
                for record in join_data:
                    # following copy field
                    modified_field_name = join_condition['parent'] + 'ORIGINAL'
                    if modified_field_name in record.keys():  # check if the data at the right side of the join contains a modified field
                        new_formed_join_data[record[modified_field_name]].append(record)
                    else:
                        new_formed_join_data[record[join_condition['parent']]].append(record)
                for record in temp_result:
                    new_record = record
                    join_key_value = record[join_condition['child']]
                    if pred_key not in new_record.keys() and wrapping_label != '0' and wrapping_label != '10':
                        new_record[pred_key] = []
                    else:
                        if pred_key in new_record.keys():
                            new_field = pred_key + 'ORIGINAL'
                            # following copy field's data is used in case the original data has the same field name
                            # as the predicate stated in the mapping
                            new_record[new_field] = new_record[pred_key]
                    if wrapping_label == '0' or wrapping_label == '10':
                        if len(new_formed_join_data[join_key_value]) > 0:
                            new_record[pred_key] = new_formed_join_data[join_key_value][0]
                    else:
                        new_record[pred_key] += new_formed_join_data[join_key_value]
                    if new_record not in result:
                        result.append(new_record)
        return result

    '''
        Generic Resolver Function
        info:
        filter_condition:
        return: a list of json objects
    '''
    def generic_resolver_func(self, info, filter_condition):
        from generic_resolver.filter_utils import Filter_Utils
        result = []
        if len(filter_condition) > 0:
            fu = Filter_Utils()
            fu.parse_cond(filter_condition)
            dnf_lst = fu.simplify()
            self.set_symbol_field_maps(fu.field_exp_symbol, fu.symbol_field_exp)
            query_entry = info.field_nodes[0].name.value
            filter_asts, common_prefix, repeated_single_exp = self.generate_filter_asts(self.filter_fields_map,
                                                                                        self.symbol_field_exp, dnf_lst,
                                                                                        query_entry)
            for filter_ast in filter_asts:
                filter_df = self.filter_evaluator(filter_ast.children[0], common_prefix, repeated_single_exp)
                for key, value in filter_df.items():
                    df_columns = list(value.columns)
                    object_iri_lst = value['iri'].tolist()
                    if len(object_iri_lst) > 0:
                        if key in self.filtered_object_iri.keys():
                            self.filtered_object_iri[key] = list(set(self.filtered_object_iri[key] + object_iri_lst))
                        else:
                            self.filtered_object_iri[key] = list(set(object_iri_lst))
                    for column in df_columns:
                        if key in column:
                            attribute = column.split('-')[1]
                            column_value = value[column].tolist()
                            if attribute in self.filtered_object_columns[key].keys():
                                self.filtered_object_columns[key][attribute] += column_value
                                break
                            else:
                                self.filtered_object_columns[key] = {attribute: column_value}
                                break

            if len(self.filtered_object_iri.keys()) > 0:
                self.filtered_object_iri['filter'] = True
                query_ast = self.generate_query_ast(info)
                result = self.query_evaluator(query_ast['fields'][0], None, None, True, self.filtered_object_iri.keys())
        else:
            self.filtered_object_iri['filter'] = False
            field_type = info.field_nodes[0].selection_set.selections[0].kind
            if info.field_name in self.interface_query_entries and field_type == 'inline_fragment':
                '''
                This block is about query interfaces with inline fragments provided.
                
                '''
                inline_query_asts = self.generate_query_asts(info)
                for inline_query_ast in inline_query_asts:
                    temp_result = self.query_evaluator(inline_query_ast, None, None, True)
                    result += temp_result
            else:
                query_ast = self.generate_query_ast(info)
                result = self.query_evaluator(query_ast['fields'][0], None, None, True)
        self.reinitialize_ru_object()
        return result



    def reinitialize_ru_object(self):
        self.filtered_object_iri = dict()
        self.filtered_object_columns = defaultdict(defaultdict)
        self.join_cache = dict()
        self.single_cache = dict()
        self.field_exp_symbol = dict()
        self.symbol_field_exp = dict()
