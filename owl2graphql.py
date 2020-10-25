from collections import defaultdict
import utils


V2Scalar = {'xsd:integer':'Int', 'xsd:float':'Float', 'xsd:string':'String', 'xsd:boolean':'Boolean'}
A, V, U, P, subsumptions, assertions = utils.read_TBox(TBox_file = './TBox.yml')

class ELQ_1_D(object):
    def __init__(self):
        self.A = list()
        self.V = list()
        self.U = list()
        self.P = list()
        self.concept2subsumptions = defaultdict(list)
        self.concept2assertions = defaultdict(list)
    
    def construct(self, A, V, U, P, subsumptions, assertions):
        self.A = A
        self.V = V
        self.U = U
        self.P = P
        for subsumption in subsumptions:
            self.concept2subsumptions[subsumption[0]].append(subsumption[1])
        for assertion in assertions:
            self.concept2assertions[assertion[0]]. append(assertion[1:])
    
    def print(self):
        print(self.concept2assertions)

class GraphQLSchema(object):
    def __init__(self):
        self.I = list()
        self.SC = list()
        self.AF = list()
        self.RF = list()
        self.implementation = defaultdict(list)
        self.fields = defaultdict(dict)
    
    def construct(self, A, V, U, P, concept2subsumptions, concept2assertions):
        self.I = A
        self.SC = V
        self.AF = U
        self.RF = P
        self.implementation = concept2subsumptions
        for (concept, assertions) in concept2assertions.items():
            for assertion in assertions:
                min_card = 0
                max_card = float("inf")
                if assertion[2] == '=1':
                    min_card = 1
                    max_card = 1
                if assertion[2] == '>=1':
                    min_card = 1
                    max_card = float("inf")
                if assertion[2] == '<=1':
                    min_card = 0
                    max_card = 1
                if assertion[2] == '>=0':
                    min_card = 0
                    max_card = float("inf")
                field_type = assertion[1]
                if assertion[1] in V2Scalar.keys():
                    field_type = V2Scalar[assertion[1]]
                self.fields[concept][(assertion[0],field_type)] = (min_card, max_card)

    def write_schema(self):
        schema = ''
        for interface in self.I:
            interface_schema = 'interface {interface}'.format(interface = interface)
            
            if len(self.implementation[interface]) >0:
                interface_schema += ' implements '
                for (i, implemented_interface) in enumerate(self.implementation[interface], 0):
                    interface_schema += '{implemented_interface}'.format(implemented_interface = implemented_interface)
                    if i < len(self.implementation[interface]) -1:
                        interface_schema += ' & '
            interface_schema += '\n{\n'

            for (key, item) in self.fields[interface].items():
                range = ''
                if item[0] == 0:
                    if item[1] == float('inf'):
                        range = '[{type}]'.format(type = key[1])
                    if item[1] == 1:
                        range = '{type}'.format(type = key[1])
                if item[0] == 1:
                    if item[1] == float('inf'):
                        range = '[{type}]!'.format(type = key[1])
                    if item[1] == 1:
                        range = '{type}!'.format(type = key[1])
                interface_schema += '\t{field}:{type}\n'.format(field = key[0], type = range)
            interface_schema += '}\n'
            schema += interface_schema
        print(schema)
            

elqd = ELQ_1_D()
elqd.construct(A, V, U, P, subsumptions, assertions)
#elqd.print()

graphql_schema = GraphQLSchema()
graphql_schema.construct(elqd.A, elqd.V, elqd.U, elqd.P,elqd.concept2subsumptions, elqd.concept2assertions)
graphql_schema.write_schema()