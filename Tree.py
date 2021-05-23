from collections import defaultdict

common_prefix_exps = set()

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


def newFilter(super_filters = None, current_filter = None):
    return 0

'''
filter_type_map = {
        'CalculationFilter': 'Calculation',
        'StructureFilter': 'Structure',
        'CompositionFilter': 'Composition',
        'SpaceGroupFilter': 'SpaceGroup'
    }
'''

schema = {'Query': {'CalculationList': {'base_type': 'Calculation', 'wrapping_label': '210'}, 'StructureList': {'base_type': 'Structure', 'wrapping_label': '210'}, 'CompositionList': {'base_type': 'Composition', 'wrapping_label': '210'}, 'SpaceGroupList': {'base_type': 'SpaceGroup', 'wrapping_label': '210'}, 'getSpaceGroupBy': {'base_type': 'SpaceGroup', 'wrapping_label': '210'}}, 'Calculation': {'hasOutputStructure': {'base_type': 'Structure', 'wrapping_label': '1210'}, 'ID': {'base_type': 'String', 'wrapping_label': '10'}}, 'Structure': {'StructureID': {'base_type': 'String', 'wrapping_label': '10'}, 'hasComposition': {'base_type': 'Composition', 'wrapping_label': '0'}, 'hasSpaceGroup': {'base_type': 'SpaceGroup', 'wrapping_label': '0'}}, 'Composition': {'ReducedFormula': {'base_type': 'String', 'wrapping_label': '0'}, 'AnonymousFormula': {'base_type': 'String', 'wrapping_label': '0'}}, 'SpaceGroup': {'SpaceGroupID': {'base_type': 'String', 'wrapping_label': '0'}, 'SpaceGroupSymbol': {'base_type': 'String', 'wrapping_label': '0'}}, 'A': {'SpaceGroupID': {'base_type': 'Int', 'wrapping_label': '0'}}, 'CalculationFilter': {'hasOutputStructure': {'base_type': 'StructureFilter', 'wrapping_label': '0'}, 'ID': {'base_type': 'StringFilter', 'wrapping_label': '0'}, '_and': {'base_type': 'CalculationFilter', 'wrapping_label': '20'}, '_or': {'base_type': 'CalculationFilter', 'wrapping_label': '20'}, '_not': {'base_type': 'CalculationFilter', 'wrapping_label': '0'}}, 'StructureFilter': {'hasSpaceGroup': {'base_type': 'SpaceGroupFilter', 'wrapping_label': '0'}, 'hasComposition': {'base_type': 'CompositionFilter', 'wrapping_label': '0'}, '_and': {'base_type': 'StructureFilter', 'wrapping_label': '20'}, '_or': {'base_type': 'StructureFilter', 'wrapping_label': '20'}, '_not': {'base_type': 'StructureFilter', 'wrapping_label': '0'}}, 'CompositionFilter': {'ReducedFormula': {'base_type': 'StringFilter', 'wrapping_label': '0'}, 'AnonymousFormula': {'base_type': 'StringFilter', 'wrapping_label': '0'}, '_and': {'base_type': 'CompositionFilter', 'wrapping_label': '20'}, '_or': {'base_type': 'CompositionFilter', 'wrapping_label': '20'}, '_not': {'base_type': 'CompositionFilter', 'wrapping_label': '0'}}, 'SpaceGroupFilter': {'SpaceGroupID': {'base_type': 'StringFilter', 'wrapping_label': '0'}, 'SpaceGroupSymbol': {'base_type': 'StringFilter', 'wrapping_label': '0'}, '_and': {'base_type': 'SpaceGroupFilter', 'wrapping_label': '20'}, '_or': {'base_type': 'SpaceGroupFilter', 'wrapping_label': '20'}, '_not': {'base_type': 'SpaceGroupFilter', 'wrapping_label': '0'}}, 'StringFilter': {'_eq': {'base_type': 'String', 'wrapping_label': '0'}, '_neq': {'base_type': 'String', 'wrapping_label': '0'}, '_gt': {'base_type': 'String', 'wrapping_label': '0'}, '_egt': {'base_type': 'String', 'wrapping_label': '0'}, '_lt': {'base_type': 'String', 'wrapping_label': '0'}, '_elt': {'base_type': 'String', 'wrapping_label': '0'}, '_in': {'base_type': 'String', 'wrapping_label': '20'}, '_nin': {'base_type': 'String', 'wrapping_label': '20'}, '_like': {'base_type': 'String', 'wrapping_label': '0'}, '_ilike': {'base_type': 'String', 'wrapping_label': '0'}, '_nlike': {'base_type': 'String', 'wrapping_label': '0'}, '_nilike': {'base_type': 'String', 'wrapping_label': '0'}}}


filter_fields_map = {
        ('CalculationList', 'filter'): 'Calculation',
        ('Calculation', 'hasOutputStructure'): 'Structure',
        ('Calculation', 'ID'): 'String',
        ('Structure', 'hasComposition'): 'Composition',
        ('Structure', 'hasSpaceGroup'): 'SpaceGroup',
        ('Composition', 'ReducedFormula'): 'String',
        ('Composition', 'AnonymousFormula'): 'String',
        ('SpaceGroup', 'SpaceGroupID'): 'String',
        ('SpaceGroup', 'SpaceGroupSymbol'): 'String'
    }
symbol_exp_dict = {'A': ('filter.hasOutputStructure.hasComposition.ReducedFormula', '_eq', 'SiC'),
                       'B': ('filter.ID', '_eq', '1'), 'C': ('filter.ID', '_eq', '2')}
#exp_symbol_dict = {('filter.hasOutputStructure.hasComposition.ReducedFormula', '_eq', 'SiC'): 'A',('filter.ID', '_eq', '1'): 'B', ('filter.ID', '_eq', '2'): 'C'}


def generateFilterAST(filter_fields_map, symbol_exp_dict, conjunctive_exp, entry = 'CalculationList'):
    fields_filter_dict = defaultdict(list)
    for exp in conjunctive_exp:
        if exp[0] is '~':
            cond = symbol_exp_dict[exp[1]]
            field = cond[0]
            new_cond = {'field': field.split('.')[-1], 'operator': cond[1], 'value': cond[2], 'negation': True, 'symbol': exp}
            fields_filter_dict[field].append(new_cond)
        else:
            cond = symbol_exp_dict[exp]
            field = cond[0]
            new_cond = {'field': field.split('.')[-1], 'operator': cond[1], 'value': cond[2], 'negation': False, 'symbol': exp}
            fields_filter_dict[field].append(new_cond)
    field_filters = fields_filter_dict.items()
    # print(field_filters)
    field_filters = sorted(field_filters, key=lambda f: len(f[0].split('.')))
    filter_ast = AST('root')
    # filter_ast.add_child_edge('filter')
    for field_filter in field_filters:
        print(field_filter)
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
    return filter_ast

def generateFilterASTs(filter_fields_map, symbol_exp_dict, conjunctive_exp_lst, entry = 'CalculationList'):
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
                new_cond = {'field': field.split('.')[-1], 'operator': cond[1], 'value': cond[2], 'negation': True, 'symbol': exp}
                fields_filter_dict[field].append(new_cond)
            else:
                cond = symbol_exp_dict[exp]
                field = cond[0]
                new_cond = {'field': field.split('.')[-1], 'operator': cond[1], 'value': cond[2], 'negation': False, 'symbol': exp}
                fields_filter_dict[field].append(new_cond)
        field_filters = fields_filter_dict.items()
        # print(field_filters)
        field_filters = sorted(field_filters, key=lambda f: len(f[0].split('.')))
        filter_ast = AST('root')
        # filter_ast.add_child_edge('filter')
        for field_filter in field_filters:
            print(field_filter)
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



def FilterEvaluator(filter_AST, super_filters = None, super_result = None):
    root_node_filter = filter_AST.getCurrentFilter()
    if root_node_filter is not None:
        print('current_filter',root_node_filter)
    new_filter = newFilter()
    joined_result = None
    if joined_result is None:
        temp_result = None
        if temp_result is None:
            type = ''
            filter_fields = []
            super_mappings_name = []
            #temp_result = DataFetcher()
            #if current node filter is a repeated expression
            #Join
            # if newfilter is a common prefix expression

    else:
        super_result = joined_result
    sub_filter_ASTs = filter_AST.getSubTrees()
    for ast in sub_filter_ASTs:
        FilterEvaluator(ast)

queryAST = {'name': 'Query', 'type': '', 'fields':
    [{'name': 'CalculationList', 'type': 'Calculation',
      'fields': [{'name': 'hasOutputStructure', 'type': 'Structure', 'fields': [{'name': 'hasComposition', 'type': 'Composition', 'fields': [{'name': 'ReducedFormula', 'type': 'String', 'fields': [], 'wrapping_label': '0'}], 'wrapping_label': '0'}], 'wrapping_label': '1210'}], 'wrapping_label': '210'}]}
root_type = queryAST['fields'][0]['type']

def QueryEvaluator(query_AST, query_result = None):
    current_type = query_AST['type']
    print('queryAST', current_type, query_AST)
    if current_type == root_type:
        temp_result = None
    else:
        temp_result = None
        if temp_result is None:
            query_fields = []
            for field in query_AST['fields']:
                if field['type'] in ['String', 'Integer', 'Float']:
                    query_fields.append(field['name'])
            print('query_fields', query_fields)
    sub_query_ASTs = query_AST['fields']
    for ast in sub_query_ASTs:
        if ast['type'] not in ['String', 'Integer', 'Float']:
            QueryEvaluator(ast, None)
    return

#QueryEvaluator(queryAST['fields'][0])
'''

def getCommonPrefix(filter_ASTs):
    common_prefix = frozenset()
    for ast in filter_ASTs:
        prefix = ast.getPrefixExps()
        common_prefix -= frozenset(prefix)
        #common_prefix.add(frozenset(prefix))
    return common_prefix
'''


#ast = generateFilterAST(filter_fields_map, symbol_exp_dict, conjunctive_exp)
#result.getCurrentExpSymbols()
#prefix_exp_set = ast.getPrefixExps()
#all_exp = ast.getAllExps()
#FilterEvaluator(ast)

asts, common_prefix, repeated_exp = generateFilterASTs(filter_fields_map, symbol_exp_dict, [['A', 'B', '~C'], ['A', 'B', 'C']])


print('end')
print('set', common_prefix)
print('repeated', repeated_exp)
