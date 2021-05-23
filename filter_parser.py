from collections import deque
import json
from sympy.logic.boolalg import to_dnf
from sympy.logic.inference import satisfiable

filter1= {
    'filter': {
        '_and': [
            {
                'hasOutputStructure': {
                    'hasComposition': {
                        '_or': [
                            {'ReducedFormula': {'_eq': 'SiC'}},
                            {'AnonymousFormula': {'_eq': 'AB'}}
                        ]
                    }
                },
                'ID': {
                    '_eq': '1',
                    '_neq': '2'
                }
            }
        ]
    }
}
filter2 = {'filter':
               {
                   '_and': [
                       {'ID': {'_eq': '1'}},
                       {'hasOutputStructure':
                            {'hasComposition':
                                 {'_or': [
                                     {'ReducedFormula': {'_eq': 'SiC'}},
                                     {'AnonymousFormula': {'_eq': 'AB'}}
                                 ]}
                            }
                       }
                   ]
               }
}
filter3 = {'filter': {
                'ID': {
                    '_eq': '1',
                    '_neq': '1'
                }}}
filter4 = {'filter':{}}
filter5 = {'filter':
               {
                   '_and': [
                       {},
                       {'hasOutputStructure':
                            {'hasComposition':
                                 {'_or': [
                                     {'ReducedFormula': {'_eq': 'SiC'}},
                                     {'AnonymousFormula': {'_eq': 'AB'}}
                                 ]}
                            }
                       }
                   ]
               }
}
filter6 = {'filter':
               {'_and':[
                   {'_not':{'ID':{'_eq': '1'}}},
                   {'ID':{'_eq':'1'}}
               ]}
          }
filter7 = {
    'filter':{
        '_not':{
            '_and':[
                {'ID':{'_eq': '2'}},
                {'ID':{'_neq': '7'}}
            ]
        }
    }
}
filter8 ={'filter': {'_not':{}}}
filter9 ={'filter': {'_or':{}}}
filter11 ={'filter': {'_and':{}}}
filter10 = {'filter':{'_and':[{'_not':{}}, {'ID':{'_eq':'1'}}]}}
filter12 = {'filter':{'hasOutputStructure':{}}}

filter13 = {'filter':
               {
                   '_and': [
                       {'ID': {'_eq': '1'}},
                       {'ID': {'_neq': '1'}}
                   ]
               }
}
filter14 = {
    'filter':{
        'ID':{'_eq': '1', '_neq':'2'},
        'hasOutputStructure':
                            {'hasComposition':
                                 {'_or': [
                                     {'ReducedFormula': {'_eq': 'SiC'}},
                                     {'AnonymousFormula': {'_eq': 'AB'}}
                                 ]}
                            }

    }
}
filter15 = {
    'filter':{
        'ID':{'_eq': '1', '_neq':'2'},
        'hasOutputStructure':
                            {'hasComposition':
                                 {'_and': {
                                     'ReducedFormula': {'_eq': 'SiC'},
                                     'AnonymousFormula': {'_eq': 'AB'}
                                 }
                                 }
                            }

    }
}
filter16 = {
    'filter':{
        'ID':{'_eq': '1'},
        'ID1': {'_eq': '1'}
    }
}
filter17 = {
    'filter':{
        'ID1':{'_eq': '1', '_neq': '3'}
        #'ID2':{'_eq': '1', '_neq': '3'}
    }
}

operator_stack = ['EOS']
fields_stack = ['EOS']
bool_exp = []
field_symbol_index = 0
field_exp_symbol_index = 0
alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
field_symbol = dict()
symbol_field = dict()
field_exp_symbol = dict()
field_exp_symbol_dict = dict()
symbol_field_exp = dict()
symbol_field_exp_dict = dict()

def check_type(condition):
    if isinstance(condition, list) is True:
        return 'LIST'
    if isinstance(condition, dict) is True:
        return 'DICT'
    if isinstance(condition, str) is True or isinstance(condition, int) is True:
        return 'BASIC_TYPE'

def convert_field_name(field_stack):
    field_name = ''
    for item in fields_stack[1:]:
        field_name += item
        field_name += '.'
    return field_name[0:-1]

def translate_field_name(field_name):
    new_name = ''
    global field_symbol_index
    global field_symbol
    global symbol_field
    if field_name in field_symbol.keys():
        return field_symbol[field_name]
    else:
        quotient = int(field_symbol_index / 11)
        remainder = int(field_symbol_index % 11)
        for i in range(quotient + 1):
            new_name += alphabet[remainder]
        field_symbol_index += 1
        field_symbol[field_name] = new_name
        symbol_field[new_name] = field_name
        return new_name

def translate_field_exp(field_exp):
    new_name = ''
    global field_exp_symbol_index
    global field_exp_symbol
    global symbol_field_exp
    if field_exp in field_exp_symbol.keys():
        return field_exp_symbol[field_exp]
    else:
        quotient = int(field_exp_symbol_index / 11)
        remainder = int(field_exp_symbol_index % 11)
        for i in range(quotient + 1):
            new_name += alphabet[remainder]
        field_exp_symbol_index += 1
        field_exp_symbol[field_exp] = new_name
        symbol_field_exp[new_name] = field_exp
        return new_name

def translate_whole_exp(exp_element):
    if exp_element.startswith('filter.') is True:
        return translate_field_name(exp_element)
    elif exp_element is '_and':
        return '&'
    elif exp_element is '_or':
        return '|'
    elif exp_element is '_not':
        return '~'
    elif exp_element is '_eq':
        return '_eq'
    elif exp_element is '_neq':
        return '_neq'
    elif exp_element is '_gt':
        return '_gt'
    elif exp_element is '_egt':
        return '_egt'
    elif exp_element is '_lt':
        return '_lt'
    elif exp_element is '_elt':
        return '_elt'
    else:
        return exp_element

def parse(filter_field, filter_condition, expression):
    expression = expression
    global operator_stack
    global fields_stack
    global bool_exp
    if filter_field in ['_and', '_or', '_not']:
        if operator_stack[-1] is not filter_field:
            operator_stack.append(filter_field)
            if filter_field is '_not':
                bool_exp.append('_not')
                expression.append('_not')
            bool_exp.append('(')
            expression.append('(')
        else:
            operator_stack.append(filter_field)
            if filter_field is '_not':
                bool_exp.append('_not')
                expression.append('_not')
            bool_exp.append('(')
            expression.append('(')
    else:
        if filter_field not in ['_eq', '_neq']:
            if fields_stack[-1] is not filter_field:
                fields_stack.append(filter_field)
    if check_type(filter_condition) is 'LIST':
        for item in filter_condition:
            parse(filter_field, item, expression)
        if operator_stack[-1] is not 'EOS':
            #After parsing a list of AND expression or OR expression, popping tops of fields_stack and operator_stack
            bool_exp.append(')')
            expression.append(')')
            fields_stack.pop(-1)
            operator_stack.pop(-1)
            bool_exp.append(operator_stack[-1])
            expression.append(operator_stack[-1])
    if check_type(filter_condition) is 'DICT':
        if len(filter_condition) >1:
            print(filter_condition.keys())
            if not list(filter_condition.keys())[0].startswith('_'):
                print('a')
                print(filter_condition)
                new_condition = []
                for key, value in filter_condition.items():
                    new_condition.append({key:value})
                print(new_condition)
                operator_stack.append('_and')
                parse('_and', new_condition, expression)
            else:
                if operator_stack[-1] is 'EOS':
                    repeated_field = fields_stack[-1]
                    fields_stack.pop(-1)
                    new_condition = []
                    for (key, value) in filter_condition.items():
                        new_condition.append({repeated_field: {key: value}})
                    parse('_and', new_condition, expression)
                else:
                    repeated_field = fields_stack[-1]
                    #fields_stack.pop(-1)
                    new_condition = []
                    for (key, value) in filter_condition.items():
                        new_condition.append({repeated_field: {key:value}})
                    parse('_and', new_condition, expression)
                    operator_stack.pop(-1)
        else:
            for (key, value) in filter_condition.items():
                if len(value) is 0:
                    break
                parse(key, value, expression)
                if operator_stack[-1] is '_not':
                    bool_exp.append(')')
                    expression.append(')')
                    #fields_stack.pop(-1)
                    operator_stack.pop(-1)
                    bool_exp.append(operator_stack[-1])
                    expression.append(operator_stack[-1])
    if check_type(filter_condition) is 'BASIC_TYPE':
        new_field_name = convert_field_name(fields_stack)
        #bool_exp.append(new_field_name)
        #bool_exp.append(filter_field)
        #bool_exp.append(filter_condition)
        new_symbol = translate_field_exp((new_field_name, filter_field, filter_condition))
        expression.append(new_field_name)
        expression.append(filter_field)
        expression.append(filter_condition)
        bool_exp.append(new_symbol)
        if operator_stack[-1] not in ['EOS', '_not']:
            bool_exp.append(operator_stack[-1])
            expression.append(operator_stack[-1])
        fields_stack.pop(-1)
    return expression

def simplify_bool_expression(bool_exp):
    simplified_bool_exp = []
    sbe = []
    for i in range(len(bool_exp)-1):
        if bool_exp[i] in ['_and', '_or', '_not']:
            if bool_exp[i+1] not in ['_and', '_or', '_not', 'EOS',')']:
                simplified_bool_exp.append(bool_exp[i])
                sbe.append(translate_whole_exp(bool_exp[i]))
        else:
            simplified_bool_exp.append(bool_exp[i])
            sbe.append(translate_whole_exp(bool_exp[i]))
    print(simplified_bool_exp)
    return sbe

def convert_to_dnf(exp_list):
    exp_str = ''
    for item in exp_list:
        exp_str += item
    #print(satisfiable(exp_str))
    dnf_obj = to_dnf(exp_str, True, True)
    print(exp_str)
    result = satisfiable(dnf_obj)
    return str(dnf_obj)



#result = parse('filter', filter17['filter'], [])
#print(result)
#exp_list_1 = simplify_bool_expression(result)
#print(exp_list_1)
#print(result)
#exp_list = simplify_bool_expression(bool_exp)
#print(exp_list)
#print(field_symbol)
#print(symbol_field)
#print(field_exp_symbol)
#print(bool_exp)
#print(convert_to_dnf(exp_list))
#print(symbol_field_exp)

expression_str = []
translated_expression_str = []
operator_stack1 = ['EOS']
fields_stack1 = ['EOS']
negative_op_map = {'_neq': '_eq', '_nin':'_in', '_nlike': '_like', '_nilike': '_ilike'}
def parse_cond(cond):
    if check_type(cond) is 'DICT':
        cond_length = len(cond)
        if cond_length >1:
            i = 0
            operator_stack1.append('_and')
            #expression_str.append('(')
            for key, value in cond.items():
                #print({key: value}, expression)
                i += 1
                if key.startswith('_'):
                    parse_cond({key:value})
                    if i < cond_length:
                        expression_str.append(operator_stack1[-1])
                        translated_expression_str.append(operator_stack1[-1])
                else:
                    fields_stack1.append(key)
                    parse_cond(value)
                    if i < cond_length:
                        expression_str.append(operator_stack1[-1])
                        translated_expression_str.append(operator_stack1[-1])
                    fields_stack1.pop(-1)
            #expression_str.append(')')
            operator_stack1.pop(-1)
        elif cond_length is 0:
            expression_str.append('NULL')
            translated_expression_str.append('NULL')
        else:
            key, value = list(cond.items())[0]
            if key in ['_eq', '_neq', '_gt', '_egt', '_lt', '_elt', '_in', '_nin', '_like', '_nlike', '_ilike', '_nilike']:
                if key in ['_neq', '_nin', '_nlike', '_nilike']:
                    operator_stack1.append('_not')
                    expression_str.append('_not')
                    translated_expression_str.append('_not')
                    expression_str.append('(')
                    translated_expression_str.append('(')
                    new_key = negative_op_map[key]
                    parse_cond({new_key:value})
                    # expression_str.append('&')
                    expression_str.append(')')
                    translated_expression_str.append(')')
                    # expression_str.append(')')
                    operator_stack1.pop(-1)
                else:
                    field_name = ''
                    for field in fields_stack1[1:]:
                        field_name += field
                        field_name += '.'
                    #print(field_name[0:-1],key, value)
                    expression_str.append(field_name[0:-1])
                    expression_str.append(key)
                    expression_str.append(value)
                    new_symbol = translate_field_exp((field_name[0:-1], key, value))
                    translated_expression_str.append(new_symbol)
            else:
                #print(value)
                # no need to append field_stack here
                if key not in ['_and', '_or', '_not']:
                    #if fields_stack1[-1] is not key:
                    fields_stack1.append(key)
                    parse_cond(value)
                    fields_stack1.pop(-1)
                else:
                    operator_stack1.append(key)
                    if key is '_not':
                        expression_str.append('_not')
                        translated_expression_str.append('_not')
                        expression_str.append('(')
                        translated_expression_str.append('(')
                        parse_cond(value)
                        # expression_str.append('&')
                        expression_str.append(')')
                        translated_expression_str.append(')')
                        #expression_str.append(')')
                        operator_stack1.pop(-1)
                    elif key is '_or':
                        expression_str.append('(')
                        translated_expression_str.append('(')
                        parse_cond(value)
                        #expression_str.append('&')
                        expression_str.append(')')
                        translated_expression_str.append(')')
                        operator_stack1.pop(-1)
                    else:
                        #key is and
                        #expression_str.append('(')
                        parse_cond(value)
                        #expression_str.append('&')
                        #expression_str.append(')')
                        operator_stack1.pop(-1)
    if check_type(cond) is 'LIST':
        #print('LIST', cond)
        i = 0
        cond_length = len(cond)
        for sub_cond in cond:
            #print(sub_cond)
            parse_cond(sub_cond)
            i += 1
            if i < cond_length:
                expression_str.append(operator_stack1[-1])
                translated_expression_str.append(operator_stack1[-1])


#print(fields_stack1)
#print(operator_stack1)
#print(expression_str)
#translate_whole_exp(expression_str)

def simplify(exp):
    common_exp_symbols = []
    print('exp', exp)
    dnf_exp_lst = []
    exp_str = ''
    for element in exp:
        if element is '_and':
            exp_str += ' & '
        elif element is '_or':
            exp_str += ' | '
        elif element is '_not':
            exp_str += '~'
        else:
            exp_str += element
    simplified_exp_str = str(to_dnf(exp_str, True))
    #result = satisfiable(dnf_obj)
    #dnf_exp_lst = str(simplified_exp).split('|')
    #print(str(simplified_exp))
    if '|' not in simplified_exp_str:
        cnf_lst = simplified_exp_str.split('&')
        cnf_lst = [x.strip() for x in cnf_lst]
        dnf_exp_lst.append(cnf_lst)
    else:
        common_symbols_set = set(symbol_field_exp.keys())
        for cnf in simplified_exp_str.split('|'):
            #print('cnf', cnf.strip()[1:-1])
            cnf_lst = cnf.strip()[1:-1].split('&')
            cnf_lst = [x.strip() for x in cnf_lst]
            dnf_exp_lst.append(cnf_lst)
            common_symbols_set = set(common_symbols_set.intersection(set(cnf_lst)))
    #print(dnf_exp_lst)
    #print(common_symbols_set)
    return dnf_exp_lst

def convert2dict(exp_lst):
    for exp in exp_lst:
        print('exp', exp)

parse_cond(filter14)
#simplify(expression_str)
print(translated_expression_str)
result = simplify(translated_expression_str)
print(field_exp_symbol)
print(symbol_field_exp)
convert2dict(result)