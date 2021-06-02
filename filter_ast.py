class Filter_AST(object):
    def __init__(self, name, children = None, parent = None, parent_edge = None, filter_dict = None):
        #data in the form of list of (field name: symbol (with negation or not))
        self.name = name
        self.children = children or []
        self.parent = parent
        self.parent_edge = parent_edge
        self.children_edges = []
        self.filter_dict = filter_dict or {}
        self.parent_edge_chain = ''
        self.attrs_type = dict()
        self.filter_flag = 'ALL'

    def add_child(self, child_name, edge):
        new_child = FilterAST(child_name, parent=self, parent_edge=edge)
        new_child.parent_edge_chain = self.parent_edge_chain + '.' + edge
        self.children.append(new_child)
        self.children_edges.append(edge)
        self.filter_flag = 'ALL'
        return new_child

    def add_child_edge(self, child_edge):
        self.children_edges.append(child_edge)

    def add_attribute_filter(self, attr_symbol, filter_dict, attr_type):
        self.filter_dict[attr_symbol] = filter_dict
        self.attrs_type[attr_symbol] = attr_type
        self.filter_flag = ''


    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return not self.children

    def get_sub_trees(self):
        return self.children

    def get_sub_tree_by_edge(self, edge):
        return_child = None
        for child in self.children:
            if child.parent_edge == edge:
                return_child = child
                break
        return return_child

    def get_current_filter(self):
        ''''''
        if len(self.filter_dict) > 0:
            return self.filter_dict
        else:
            return {}

    def get_current_expression_symbols(self):
        exp_symbols = set()
        current_filter = self.get_current_filter()
        if len(current_filter) > 0:
            for key, value in current_filter.items():
                for exp in value:
                    exp_symbols.add(exp['symbol'])
        else:
            if self.name != 'root':
                exp_symbols.add(self.name + '-ALL')
        return exp_symbols

    def get_prefix_expressions(self):
        if len(self.children) > 0:
            exp_symbols = self.get_current_expression_symbols()
            for child in self.children:
                child_prefix_exp_symbols = child.get_prefix_expressions()
                exp_symbols = set.union(exp_symbols, child_prefix_exp_symbols)
            return exp_symbols
        else:
            return set()

    def get_all_expression(self):
        exp_symbols = self.get_current_expression_symbols()
        for child in self.children:
            child_prefix_exp_symbols = child.get_all_expression()
            exp_symbols = set.union(exp_symbols, child_prefix_exp_symbols)
        return exp_symbols