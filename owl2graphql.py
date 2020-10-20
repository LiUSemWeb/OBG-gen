# Class of ontology
from collections import defaultdict

classes = ['Calculation', 'Property', 'CalculatedProperty', 'PhysicalProperty', 'Structure']
data_types = ['xsd:string', 'xsd:double']
data_roles = ['ID', 'numericalValue', 'PropertyName']
object_roles = ['hasInputProperty', 'hasOutputProperty', 'hasInputStructure', 'hasOutputStructure', 'relatesToMaterial', 'relatesToStructure']
#classes2subsumptions = {'CalculationProperty': ['Property'], 'PhysicalProperty': ['Property']}
subsumptions = [('CalculatedProperty', 'Property'), ('PhysicalProperty', 'Property')]
assertions = [('Calculation', 'ID', 'xsd:String', '=1'), ('Calculation', 'hasInputStructure','Structure', '>=1')]
#classes2assertions = {'Calculation':[('ID', 'xsd:String', '=1'),('hasInputStructure','Structure', '>=1')}

def map_scalartype(datatype):
    if datatype == 'xsd:string':
        return 'String'
    if datatype == 'xsd:double':
        return 'Float'

class ELQ(object):
    def __init__(self):
        self.classes = list()
        self.data_types = list()
        self.data_roles = list()
        self.object_roles = list()
        self.classes2subsumptions = defaultdict(list)
        self.classes2assertions = defaultdict(list)
    
    def construct(self, classes, data_types, data_roles, object_roles, subsumptions, assertions):
        self.classes = classes
        self.data_types = data_types
        self.data_roles = data_roles
        self.object_roles = object_roles
        for subsumption in subsumptions:
            self.classes2subsumptions[subsumption[0]].append(subsumption[1])
        for assertion in assertions:
            self.classes2assertions[assertion[0]]. append(assertion[1:])
    
    def print(self):
        #print(self.classes)
        #print(self.classes2subsumptions)
        print(self.classes2assertions)

class GraphQLSchema(object):
    def __init(self):
        #self.object_types = list()
        self.interfaces = list()
        self.Scalar_types = list()
        self.implementation = defaultdict(list)
        self.fields = defaultdict(list)
    
    def construct(self, classes, data_types, data_roles, object_roles, classes2subsumptions, class2assertions):
        self.interfaces = classes
        self.Scalar_types = data_types
        self.data_roles = data_roles
        self.object_roles = object_roles
        self.implementation = classes2subsumptions
        self.fields = class2assertions
    
    def write_schema(self):
        for interface in self.interfaces:
            print('interface ' + interface)
            for implemented_interfaces in self.implementation[interface]:
                print('implements ' + implemented_interfaces)
            print('{')
            for assertion in self.fields[interface]:
                if assertion[2] == '=1':
                    print(assertion[0] + ': ' + assertion[1] + '!')
                if assertion[2] == '>=1':
                    print(assertion[0] + ': [' + assertion[1] + ']!')
            print('}')
            print('----------')

elq_1 = ELQ()
elq_1.construct(classes, data_types, data_roles, object_roles, subsumptions, assertions)
elq_1.print()

graphql_schema = GraphQLSchema()
graphql_schema.construct(elq_1.classes, [map_scalartype(t) for t in elq_1.data_types], elq_1.data_roles, elq_1.object_roles,elq_1.classes2subsumptions, elq_1.classes2assertions)
graphql_schema.write_schema()