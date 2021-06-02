from collections import deque
import json
from sympy.logic.boolalg import to_dnf
from sympy.logic.inference import satisfiable
import logging

'''
log debug
log info
log warning (default)
log error
log critical
'''

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler('filter.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.info('\n')
logger.info('----------NEW LOG----------')
#logging.basicConfig(filename ='filter.log',level = logging.DEBUG,format='%(asctime)s:%(levelname)s:%(message)s')

class Filter_Utils(object):
    def __init__(self):
        self.operator_stack = ['EOS']
        self.fields_stack = ['EOS']
        self.bool_exp = []
        self.field_symbol_index = 0
        self.field_exp_symbol_index = 0
        self.alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
        self.field_symbol = dict()
        self.symbol_field = dict()
        self.field_exp_symbol = dict()
        self.symbol_field_exp = dict()

        self.expression_str = []
        self.translated_expression_str = []
        self.operator_stack1 = ['EOS']
        self.fields_stack1 = ['EOS']
        self.negative_op_map = {'_neq': '_eq', '_nin': '_in', '_nlike': '_like', '_nilike': '_ilike'}
        #self.common_exp_symbols = set()

    #def set_Phi(self, file='o2graphql.json'):
     #   with open(file) as f:
      #      self.ontology_GraphQLschema = json.load(f)
       #     self.GraphQLschema_Ontology = self.ontology_GraphQLschema

    def check_type(self, condition):
        if isinstance(condition, list)==True:
            return 'LIST'
        if isinstance(condition, dict)==True:
            return 'DICT'
        if isinstance(condition, str)==True or isinstance(condition, int)==True:
            return 'BASIC_TYPE'

    def convert_field_name(self):
        field_name = ''
        for item in self.fields_stack[1:]:
            field_name += item
            field_name += '.'
        return field_name[0:-1]

    def translate_field_name(self, field_name):
        new_name = ''
        if field_name in self.field_symbol.keys():
            return self.field_symbol[field_name]
        else:
            quotient = int(self.field_symbol_index / 11)
            remainder = int(self.field_symbol_index % 11)
            for i in range(quotient + 1):
                new_name += self.alphabet[remainder]
            self.field_symbol_index += 1
            self.field_symbol[field_name] = new_name
            self.symbol_field[new_name] = field_name
            return new_name

    def translate_field_exp(self, field_exp):
        new_name = ''
        if field_exp in self.field_exp_symbol.keys():
            return self.field_exp_symbol[field_exp]
        else:
            quotient = int(self.field_exp_symbol_index / 11)
            remainder = int(self.field_exp_symbol_index % 11)
            for i in range(quotient + 1):
                new_name += self.alphabet[remainder]
            self.field_exp_symbol_index += 1
            self.field_exp_symbol[field_exp] = new_name
            self.symbol_field_exp[new_name] = field_exp
            return new_name

    def translate_whole_exp(self, exp_element):
        if exp_element.startswith('filter.')==True:
            return self.translate_field_name(exp_element)
        elif exp_element == '_and':
            return '&'
        elif exp_element == '_or':
            return '|'
        elif exp_element == '_not':
            return '~'
        elif exp_element == '_eq':
            return '_eq'
        elif exp_element == '_neq':
            return '_neq'
        elif exp_element == '_gt':
            return '_gt'
        elif exp_element == '_egt':
            return '_egt'
        elif exp_element == '_lt':
            return '_lt'
        elif exp_element == '_elt':
            return '_elt'
        else:
            return exp_element

    def simplify_bool_expression(self, bool_exp):
        simplified_bool_exp = []
        sbe = []
        for i in range(len(bool_exp) - 1):
            if bool_exp[i] in ['_and', '_or', '_not']:
                if bool_exp[i + 1] not in ['_and', '_or', '_not', 'EOS', ')']:
                    simplified_bool_exp.append(bool_exp[i])
                    sbe.append(self.translate_whole_exp(bool_exp[i]))
            else:
                simplified_bool_exp.append(bool_exp[i])
                sbe.append(self.translate_whole_exp(bool_exp[i]))
        print('ss', simplified_bool_exp)
        print('sbe', sbe)
        return sbe

    def convert_to_dnf(self, exp_list):
        exp_str = ''
        for item in exp_list:
            exp_str += item
        # print(satisfiable(exp_str))
        dnf_obj = to_dnf(exp_str, True, True)
        logger.info('dnf_obj')
        logger.info(dnf_obj)
        result = satisfiable(dnf_obj)
        return str(dnf_obj)

    def simplify2DNF(self, filter_condition):
        test_filter = {'filter':
            {
                '_and': [
                    {'ID': {'_eq': '1'}},
                    {'ID': {'_neq': '1'}}
                ]
            }
        }
        expression = self.parse('filter', filter_condition['filter'], [])
        logger.info('expression')
        logger.info(expression)
        exp_list_1 = self.simplify_bool_expression(expression)
        result = self.convert_to_dnf(exp_list_1)
        logger.info(exp_list_1)
        logger.info(result)
        logger.info('asdasd')

    def parse_cond(self, cond):
        if self.check_type(cond) == 'DICT':
            cond_length = len(cond)
            if cond_length > 1:
                i = 0
                self.operator_stack1.append('_and')
                # expression_str.append('(')
                for key, value in cond.items():
                    i += 1
                    if key.startswith('_'):
                        self.parse_cond({key: value})
                        if i < cond_length:
                            self.expression_str.append(self.operator_stack1[-1])
                            self.translated_expression_str.append(self.operator_stack1[-1])
                    else:
                        self.fields_stack1.append(key)
                        self.parse_cond(value)
                        if i < cond_length:
                            self.expression_str.append(self.operator_stack1[-1])
                            self.translated_expression_str.append(self.operator_stack1[-1])
                        self.fields_stack1.pop(-1)
                # expression_str.append(')')
                self.operator_stack1.pop(-1)
            elif cond_length == 0:
                self.expression_str.append('NULL')
                self.translated_expression_str.append('NULL')
            else:
                key, value = list(cond.items())[0]
                if key in ['_eq', '_neq', '_gt', '_egt', '_lt', '_elt', '_in', '_nin', '_like', '_nlike', '_ilike',
                           '_nilike']:
                    if key in ['_neq', '_nin', '_nlike', '_nilike']:
                        self.operator_stack1.append('_not')
                        self.expression_str.append('_not')
                        self.translated_expression_str.append('_not')
                        self.expression_str.append('(')
                        self.translated_expression_str.append('(')
                        new_key = self.negative_op_map[key]
                        if key == '_nin':
                            value = str(value)
                        self.parse_cond({new_key: value})
                        # expression_str.append('&')
                        self.expression_str.append(')')
                        self.translated_expression_str.append(')')
                        # expression_str.append(')')
                        self.operator_stack1.pop(-1)
                    else:
                        field_name = ''
                        for field in self.fields_stack1[1:]:
                            field_name += field
                            field_name += '.'
                        self.expression_str.append(field_name[0:-1])
                        self.expression_str.append(key)
                        if key == '_in':
                            value = str(value)
                        self.expression_str.append(value)
                        new_symbol = self.translate_field_exp((field_name[0:-1], key, value))
                        self.translated_expression_str.append(new_symbol)
                else:
                    # no need to append field_stack here
                    if key not in ['_and', '_or', '_not']:
                        # if fields_stack1[-1] is not key:
                        self.fields_stack1.append(key)
                        if key in ['_in', '_nin']:
                            value = str(value)
                        self.parse_cond(value)
                        self.fields_stack1.pop(-1)
                    else:
                        self.operator_stack1.append(key)
                        if key == '_not':
                            self.expression_str.append('_not')
                            self.translated_expression_str.append('_not')
                            self.expression_str.append('(')
                            self.translated_expression_str.append('(')
                            self.parse_cond(value)
                            # expression_str.append('&')
                            self.expression_str.append(')')
                            self.translated_expression_str.append(')')
                            # expression_str.append(')')
                            self.operator_stack1.pop(-1)
                        elif key == '_or':
                            self.expression_str.append('(')
                            self.translated_expression_str.append('(')
                            self.parse_cond(value)
                            # expression_str.append('&')
                            self.expression_str.append(')')
                            self.translated_expression_str.append(')')
                            self.operator_stack1.pop(-1)
                        else:
                            # key is and
                            # expression_str.append('(')
                            self.parse_cond(value)
                            # expression_str.append('&')
                            # expression_str.append(')')
                            self.operator_stack1.pop(-1)
        if self.check_type(cond) == 'LIST':
            i = 0
            cond_length = len(cond)
            for sub_cond in cond:
                # print(sub_cond)
                self.parse_cond(sub_cond)
                i += 1
                if i < cond_length:
                    self.expression_str.append(self.operator_stack1[-1])
                    self.translated_expression_str.append(self.operator_stack1[-1])

    def simplify(self):
        dnf_exp_lst = []
        exp_str = ''
        print('self translated_expression_str', self.translated_expression_str)
        for element in self.translated_expression_str:
            if element == '_and':
                exp_str += ' & '
            elif element == '_or':
                exp_str += ' | '
            elif element == '_not':
                exp_str += '~'
            else:
                exp_str += element
        #print('exp_str', exp_str)
        simplified_exp_str = str(to_dnf(exp_str, True))
        print('DNF_STR', simplified_exp_str)
        # result = satisfiable(dnf_obj)
        # dnf_exp_lst = str(simplified_exp).split('|')
        if '|' not in simplified_exp_str:
            #print('simplified_exp_str', simplified_exp_str)
            cnf_lst = simplified_exp_str.split('&')
            cnf_lst = [x.strip() for x in cnf_lst]
            dnf_exp_lst.append(cnf_lst)
        else:
            #common_symbols_set = set(self.symbol_field_exp.keys())
            for cnf in simplified_exp_str.split('|'):
                #print('cnf', cnf)
                if '&' in cnf:
                    cnf_lst = cnf.strip()[1:-1].split('&')
                    cnf_lst = [x.strip() for x in cnf_lst]
                else:
                    cnf_lst = [cnf.strip()]
                dnf_exp_lst.append(cnf_lst)
                #common_symbols_set = set(common_symbols_set.intersection(set(cnf_lst)))
        #print(dnf_exp_lst)
        #self.common_exp_symbols = common_symbols_set
        return dnf_exp_lst

'''
    def parse(self, filter_field, filter_condition, expression):
        expression = expression
        if filter_field in ['_and', '_or', '_not']:
            if self.operator_stack[-1] != filter_field:
                self.operator_stack.append(filter_field)
                if filter_field == '_not':
                    self.bool_exp.append('_not')
                    expression.append('_not')
                self.bool_exp.append('(')
                expression.append('(')
        else:
            if filter_field not in ['_eq', '_neq']:
                self.fields_stack.append(filter_field)
        if self.check_type(filter_condition) == 'LIST':
            for item in filter_condition:
                self.parse(filter_field, item, expression)
            if self.operator_stack[-1] != 'EOS':
                # After parsing a list of AND expression or OR expression, popping tops of fields_stack and operator_stack
                self.bool_exp.append(')')
                expression.append(')')
                self.fields_stack.pop(-1)
                self.operator_stack.pop(-1)
                self.bool_exp.append(self.operator_stack[-1])
                expression.append(self.operator_stack[-1])
        if self.check_type(filter_condition) == 'DICT':
            if len(filter_condition) > 1 and filter_field != '_and':
                repeated_field = self.fields_stack[-1]
                self.fields_stack.pop(-1)
                new_condition = []
                for (key, value) in filter_condition.items():
                    new_condition.append({repeated_field: {key: value}})
                self.parse('_and', new_condition, expression)
            else:
                for (key, value) in filter_condition.items():
                    if len(value) == 0:
                        break
                    self.parse(key, value, expression)
                    if self.operator_stack[-1] == '_not':
                        self.bool_exp.append(')')
                        expression.append(')')
                        # self.fields_stack.pop(-1)
                        self.operator_stack.pop(-1)
                        self.bool_exp.append(self.operator_stack[-1])
                        expression.append(self.operator_stack[-1])
        if self.check_type(filter_condition) == 'BASIC_TYPE':
            new_field_name = self.convert_field_name()
            # self.bool_exp.append(new_field_name)
            # self.bool_exp.append(filter_field)
            # self.bool_exp.append(filter_condition)
            new_symbol = self.translate_field_exp((new_field_name, filter_field, filter_condition))
            expression.append(new_field_name)
            expression.append(filter_field)
            expression.append(filter_condition)
            self.bool_exp.append(new_symbol)
            if self.operator_stack[-1] not in ['EOS', '_not']:
                self.bool_exp.append(self.operator_stack[-1])
                expression.append(self.operator_stack[-1])
            self.fields_stack.pop(-1)
        return expression
'''


'''
ru = Filter_Utils()

result = ru.parse('filter', filter13['filter'], [])
#print(result)
exp_list_1 = ru.simplify_bool_expression(result)
print(ru.bool_exp)
exp_list = ru.simplify_bool_expression(ru.bool_exp)
print(exp_list)
#print(field_symbol)
#print(symbol_field)
#print(field_exp_symbol)
#print(bool_exp)
print(ru.convert_to_dnf(exp_list))
print(ru.symbol_field_exp)

ru = Filter_Utils()
'''