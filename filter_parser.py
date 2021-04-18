from collections import deque
import json

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
filter3 = {
'filter': {



                'ID': {
                    '_eq': '1',
                    '_neq': '2'
                }


    }
}
def tokenize(bool_exp):
    for (key, value) in bool_exp.items():
        print(0)

def check_type(condition):
    if isinstance(condition, list) is True:
        return 'LIST'
    if isinstance(condition, dict) is True:
        return 'DICT'
    if isinstance(condition, str) is True or isinstance(condition, int) is True:
        return 'BASIC_TYPE'

operator_stack = ['EOS']
fields_stack = ['EOS']
bool_exp = []

def translate_field_name(field_stack):
    field_name = ''
    for item in fields_stack[1:]:
        field_name += item
        field_name += '.'
    return field_name[0:-1]


def parse(filter_field, filter_condition):
    global operator_stack
    global fields_stack
    global bool_exp
    if filter_field in ['_and', '_or', '_not']:
        if operator_stack[-1] is not filter_field:
            operator_stack.append(filter_field)
    else:
        if filter_field not in ['_eq', '_neq']:
            fields_stack.append(filter_field)
    if check_type(filter_condition) is 'LIST':
        for item in filter_condition:
            parse(filter_field, item)
        if operator_stack[-1] is not 'EOS':
            operator_stack.pop(-1)
            bool_exp.append(operator_stack[-1])
            fields_stack.pop(-1)
    if check_type(filter_condition) is 'DICT':
        if len(filter_condition) >1 and filter_field is not '_and':
            repeated_field = fields_stack[-1]
            fields_stack.pop(-1)
            new_condition = []
            for (key, value) in filter_condition.items():
                new_condition.append({repeated_field:{key:value}})
            parse('_and', new_condition)
        else:
            for (key, value) in filter_condition.items():
                parse(key, value)
    if check_type(filter_condition) is 'BASIC_TYPE':
        bool_exp.append(translate_field_name(fields_stack))
        bool_exp.append(filter_field)
        bool_exp.append(filter_condition)
        if operator_stack[-1] is not 'EOS':
            bool_exp.append(operator_stack[-1])
        fields_stack.pop(-1)

def simplify_bool_expression(bool_exp):
    simplified_bool_exp = []
    for i in range(len(bool_exp)-1):
        if bool_exp[i] in ['_and', '_or', '_not']:
            if bool_exp[i+1] not in ['_and', '_or', '_not', 'EOS']:
                simplified_bool_exp.append(bool_exp[i])
        else:
            simplified_bool_exp.append(bool_exp[i])
    print(simplified_bool_exp)

parse('filter', filter1['filter'])
simplify_bool_expression(bool_exp)
#print(operator_stack)
#print(fields_stack)
print(bool_exp)