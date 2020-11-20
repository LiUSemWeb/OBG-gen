from collections import defaultdict
import utils
from rdflib.namespace import RDF, RDFS,OWL

prefixes = {'rdf:type': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'rdf:comment':'http://www.w3.org/2000/01/rdf-schema#comment', 'rdfs:subClassOf': 'http://www.w3.org/2000/01/rdf-schema#subClassOf',
            'rdfs:label': 'http://www.w3.org/2000/01/rdf-schema#label', 'rdfs:domain': 'http://www.w3.org/2000/01/rdf-schema#domain', 'rdfs:range': 'http://www.w3.org/2000/01/rdf-schema#range',
            'owl:allValuesFrom': 'http://www.w3.org/2002/07/owl#allValuesFrom', 'owl:someValuesFrom': 'http://www.w3.org/2002/07/owl#someValuesFrom', 'owl:intersectionOf': 'http://www.w3.org/2002/07/owl#intersectionOf',
            'rdf:first': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#first', 'rdf:rest': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#rest', 'owl:onProperty': 'http://www.w3.org/2002/07/owl#onProperty',
            'owl:Restriction': 'http://www.w3.org/2002/07/owl#Restriction', 'rdfs:nil': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#nil', 'owl:qualifiedCardinality': 'http://www.w3.org/2002/07/owl#qualifiedCardinality',
            'owl:minQualifiedCardinality': 'http://www.w3.org/2002/07/owl#minQualifiedCardinality', 'owl:maxQualifiedCardinality': 'http://www.w3.org/2002/07/owl#maxQualifiedCardinality',
            'owl:onClass': 'http://www.w3.org/2002/07/owl#onClass', 'owl:ObjectProperty': 'http://www.w3.org/2002/07/owl#ObjectProperty', 'owl:DatatypeProperty': 'http://www.w3.org/2002/07/owl#DatatypeProperty',
            'owl:Class': 'http://www.w3.org/2002/07/owl#Class', 'owl:Ontology': 'http://www.w3.org/2002/07/owl#Ontology', 'owl:versionIRI': 'http://www.w3.org/2002/07/owl#versionIRI',
            'owl:onDataRange': 'http://www.w3.org/2002/07/owl#onDataRange'}



class Ontology(object):
    def __init__(self):
        self.classes = list()
        self.object_properties = list()
        self.data_properties = list()
        self.datatypes = list()
        self.domains_dict = defaultdict(list)
        self.ranges_dict = defaultdict(list)
        #self.types_dict = defaultdict(list)
        #self.labels_dict = defaultdict(list)
        #self.comments_dict = defaultdict(list)
        #self.subclasses_dict = defaultdict(list)
        self.triples = list()
        self.subsumption = list()
        self.generalaxioms_dict = defaultdict(list)
        self.allvaluesfrom_dict = defaultdict()
        self.somevaluesfrom_dict = defaultdict()
        self.eqc_dict = defaultdict()
        self.minqc_dict = defaultdict()
        self.maxqc_dict = defaultdict()
        self.ondatarange_dict = defaultdict()
        self.intersecctionof_dict = defaultdict(list)
        self.first_dict = defaultdict()
        self.rest_dict = defaultdict()
        self.restriction_list = list()
        self.onproperty_dist = defaultdict()
        self.onclass_dist = defaultdict()

        self.classes2subsumption = defaultdict(list)
        self.classes2axioms = defaultdict(list)
        self.axioms = list()

    def construct(self, graph):
        for s in graph.subjects(RDF.type, OWL.Class):
            s = s.toPython()
            self.classes.append(s)
        for s in graph.subjects(RDF.type, OWL.ObjectProperty):
            s = s.toPython()
            self.object_properties.append(s)
        for s in graph.subjects(RDF.type, OWL.DatatypeProperty):
            s = s.toPython()
            self.data_properties.append(s)
        
        file = open('all_triples.txt', 'w')
        for s, p, o in graph.triples((None, None, None)):
            file.writelines('{} {} {}\n'.format(s.toPython(),p.toPython(),o.toPython()))
            s = s.toPython()
            p = p.toPython()
            o = o.toPython()
            '''
            if p == prefixes['rdf:type']:
                self.types_dict[s].append(o)
            if p == prefixes['rdfs:label']:
                self.labels_dict[s].append(o)
            if p == prefixes['rdf:comment']:
                self.comments_dict[s].append(o)
            '''
            if p == prefixes['rdfs:domain']:
                self.domains_dict[s].append(o)
            if p == prefixes['rdfs:range']:
                self.ranges_dict[s].append(o)
                if s in self.data_properties and o not in self.datatypes:
                    self.datatypes.append(o)
            if p == prefixes['rdfs:subClassOf']:
                #self.subclasses_dict[s].append(o)
                if(o[0:4] != 'http'):
                    self.generalaxioms_dict[s].append(o)
                    #self.classes2axioms[s].append(o)
                else:
                    self.subsumption.append([s, o])
                    self.classes2subsumption[s].append(o)
            if p == prefixes['owl:intersectionOf']:
                self.intersecctionof_dict[s].append(o)
            if p == prefixes['owl:allValuesFrom']:
                self.allvaluesfrom_dict[s] = o
            if p == prefixes['owl:someValuesFrom']:
                self.somevaluesfrom_dict[s] = o
            if p == prefixes['owl:qualifiedCardinality']:
                self.eqc_dict[s] = o
            if p == prefixes['owl:minQualifiedCardinality']:
                self.minqc_dict[s] = o
            if p == prefixes['owl:maxQualifiedCardinality']:
                self.maxqc_dict[s] = o
            if p == prefixes['owl:onProperty']:
                self.onproperty_dist[s] = o
            if p == prefixes['owl:onClass']:
                self.onclass_dist[s] = o
            if p == prefixes['owl:onDataRange']:
                self.ondatarange_dict[s] = o
            if p == prefixes['rdf:first']:
                self.first_dict[s] = o
            if p == prefixes['rdf:rest']:
                self.rest_dict[s] = o
            if p == prefixes['rdf:type'] and o == prefixes['owl:Restriction']:
                self.restriction_list.append(s)

    def parse_general_axioms(self):
        #print(self.generalaxioms_dict)
        for (concept, anonymous_concepts) in self.generalaxioms_dict.items():
            for anonymous_concept in anonymous_concepts:
                #print(anonymous_concept)
                self.parse_anonymous_concept(concept, anonymous_concept)
                # not intersection
        for concept in self.classes:
            self.axioms.append([concept, 'iri', 'http://www.w3.org/2001/XMLSchema#string', '=1'])
        self.parse_anonymous_properties()
        return 0
    
    def parse_anonymous_properties(self):
        #print(self.onproperty_dist)
        for dp in self.data_properties:
            if dp not in self.onproperty_dist.values():
                'here maybe update in the future, if property has multiple domains'
                if len(self.domains_dict[dp]) > 0 and len(self.ranges_dict[dp]) >0:
                    self.axioms.append([self.domains_dict[dp][0], dp, self.ranges_dict[dp][0], '>0'])
        for op in self.object_properties:
            if op not in self.onproperty_dist.values():
                'here maybe update in the future, if property has multiple domains'
                if len(self.domains_dict[op]) > 0 and len(self.ranges_dict[op]) >0:
                    self.axioms.append([self.domains_dict[op][0], op, self.ranges_dict[op][0], '>0'])
        return 0



    def parse_anonymous_concept(self, concept, anonymous_concept):
        #print('ALL',self.allvaluesfrom_dict)
        if anonymous_concept in self.intersecctionof_dict.keys():
            for intersection_element in self.intersecctionof_dict[anonymous_concept]:
                #print('intersection')
                #print(intersection_element)
                first_element = self.first_dict[intersection_element]
                #print(concept, first_element)
                self.parse_anonymous_concept(concept, first_element)
                rest_element = self.rest_dict[intersection_element]
                #print(rest_element)
                self.parse_anonymous_concept(concept, rest_element)
        else:
            #print(anonymous_concept, self.maxqc_dict.keys())
            if anonymous_concept in self.restriction_list:
                if anonymous_concept in self.allvaluesfrom_dict.keys():
                    self.classes2axioms[concept].append((self.onproperty_dist[anonymous_concept], self.allvaluesfrom_dict[anonymous_concept], '>0'))
                    self.axioms.append([concept, self.onproperty_dist[anonymous_concept], self.allvaluesfrom_dict[anonymous_concept], '>0'])
                    #assertion = (concept, self.onproperty_dist[anonymous_concept], self.allvaluesfrom_dict[anonymous_concept], '>0')
                    #print(assertion)
                    if self.allvaluesfrom_dict[anonymous_concept][0:4] != 'http':
                        new_anonymous_concept = self.allvaluesfrom_dict[anonymous_concept]
                        self.classes.append(new_anonymous_concept)
                        self.parse_anonymous_concept(new_anonymous_concept, new_anonymous_concept)
                if anonymous_concept in self.somevaluesfrom_dict.keys():
                    #assertion = (concept, self.onproperty_dist[anonymous_concept], self.somevaluesfrom_dict[anonymous_concept], '>=1')
                    self.classes2axioms[concept].append((self.onproperty_dist[anonymous_concept], self.somevaluesfrom_dict[anonymous_concept], '>=1'))
                    self.axioms.append([concept, self.onproperty_dist[anonymous_concept], self.somevaluesfrom_dict[anonymous_concept], '>=1'])
                    if self.somevaluesfrom_dict[anonymous_concept][0:4] != 'http':
                        new_anonymous_concept = self.somevaluesfrom_dict[anonymous_concept]
                        self.classes.append(new_anonymous_concept)
                        self.parse_anonymous_concept(new_anonymous_concept, new_anonymous_concept)
                if anonymous_concept in self.eqc_dict.keys():
                    if anonymous_concept in self.ondatarange_dict.keys():
                        self.classes2axioms[concept].append((self.onproperty_dist[anonymous_concept], self.ondatarange_dict[anonymous_concept], '=' + str(self.eqc_dict[anonymous_concept])))
                        self.axioms.append([concept, self.onproperty_dist[anonymous_concept], self.ondatarange_dict[anonymous_concept], '=' + str(self.eqc_dict[anonymous_concept])])
                        #print((self.onproperty_dist[anonymous_concept], self.ondatarange_dict[anonymous_concept], '=', self.eqc_dict[anonymous_concept]))
                    else:
                        self.classes2axioms[concept].append((self.onproperty_dist[anonymous_concept], self.onclass_dist[anonymous_concept], '=' + str(self.eqc_dict[anonymous_concept])))
                        self.axioms.append([concept, self.onproperty_dist[anonymous_concept], self.onclass_dist[anonymous_concept], '=' + str(self.eqc_dict[anonymous_concept])])
                        #assertion = (concept, self.onproperty_dist[anonymous_concept], self.onclass_dist[anonymous_concept], '=', self.eqc_dict[anonymous_concept])
                        #print(assertion)
                        if self.onclass_dist[anonymous_concept][0:4] != 'http':
                            new_anonymous_concept = self.onclass_dist[anonymous_concept]
                            self.classes.append(new_anonymous_concept)
                            self.parse_anonymous_concept(new_anonymous_concept, new_anonymous_concept)
                if anonymous_concept in self.minqc_dict.keys():
                    if anonymous_concept in self.ondatarange_dict.keys():
                        self.classes2axioms[concept].append((self.onproperty_dist[anonymous_concept], self.ondatarange_dict[anonymous_concept], '>=' + str(self.minqc_dict[anonymous_concept])))
                        self.axioms.append([concept, self.onproperty_dist[anonymous_concept], self.ondatarange_dict[anonymous_concept], '>=' + str(self.minqc_dict[anonymous_concept])])
                        #print((self.onproperty_dist[anonymous_concept], self.ondatarange_dict[anonymous_concept], '=', self.minqc_dict[anonymous_concept]))
                    else:
                        self.classes2axioms[concept].append((self.onproperty_dist[anonymous_concept], self.onclass_dist[anonymous_concept], '>=' + str(self.minqc_dict[anonymous_concept])))
                        self.axioms.append([concept, self.onproperty_dist[anonymous_concept], self.onclass_dist[anonymous_concept], '>=' + str(self.minqc_dict[anonymous_concept])])
                        #assertion = (concept, self.onproperty_dist[anonymous_concept], self.onclass_dist[anonymous_concept], '>=', self.minqc_dict[anonymous_concept])
                        #print(assertion)
                        if self.onclass_dist[anonymous_concept][0:4] != 'http':
                            new_anonymous_concept = self.onclass_dist[anonymous_concept]
                            self.classes.append(new_anonymous_concept)
                            self.parse_anonymous_concept(new_anonymous_concept, new_anonymous_concept)
                if anonymous_concept in self.maxqc_dict.keys():
                    if anonymous_concept in self.ondatarange_dict.keys():
                        self.classes2axioms[concept].append((self.onproperty_dist[anonymous_concept], self.ondatarange_dict[anonymous_concept], '<=' + str(self.maxqc_dict[anonymous_concept])))
                        self.axioms.append([concept, self.onproperty_dist[anonymous_concept], self.ondatarange_dict[anonymous_concept], '<=' + str(self.maxqc_dict[anonymous_concept])])
                        #print((self.onproperty_dist[anonymous_concept], self.ondatarange_dict[anonymous_concept], '=', self.maxqc_dict[anonymous_concept]))
                    else:
                        self.classes2axioms[concept].append((self.onproperty_dist[anonymous_concept], self.onclass_dist[anonymous_concept], '<=' + str(self.maxqc_dict[anonymous_concept])))
                        self.axioms.append([concept, self.onproperty_dist[anonymous_concept], self.onclass_dist[anonymous_concept], '<=' + str(self.maxqc_dict[anonymous_concept])])
                        #assertion = (concept, self.onproperty_dist[anonymous_concept], self.onclass_dist[anonymous_concept], '<=', self.maxqc_dict[anonymous_concept])
                        #print(assertion)
                        if self.onclass_dist[anonymous_concept][0:4] != 'http':
                            new_anonymous_concept = self.onclass_dist[anonymous_concept]
                            self.classes.append(new_anonymous_concept)
                            self.parse_anonymous_concept(new_anonymous_concept, new_anonymous_concept)
            else:
                if anonymous_concept in self.first_dict.keys():
                    first_element = self.first_dict[anonymous_concept]
                    rest_element = self.rest_dict[anonymous_concept]
                    self.parse_anonymous_concept(concept, first_element)
                    if rest_element != prefixes['rdfs:nil']:
                        self.parse_anonymous_concept(concept, rest_element)
                else:
                    self.subsumption.append([concept, anonymous_concept])
                    self.classes2subsumption[concept].append(anonymous_concept)

    def print_subsumption_axiom(self):
        print('Classes', self.classes)
        print('-------------------')
        print('Data Types', self.datatypes)
        print('-------------------')
        print('Data Properties', self.data_properties)
        print('-------------------')
        print('Object Properties', self.object_properties)
        print('-------------------')
        print('Subsumptions', self.subsumption)
        print('-------------------')
        print('Axioms', self.axioms)
        return 0
    def output_ontology(self):
        return self.classes, self.datatypes, self.data_properties, self.object_properties, self.subsumption, self.axioms
       
'''
g = utils.parse_owl('testcoreQ.ttl')

o = Ontology()
o.construct(g)
o.parse_general_axioms()
o.print_subsumption_axiom()
#print(o.output_ontology())
'''