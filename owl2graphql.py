# Class of ontology
from collections import defaultdict

A = ['Calculation', 'Property', 'CalculatedProperty', 'PhysicalProperty', 'Structure', 'Quantity']
V = ['xsd:string', 'xsd:double']
U = ['ID', 'numericalValue', 'PropertyName']
P = ['hasInputProperty', 'hasOutputProperty', 'hasInputStructure', 'hasOutputStructure', 'relatesToMaterial', 'relatesToStructure']
#concept2subsumptions = {'CalculationProperty': ['Property'], 'PhysicalProperty': ['Property']}
subsumptions = [('CalculatedProperty', 'Property'), ('PhysicalProperty', 'Property')]
assertions = [('Calculation', 'ID', 'xsd:string', '=1'), ('Calculation', 'hasInputStructure','Structure', '>=1')]
#concept2assertions = {'Calculation':[('ID', 'xsd:String', '=1'),('hasInputStructure','Structure', '>=1')}
V2Scalar = {'xsd:integer':'Int', 'xsd:float':'Float', 'xsd:string':'String', 'xsd:boolean':'Boolean'}

def map_scalartype(datatype):
    if datatype == 'xsd:string':
        return 'String'
    if datatype == 'xsd:double':
        return 'Float'

class ELQD(object):
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
        #print(self.classes)
        #print(self.concept2subsumptions)
        print(self.concept2assertions)

class GraphQLSchema(object):
    def __init__(self):
        #self.object_types = list()
        self.interfaces = list()
        self.Scalar_types = list()
        self.implementation = defaultdict(list)
        self.fields = defaultdict(dict)
    
    def construct(self, A, V, U, P, concept2subsumptions, concept2assertions):
        print(self.interfaces)
        self.interfaces = A
        self.Scalar_types = V
        self.U = U
        self.P = P
        self.implementation = concept2subsumptions
        #self.fields = defaultdict(list)
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
                print(assertion)
                #assertion[1] = V2Scalar[assertion[1]]
                field_type = assertion[1]
                if assertion[1] in V2Scalar.keys():
                    field_type = V2Scalar[assertion[1]]
                assertion_dict = {(assertion[0],field_type): (min_card, max_card)}
                #self.fields[concept].append(assertion_dict)
                self.fields[concept][(assertion[0],field_type)] = (min_card, max_card)
        print(self.fields)

    def write_schema(self):
        schema = ''
        for interface in self.interfaces:
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
            

elqd = ELQD()
elqd.construct(A, V, U, P, subsumptions, assertions)
#elqd.print()

graphql_schema = GraphQLSchema()
graphql_schema.construct(elqd.A, elqd.V, elqd.U, elqd.P,elqd.concept2subsumptions, elqd.concept2assertions)
graphql_schema.write_schema()