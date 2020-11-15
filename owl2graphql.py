from collections import defaultdict
import utils
from rdflib.namespace import RDF, RDFS,OWL
from ontology import Ontology

V2Scalar = {'xsd:integer':'Int', 'xsd:float':'Float', 'xsd:string':'String', 'xsd:boolean':'Boolean',
            'http://www.w3.org/2001/XMLSchema#string': 'String', 'http://www.w3.org/2001/XMLSchema#double': 'Float'}
A, V, U, P, subsumptions, assertions = utils.read_TBox(TBox_file = './TBox.yml')
'''
print('A:', A)
print('V:', V)
print('U:', U)
print('P:', P)
print('subsumptions:', subsumptions)
print('assertions:', assertions)
'''



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
    
    def test_write_schema(self):
        schema = ''
        for interface in self.I:
            interface_schema = 'interface {interface}'.format(interface = utils.remove_prefix(interface))
            
            if len(self.implementation[interface]) >0:
                interface_schema += ' implements '
                for (i, implemented_interface) in enumerate(self.implementation[interface], 0):
                    interface_schema += '{implemented_interface}'.format(implemented_interface = utils.remove_prefix(implemented_interface))
                    if i < len(self.implementation[interface]) -1:
                        interface_schema += ' & '
            interface_schema += '\n{\n'

            for (key, item) in self.fields[interface].items():
                range = ''
                if item[0] == 0:
                    if item[1] == float('inf'):
                        range = '[{type}]'.format(type = utils.remove_prefix(key[1]))
                    if item[1] == 1:
                        range = '{type}'.format(type = utils.remove_prefix(key[1]))
                if item[0] == 1:
                    if item[1] == float('inf'):
                        range = '[{type}]!'.format(type = utils.remove_prefix(key[1]))
                    if item[1] == 1:
                        range = '{type}!'.format(type = utils.remove_prefix(key[1]))
                interface_schema += '\t{field}:{type}\n'.format(field = utils.remove_prefix(key[0]), type = range)
            interface_schema += '}\n'
            schema += interface_schema
        print(schema)
            



elq1d = ELQ_1_D()
elq1d.construct(A, V, U, P, subsumptions, assertions)
#elq1d.print()

graphql_schema = GraphQLSchema()
graphql_schema.construct(elq1d.A, elq1d.V, elq1d.U, elq1d.P,elq1d.concept2subsumptions, elq1d.concept2assertions)
graphql_schema.write_schema()

g = utils.parse_owl('testcoreQ.ttl')

o = Ontology()
o.construct(g)
o.parse_general_axioms()
#o.print_subsumption_axiom()

elq1d_test = ELQ_1_D()
A, V, U, P, subsumptions, assertions = o.output_ontology()
elq1d_test.construct(A, V, U, P, subsumptions, assertions)
#elq1d.print()

graphql_schema_test = GraphQLSchema()
graphql_schema_test.construct(elq1d_test.A, elq1d_test.V, elq1d_test.U, elq1d_test.P,elq1d_test.concept2subsumptions, elq1d_test.concept2assertions)
graphql_schema_test.test_write_schema()

    