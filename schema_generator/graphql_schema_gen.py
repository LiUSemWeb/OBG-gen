from collections import defaultdict
from schema_generator.ontology import Ontology
import json
import datetime
import sys

from yaml import load, dump, FullLoader
from rdflib import Graph

#A = ['Calculation', 'Property', 'CalculatedProperty', 'PhysicalProperty', 'Structure', 'Quantity']
#V = ['xsd:string', 'xsd:double']
#U = ['ID', 'numericalValue', 'PropertyName']
#P = ['hasInputProperty', 'hasOutputProperty', 'hasInputStructure', 'hasOutputStructure', 'relatesToMaterial', 'relatesToStructure']
#subsumptions = [['CalculatedProperty', 'Property'], ['PhysicalProperty', 'Property']]
#assertions = [['Calculation', 'ID', 'xsd:string', '=1'], ['Calculation', 'hasInputStructure','Structure', '>=1']]

types = {'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':'rdf:type', 'http://www.w3.org/2000/01/rdf-schema#comment':'rdf:comment', 'http://www.w3.org/2000/01/rdf-schema#subClassOf': 'rdfs:subClassOf',
         'http://www.w3.org/2000/01/rdf-schema#label': 'rdfs:label', 'http://www.w3.org/2000/01/rdf-schema#domain': 'rdfs:domain', 'http://www.w3.org/2000/01/rdf-schema#range': 'rdfs:range',
         'http://www.w3.org/2002/07/owl#allValuesFrom': 'owl:allValuesFrom', 'http://www.w3.org/2002/07/owl#someValuesFrom' :'owl:someValuesFrom', 'http://www.w3.org/2002/07/owl#intersectionOf': 'owl:intersectionOf',
         'http://www.w3.org/1999/02/22-rdf-syntax-ns#first': 'rdf:first', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#rest': 'rdf:rest', 'http://www.w3.org/2002/07/owl#onProperty': 'owl:onProperty',
         'http://www.w3.org/2002/07/owl#Restriction': 'owl:Restriction', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#nil': 'rdfs:nil', 'http://www.w3.org/2002/07/owl#qualifiedCardinality': 'owl:qualifiedCardinality',
         'http://www.w3.org/2002/07/owl#minQualifiedCardinality': 'owl:minQualifiedCardinality', 'http://www.w3.org/2002/07/owl#maxQualifiedCardinality': 'owl:maxQualifiedCardinality',
         'http://www.w3.org/2002/07/owl#onClass': 'owl:onClass', 'http://www.w3.org/2002/07/owl#ObjectProperty': 'owl:ObjectProperty', 'http://www.w3.org/2002/07/owl#DataProperty': 'owl:DataProperty',
         'http://www.w3.org/2002/07/owl#Class': 'owl:Class', 'http://www.w3.org/2002/07/owl#Ontology': 'owl:Ontology', 'http://www.w3.org/2002/07/owl#versionIRI': 'owl:versionIRI',
         'http://www.w3.org/2002/07/owl#NamedIndividual': 'owl:NamedIndividual', 'http://www.w3.org/2002/07/owl#AnnotationProperty': 'owl:AnnotationProperty', 'http://purl.org/dc/terms/contributor': 'dcterms:contributor',
         'http://purl.org/dc/terms/creator': 'dcterms:creator', 'http://www.w3.org/2000/01/rdf-schema#Datatype': 'rdfs:Datatype', 'http://www.w3.org/2001/XMLSchema#date': 'xml:date',
         'http://purl.org/vocab/vann/preferredNamespaceUri': 'vann:preferredNamespaceUri', 'http://purl.org/dc/terms/license': 'dc:termslicense', 'http://purl.org/dc/terms/created': 'dcterms:created',
         'http://purl.org/vocab/vann/preferredNamespacePrefix': 'vann:preferredNamespacePrefix', 'http://www.w3.org/2002/07/owl#DatatypeProperty': 'owl:DatatypeProperty', 'http://www.w3.org/2001/XMLSchema#string': 'xmls:string',
         'http://www.w3.org/2002/07/owl#versionInfo': 'owl:versionInfo', 'http://www.w3.org/2001/XMLSchema#double': 'xmls:double'
         }


def read_TBox(TBox_file = './TBox.yml'):
    with open(TBox_file) as f:
        data = load(f, Loader=FullLoader)
        #print(data)
    return data['concepts'], data['data_types'], data['data_properties'], data['object_properties'], data['subsumptions'], data['axioms']
def write_file(schema_file, gq_schema):
    with open(schema_file, 'w') as output_file:
        output_file.write(gq_schema)
    #with open('./schemas/' + schema_file, 'w') as output_file:

def parse_owl(owl_file = 'testcore.ttl', format = 'n3'):
    g = Graph()
    g.parse(owl_file, format=format)
    return g

def remove_prefix(iri):
    if len(iri) > 4:
        if iri[0:4] == 'http':
            if '#' not in iri:
                return iri.split('/')[-1]
            else:
                return iri.split('#')[-1]
        else:
            return iri
    else:
        return iri

V2Scalar = {'http://www.w3.org/2001/XMLSchema#integer':'Int', 'xsd:float':'Float', 'xsd:string':'String', 'xsd:boolean':'Boolean',
            'http://www.w3.org/2001/XMLSchema#string': 'String', 'http://www.w3.org/2001/XMLSchema#double': 'Float'}
#A, V, U, P, subsumptions, assertions = su.read_TBox(TBox_file = './TBox.yml')
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
        self.implementation_temp = defaultdict(list)
        self.fields = defaultdict(dict)
    
    def construct(self, A, V, U, P, concept2superconcept, concept2assertions):
        self.I = A
        self.SC = V
        self.AF = U
        self.RF = P
        #self.implementation = concept2subsumptions
        self.implementation = concept2superconcept
        for (concept, assertions) in concept2assertions.items():
            for assertion in assertions:
                min_card = 0
                max_card = float("inf")
                if assertion[2] == '=1':
                    min_card = 1
                    max_card = 1
                if assertion[2] == '>=1':
                    continue
                    #should skip
                    #min_card = 1
                    #max_card = float("inf")
                if assertion[2] == '<=1':
                    continue
                    #should skip
                    #min_card = 0
                    #max_card = 1
                if assertion[2] == '>=0':
                    min_card = 0
                    max_card = float("inf")

                field_type = assertion[1]
                if assertion[1] in V2Scalar.keys():
                    field_type = V2Scalar[assertion[1]]
                self.fields[concept][(assertion[0],field_type)] = (min_card, max_card)
    
    def write_OntologyGraphQLSchemaMapping(self, A, U, P):
        temp_data = dict()
        for concept in A:
            temp_data[su.remove_prefix(concept)] = su.remove_prefix(concept)
        for data_property in U:
            temp_data[su.remove_prefix(data_property)] = su.remove_prefix(data_property)
        for object_property in P:
            temp_data[su.remove_prefix(object_property)] = su.remove_prefix(object_property)
        with open('o2graphql.json', 'w') as fp:
            json.dump(temp_data, fp)


    def write_global_schema(self):
        interfacetype_schema = ''
        objecttype_schema = ''
        querytype_schema = 'type Query {\n\t'

        self.I.sort(key = su.remove_prefix)
        for interface in self.I:
            interfacetype_schema += 'interface {interface}'.format(interface = su.remove_prefix(interface))
            objecttype_schema += 'type {interface}_obj implements {interface}'.format(interface = su.remove_prefix(interface))

            querytype_schema += '{interface}List('.format(interface = su.remove_prefix(interface))
            if len(self.implementation[interface]) >0:
                interfacetype_schema += ' implements '
                #objecttype_schema += ' implements {interface} & '.format(interface = su.remove_prefix(interface))
                for (i, implemented_interface) in enumerate(self.implementation[interface], 0):
                    interfacetype_schema += '{implemented_interface}'.format(implemented_interface = su.remove_prefix(implemented_interface))
                    objecttype_schema += ' & {implemented_interface}'.format(implemented_interface = su.remove_prefix(implemented_interface))
                    if i < len(self.implementation[interface]) -1:
                        interfacetype_schema += ' & '
                        #objecttype_schema += ' & '
            interfacetype_schema += '\n{\n'
            objecttype_schema += '\n{\n'

            for (key, item) in self.fields[interface].items():
                range = ''
                if item[0] == 0:
                    if item[1] == float('inf'):
                        range = '[{type}!]'.format(type = su.remove_prefix(key[1]))
                    if item[1] == 1:
                        range = '{type}'.format(type = su.remove_prefix(key[1]))
                if item[0] == 1:
                    if item[1] == float('inf'):
                        range = '[{type}!]!'.format(type = su.remove_prefix(key[1]))
                    if item[1] == 1:
                        range = '{type}!'.format(type = su.remove_prefix(key[1]))
                interfacetype_schema += '\t{field}:{type}\n'.format(field = su.remove_prefix(key[0]), type = range)
                objecttype_schema += '\t{field}:{type}\n'.format(field = su.remove_prefix(key[0]), type = range)
                if(key[1] in V2Scalar.values()):
                    querytype_schema += '{field}:[{type}],'.format(field = su.remove_prefix(key[0]), type = range)
            querytype_schema = querytype_schema[0:-1]
            querytype_schema += '): [{interface}]\n\t'.format(interface = su.remove_prefix(interface))
            interfacetype_schema += '}\n'
            objecttype_schema += '}\n'
        querytype_schema += '}\n'
            #schema += interfacetype_schema
        print(interfacetype_schema)
        print(objecttype_schema)
        print(querytype_schema)
        su.write_file('./schema_generator/schema-input_type-' + global_ontolopy_name +'.graphql',interfacetype_schema)
        su.write_file('./schema_generator/schema-object_type-' + global_ontolopy_name +'.graphql',objecttype_schema+'\n'+querytype_schema)

    def write_local_schema(self, local_prefixes):
        for local_prefix in local_prefixes:
            schema = ''
            self.I.sort(key = su.remove_prefix)
            for interface in self.I:
                type_schema = 'type {local_prefix}_{interface}'.format(local_prefix = local_prefix, interface = su.remove_prefix(interface))
                
                if len(self.implementation[interface]) >0:
                    type_schema += ' implements '
                    for (i, implemented_interface) in enumerate(self.implementation[interface], 0):
                        type_schema += '{implemented_interface}'.format(implemented_interface = su.remove_prefix(implemented_interface))
                        if i < len(self.implementation[interface]) -1:
                            type_schema += ' & '
                type_schema += '\n{\n'

                for (key, item) in self.fields[interface].items():
                    range = ''
                    field_type = su.remove_prefix(key[1])
                    if item[0] == 0:
                        if item[1] == float('inf'):
                            if key[1] in self.I:
                                range = '[{local_prefix}_{type}]'.format(local_prefix = local_prefix, type = field_type)
                            else:
                                range = '[{type}]'.format(type = field_type)
                        if item[1] == 1:
                            if key[1] in self.I:
                                range = '[{local_prefix}_{type}]'.format(local_prefix = local_prefix, type = field_type)
                            else:
                                range = '{type}'.format(type = field_type)
                    if item[0] == 1:
                        if item[1] == float('inf'):
                            if key[1] in self.I:
                                range = '[{local_prefix}_{type}]'.format(local_prefix = local_prefix, type = field_type)
                            else:
                                range = '[{type}!]!'.format(type = field_type)
                        if item[1] == 1:
                            if key[1] in self.I:
                                range = '[{local_prefix}_{type}]'.format(local_prefix = local_prefix, type = field_type)
                            else:
                                range = '{type}!'.format(type = field_type)
                    type_schema += '\t{field}:{type}\n'.format(field = su.remove_prefix(key[0]), type = range)
                type_schema += '}\n'
                schema += type_schema
            print(schema)
            print(local_prefix)
            su.write_file('{local_prefix}_schema.graphql'.format(local_prefix = local_prefix),schema)
        
            
def main(ontology):
    print('main function')
    g = su.parse_owl(ontology)
    o = Ontology()
    o.construct(g)
    #o.parse_general_axioms()
    #o.print_subsumption_axiom()
    #elq1d_test = ELQ_1_D()
    A, V, U, P, subsumptions, assertions, concepts2superconcepts, concepts2axioms = o.output_ontology()
    #o.print()
    #print(len(assertions))
    #print(A, V, U, P, subsumptions, assertions)
    #elq1d_test.construct(A, V, U, P, subsumptions, assertions)
    #elq1d.print()
    a = datetime.datetime.now()
    graphql_schema_test = GraphQLSchema()
    #graphql_schema_test.construct(elq1d_test.A, elq1d_test.V, elq1d_test.U, elq1d_test.P, elq1d_test.concept2subsumptions, elq1d_test.concept2assertions)
    graphql_schema_test.construct(A, V, U, P, concepts2superconcepts, concepts2axioms)
    graphql_schema_test.write_global_schema()
    graphql_schema_test.write_OntologyGraphQLSchemaMapping(A, U, P)
    #graphql_schema_test.write_local_schema(['OQMD','MP'])
    #graphql_schema_test.write_local_schema(databases)
    b = datetime.datetime.now()
    print(b-a)

global_ontolopy_name = ''
databases = list()

if __name__ == '__main__':
    print(str(sys.argv[1]))
    global_ontolopy_name = str(sys.argv[1]).split('/')[2].split('.')[0]
    databases = [str(k) for k in sys.argv[2:]]
    main(str(sys.argv[1]))
'''
elq1d = ELQ_1_D()
elq1d.construct(A, V, U, P, subsumptions, assertions)
#elq1d.print()

graphql_schema = GraphQLSchema()
graphql_schema.construct(elq1d.A, elq1d.V, elq1d.U, elq1d.P,elq1d.concept2subsumptions, elq1d.concept2assertions)
graphql_schema.write_schema()

'''
#g = su.parse_owl('testcoreQ.ttl')
#print(str(sys.argv[1]))
