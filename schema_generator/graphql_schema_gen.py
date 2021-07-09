from collections import defaultdict
from ontology import Ontology
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
    with open(schema_file, 'w+') as output_file:
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
        self.concept2superconcepts = dict()

        self.I_T = list()
        self.O_T = list()
        self.IO_T = list()
        self.F = list()
        self.S = list()

        self.type_S_F = defaultdict(dict)
        self.type_S_I_F = defaultdict(dict)
        self.type_S_AF = defaultdict(dict)
        self.impl = defaultdict(list)

    @staticmethod
    def Phi(term):
        if term in V2Scalar.keys():
            new_term = V2Scalar[term]
        else:
            new_term = remove_prefix(term)
        return new_term

    @staticmethod
    def Psi(entry):
        return '{entry_type}List'.format(entry_type=remove_prefix(entry))

    @staticmethod
    def Upsilon(interface_name):
        return '{interface}_IF'.format(interface=remove_prefix(interface_name))

    @staticmethod
    def Theta(entry):
        return '{entry_type}Filter'.format(entry_type=remove_prefix(entry))

    @staticmethod
    def check_assertion_cardinality(assertions):
        card_flag = False
        for assertion in assertions:
            if assertion[2] == '=1':
                card_flag = True
                break
        return card_flag

    def schema_gen(self, N_C, N_D, N_A, N_R, concept2superconcept, concept2assertions):
        self.O_T = [self.Phi(c) for c in N_C]
        self.IO_T = [self.Theta(c) for c in N_C]
        #self.fields[concept][(assertion[0], field_type)] = (min_card, max_card)
        for c in N_C:
            self.type_S_F[self.Phi(c)][('IRI', 'String')] = (1, 1)
            self.type_S_F['Query'][(self.Psi(c), self.Phi(c))] =(0, float('inf'))
            self.type_S_AF['Query'][(self.Psi(c), 'filter')] = (1, 1)
        self.F = [self.Phi(r) for r in N_R]
        self.F += [self.Phi(a) for a in N_A]
        self.S = [self.Phi(d) for d in N_D]
        self.IO_T += [self.Theta(self.Phi(d)) for d in N_D]
        for sub_concept, super_concepts in concept2superconcept.items():
            self.concept2superconcepts[remove_prefix(sub_concept)] = [remove_prefix(sc) for sc in super_concepts]
            for super_concept in super_concepts:
                self.I_T.append(self.Upsilon(super_concept))
                self.type_S_F[self.Upsilon(super_concept)][('IRI', 'String')] = (1, 1)
                self.impl[self.Upsilon(super_concept)].append(self.Phi(sub_concept))
                if self.Phi(super_concept) not in self.impl[self.Upsilon(super_concept)]:
                    self.impl[self.Upsilon(super_concept)].append(self.Phi(super_concept))
        for (concept, assertions) in concept2assertions.items():
            for assertion in assertions:
                min_card = 0
                max_card = float("inf")
                if assertion[2] == '>=0':
                    if self.check_assertion_cardinality(assertions) is True:
                        max_card = 1
                field_type = assertion[1]
                if assertion[1] in V2Scalar.keys():
                    field_type = V2Scalar[assertion[1]]
                self.type_S_F[self.Phi(concept)][(self.Phi(assertion[0]), self.Phi(field_type))] = (min_card, max_card)
                self.type_S_I_F[self.Theta(concept)][(self.Phi(assertion[0]), self.Theta(field_type))] = (min_card, 1)
        # self.I = list(set(self.I))
        # print(self.impl)
        return

    def render_object_types(self):
        object_type_str_dict = defaultdict()
        object_impl_str_dict = defaultdict()
        for object_type, field_definition_dict in self.type_S_F.items():
            if object_type not in self.I_T:
                impl_str = ''
                if object_type in self.concept2superconcepts.keys():
                    interfaces_lst = [self.Upsilon(sc) for sc in self.concept2superconcepts[object_type]]
                    impl_str = ' & '.join(interfaces_lst)
                    object_impl_str_dict[object_type] = ' implements {impl_str}'.format(impl_str=impl_str)
                line_str_lst = ['{\n']
                for field_name_type, cards in field_definition_dict.items():
                    field_name = field_name_type[0]
                    field_type = field_name_type[1]
                    if cards[1] == 1:
                        field_return_str = '\t{field_name}: {return_type}\n'.format(field_name=field_name, return_type=field_type)
                    else:
                        if object_type == 'Query':
                            field_return_str = '\t{field_name}(filter: {input_type}): [{return_type}]\n'.format(field_name=field_name, input_type=self.Theta(field_type), return_type=field_type)
                        else:
                            field_return_str = '\t{field_name}: [{return_type}]\n'.format(field_name=field_name,
                                                                                        return_type=field_type)
                    line_str_lst.append(field_return_str)
                line_str_lst.append('}\n')
                object_type_str_dict[object_type] = line_str_lst
        with open('test-schema.graphql', 'a') as output_file:
            for object_type, object_field_lst in object_type_str_dict.items():
                if object_type in object_impl_str_dict.keys():
                    # print('type ' + object_type + object_impl_str_dict[object_type])
                    output_file.write('type ' + object_type + object_impl_str_dict[object_type])
                else:
                    # print('type ' + object_type)
                    output_file.write('type ' + object_type)
                # print(''.join(object_field_lst))
                output_file.write(''.join(object_field_lst))

    def render_interface_types(self):
        interface_type_str_dict = defaultdict()
        for interface_name in self.impl.keys():
            object_type_name = interface_name.split('_IF')[0]
            field_definition_dict = self.type_S_F[object_type_name]
            line_str_lst = ['{\n']
            for field_name_type, cards in field_definition_dict.items():
                field_name = field_name_type[0]
                field_type = field_name_type[1]
                if cards[1] == 1:
                    field_return_str = '\t{field_name}: {return_type}\n'.format(field_name=field_name,
                                                                                return_type=field_type)
                else:
                    field_return_str = '\t{field_name}: [{return_type}]\n'.format(field_name=field_name,
                                                                                  return_type=field_type)
                line_str_lst.append(field_return_str)
            line_str_lst.append('}\n')
            interface_type_str_dict[interface_name] = line_str_lst
        with open('test-schema.graphql', 'a') as output_file:
            for object_type, object_field_lst in interface_type_str_dict.items():
                # print('interface ' + object_type)
                # print(''.join(object_field_lst))
                output_file.write('interface ' + object_type)
                output_file.write(''.join(object_field_lst))

    def render_input_object_types(self):
        input_object_type_str_dict = defaultdict()
        for object_type, field_definition_dict in self.type_S_I_F.items():
            line_str_lst = ['{\n']
            for field_name_type, cards in field_definition_dict.items():
                field_name = field_name_type[0]
                field_type = field_name_type[1]
                if cards[1] == 1:
                    field_return_str = '\t{field_name}: {return_type}\n'.format(field_name=field_name, return_type=field_type)
                else:
                    field_return_str = '\t{field_name}: [{return_type}]\n'.format(field_name=field_name, return_type=field_type)
                line_str_lst.append(field_return_str)
            line_str_lst.append('}\n')
            input_object_type_str_dict[object_type] = line_str_lst
        with open('test-schema.graphql', 'a') as output_file:
            for object_type, object_field_lst in input_object_type_str_dict.items():
                # print('input ' + object_type)
                # print(''.join(object_field_lst))
                output_file.write('input ' + object_type)
                output_file.write(''.join(object_field_lst))

    def construct(self, A, V, U, P, concept2superconcept, concept2assertions):
        self.I = A
        self.SC = V
        self.AF = U
        self.RF = P
        #self.implementation = concept2subsumptions
        self.implementation = concept2superconcept
        '''
        for sub_concept, super_concepts in concept2superconcept.items():
            for super_concept in super_concepts:
                self.I.append(super_concept)
        self.I = list(set(self.I))
        '''
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
            temp_data[remove_prefix(concept)] = remove_prefix(concept)
        for data_property in U:
            temp_data[remove_prefix(data_property)] = remove_prefix(data_property)
        for object_property in P:
            temp_data[remove_prefix(object_property)] = remove_prefix(object_property)
        with open('o2graphql.json', 'w') as fp:
            json.dump(temp_data, fp)


    def write_global_schema(self):
        interfacetype_schema = ''
        objecttype_schema = ''
        querytype_schema = 'type Query {\n\t'

        self.I.sort(key = remove_prefix)
        for interface in self.I:
            interfacetype_schema += 'interface {interface}'.format(interface = remove_prefix(interface))
            objecttype_schema += 'type {interface}_obj implements {interface}'.format(interface = remove_prefix(interface))

            querytype_schema += '{interface}List('.format(interface = remove_prefix(interface))
            if len(self.implementation[interface]) >0:
                interfacetype_schema += ' implements '
                #objecttype_schema += ' implements {interface} & '.format(interface = remove_prefix(interface))
                for (i, implemented_interface) in enumerate(self.implementation[interface], 0):
                    interfacetype_schema += '{implemented_interface}'.format(implemented_interface = remove_prefix(implemented_interface))
                    objecttype_schema += ' & {implemented_interface}'.format(implemented_interface = remove_prefix(implemented_interface))
                    if i < len(self.implementation[interface]) -1:
                        interfacetype_schema += ' & '
                        #objecttype_schema += ' & '
            interfacetype_schema += '\n{\n'
            objecttype_schema += '\n{\n'

            for (key, item) in self.fields[interface].items():
                range = ''
                if item[0] == 0:
                    if item[1] == float('inf'):
                        range = '[{type}!]'.format(type = remove_prefix(key[1]))
                    if item[1] == 1:
                        range = '{type}'.format(type = remove_prefix(key[1]))
                if item[0] == 1:
                    if item[1] == float('inf'):
                        range = '[{type}!]!'.format(type = remove_prefix(key[1]))
                    if item[1] == 1:
                        range = '{type}!'.format(type = remove_prefix(key[1]))
                interfacetype_schema += '\t{field}:{type}\n'.format(field = remove_prefix(key[0]), type = range)
                objecttype_schema += '\t{field}:{type}\n'.format(field = remove_prefix(key[0]), type = range)
                if(key[1] in V2Scalar.values()):
                    querytype_schema += '{field}:[{type}],'.format(field = remove_prefix(key[0]), type = range)
            querytype_schema = querytype_schema[0:-1]
            querytype_schema += '): [{interface}]\n\t'.format(interface = remove_prefix(interface))
            interfacetype_schema += '}\n'
            objecttype_schema += '}\n'
        querytype_schema += '}\n'
            #schema += interfacetype_schema
        print(interfacetype_schema)
        print(objecttype_schema)
        print(querytype_schema)
        # write_file('./schema_generator/schema-input_type-' + global_ontolopy_name +'.graphql',interfacetype_schema)
        # write_file('./schema_generator/schema-object_type-' + global_ontolopy_name +'.graphql',objecttype_schema+'\n'+querytype_schema)
        write_file('schema-input_type-' + global_ontolopy_name + '.graphql', interfacetype_schema)
        write_file('schema-object_type-' + global_ontolopy_name + '.graphql',
                   objecttype_schema + '\n' + querytype_schema)

    def write_local_schema(self, local_prefixes):
        for local_prefix in local_prefixes:
            schema = ''
            self.I.sort(key = remove_prefix)
            for interface in self.I:
                type_schema = 'type {local_prefix}_{interface}'.format(local_prefix = local_prefix, interface = remove_prefix(interface))
                
                if len(self.implementation[interface]) >0:
                    type_schema += ' implements '
                    for (i, implemented_interface) in enumerate(self.implementation[interface], 0):
                        type_schema += '{implemented_interface}'.format(implemented_interface = remove_prefix(implemented_interface))
                        if i < len(self.implementation[interface]) -1:
                            type_schema += ' & '
                type_schema += '\n{\n'

                for (key, item) in self.fields[interface].items():
                    range = ''
                    field_type = remove_prefix(key[1])
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
                    type_schema += '\t{field}:{type}\n'.format(field = remove_prefix(key[0]), type = range)
                type_schema += '}\n'
                schema += type_schema
            print(schema)
            print(local_prefix)
            write_file('{local_prefix}_schema.graphql'.format(local_prefix = local_prefix),schema)
        
            
def main(ontology):
    print('main function')
    g = parse_owl(ontology)
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
    graphql_schema_test.schema_gen(A, V, U, P, concepts2superconcepts, concepts2axioms)
    graphql_schema_test.render_interface_types()
    graphql_schema_test.render_object_types()
    graphql_schema_test.render_input_object_types()
    # graphql_schema_test.write_global_schema()
    # graphql_schema_test.write_OntologyGraphQLSchemaMapping(A, U, P)
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
#g = parse_owl('testcoreQ.ttl')
#print(str(sys.argv[1]))
