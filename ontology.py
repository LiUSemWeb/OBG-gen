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

        self.class2superclass = defaultdict(list)
        self.class2subclass = defaultdict(list)
        self.class2axioms = defaultdict(list)
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
                    self.class2superclass[s].append(o)
                    self.class2subclass[o].append(s)
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
        
        
        self.class2superclass_flag = {k:-1 for k in self.class2superclass.keys()}
        self.class2subclass_flag = {k:-1 for k in self.class2subclass.keys()}
        #The order of following functions
        self.__parse_tree()
        self.__parse_general_axioms()
        
        for c in self.classes:
            if c[0:4] != 'http':
                for (key, value) in self.domains_dict.items():
                    if (key in self.data_properties or key in self.object_properties) and c in value:
                        self.classes.remove(c)
                        break
                '''
                for (key, value) in self.ranges_dict.items():
                    if (key in self.data_properties or key in self.object_properties) and c in value:
                        self.classes.remove(c)
                        break
                '''

    
    def __parse_general_axioms(self):
        for (current_class, anonymous_classes) in self.generalaxioms_dict.items():
            for anonymous_class in anonymous_classes:
                self.__parse_anonymous_class(current_class, anonymous_class)
                # not intersection
        for current_class in self.classes:
            self.axioms.append([current_class, 'iri', 'http://www.w3.org/2001/XMLSchema#string', '=1'])
            self.class2axioms[current_class].append(['iri', 'http://www.w3.org/2001/XMLSchema#string', '=1'])
        self.__parse_anonymous_properties()
    
    # to parse some property do not appear in any axiom but have both domain and range definition, (for all)
    def __parse_anonymous_properties(self):
        for dp in self.data_properties:
            if dp not in self.onproperty_dist.values():
                'here maybe update in the future, if property has multiple domains'
                if len(self.domains_dict[dp]) > 0 and len(self.ranges_dict[dp]) >0:
                    self.axioms.append([self.domains_dict[dp][0], dp, self.ranges_dict[dp][0], '>0'])
                    self.class2axioms[self.domains_dict[dp][0]].append([dp, self.ranges_dict[dp][0], '>0'])
        for op in self.object_properties:
            if op not in self.onproperty_dist.values():
                'here maybe update in the future, if property has multiple domains'
                if len(self.domains_dict[op]) > 0 and len(self.ranges_dict[op]) >0:
                    self.axioms.append([self.domains_dict[op][0], op, self.ranges_dict[op][0], '>0'])
                    self.class2axioms[self.domains_dict[op][0]].append([op, self.ranges_dict[op][0], '>0'])

    # to parse an expression
    def __parse_anonymous_class(self, current_class, anonymous_class):
        if anonymous_class in self.intersecctionof_dict.keys():
            for intersection_element in self.intersecctionof_dict[anonymous_class]:
                first_element = self.first_dict[intersection_element]
                self.__parse_anonymous_class(current_class, first_element)
                rest_element = self.rest_dict[intersection_element]
                self.__parse_anonymous_class(current_class, rest_element)
        else:
            if anonymous_class in self.restriction_list:
                if anonymous_class in self.allvaluesfrom_dict.keys():
                    axiom = [current_class, self.onproperty_dist[anonymous_class], self.allvaluesfrom_dict[anonymous_class], '>0']
                    if axiom not in self.axioms:
                        self.axioms.append(axiom)
                        self.class2axioms[current_class].append([self.onproperty_dist[anonymous_class], self.allvaluesfrom_dict[anonymous_class], '>0'])
                        #add axiom for current_class's sub-current_class
                        for subclass in self.class2subclass[current_class]:
                            axiom = [subclass, self.onproperty_dist[anonymous_class], self.allvaluesfrom_dict[anonymous_class], '>0']
                            if axiom not in self.axioms:
                                self.axioms.append(axiom)
                                self.class2axioms[subclass].append([self.onproperty_dist[anonymous_class], self.allvaluesfrom_dict[anonymous_class], '>0'])
                    if self.allvaluesfrom_dict[anonymous_class][0:4] != 'http':
                        new_anonymous_class = self.allvaluesfrom_dict[anonymous_class]
                        self.classes.append(new_anonymous_class)
                        self.__parse_anonymous_class(new_anonymous_class, new_anonymous_class)
                if anonymous_class in self.somevaluesfrom_dict.keys():
                    axiom = [current_class, self.onproperty_dist[anonymous_class], self.somevaluesfrom_dict[anonymous_class], '>=1']
                    if axiom not in self.axioms:
                        self.axioms.append(axiom)
                        self.class2axioms[current_class].append([self.onproperty_dist[anonymous_class], self.somevaluesfrom_dict[anonymous_class], '>=1'])
                        #add axiom for current_class's sub-current_class
                        for subclass in self.class2subclass[current_class]:
                            axiom = [subclass, self.onproperty_dist[anonymous_class], self.somevaluesfrom_dict[anonymous_class], '>=1']
                            if axiom not in self.axioms:
                                self.axioms.append(axiom)
                                self.class2axioms[subclass].append([self.onproperty_dist[anonymous_class], self.somevaluesfrom_dict[anonymous_class], '>=1'])
                    if self.somevaluesfrom_dict[anonymous_class][0:4] != 'http':
                        new_anonymous_class = self.somevaluesfrom_dict[anonymous_class]
                        self.classes.append(new_anonymous_class)
                        self.__parse_anonymous_class(new_anonymous_class, new_anonymous_class)
                if anonymous_class in self.eqc_dict.keys():
                    if anonymous_class in self.ondatarange_dict.keys():
                        axiom = [current_class, self.onproperty_dist[anonymous_class], self.ondatarange_dict[anonymous_class], '=' + str(self.eqc_dict[anonymous_class])]
                        if axiom not in self.axioms:
                            self.axioms.append(axiom)
                            self.class2axioms[current_class].append([self.onproperty_dist[anonymous_class], self.ondatarange_dict[anonymous_class], '=' + str(self.eqc_dict[anonymous_class])])
                            #add axiom for current_class's sub-current_class
                            for subclass in self.class2subclass[current_class]:
                                axiom = [subclass, self.onproperty_dist[anonymous_class], self.ondatarange_dict[anonymous_class], '=' + str(self.eqc_dict[anonymous_class])]
                                if axiom not in self.axioms:
                                    self.axioms.append(axiom)
                                    self.class2axioms[subclass].append([self.onproperty_dist[anonymous_class], self.ondatarange_dict[anonymous_class], '=' + str(self.eqc_dict[anonymous_class])])
                    else:
                        axiom = [current_class, self.onproperty_dist[anonymous_class], self.onclass_dist[anonymous_class], '=' + str(self.eqc_dict[anonymous_class])]
                        if axiom not in self.axioms:
                            self.axioms.append(axiom)
                            self.class2axioms[current_class].append([self.onproperty_dist[anonymous_class], self.onclass_dist[anonymous_class], '=' + str(self.eqc_dict[anonymous_class])])
                            #add axiom for current_class's sub-current_class
                            for subclass in self.class2subclass[current_class]:
                                axiom = [subclass, self.onproperty_dist[anonymous_class], self.onclass_dist[anonymous_class], '=' + str(self.eqc_dict[anonymous_class])]
                                if axiom not in self.axioms:
                                    self.axioms.append(axiom)
                                    self.class2axioms[subclass].append([self.onproperty_dist[anonymous_class], self.onclass_dist[anonymous_class], '=' + str(self.eqc_dict[anonymous_class])])
                        if self.onclass_dist[anonymous_class][0:4] != 'http':
                            new_anonymous_class = self.onclass_dist[anonymous_class]
                            self.classes.append(new_anonymous_class)
                            self.__parse_anonymous_class(new_anonymous_class, new_anonymous_class)
                if anonymous_class in self.minqc_dict.keys():
                    if anonymous_class in self.ondatarange_dict.keys():
                        self.axioms.append([current_class, self.onproperty_dist[anonymous_class], self.ondatarange_dict[anonymous_class], '>=' + str(self.minqc_dict[anonymous_class])])
                        self.class2axioms[current_class].append([self.onproperty_dist[anonymous_class], self.ondatarange_dict[anonymous_class], '>=' + str(self.minqc_dict[anonymous_class])])
                    else:
                        axiom = [current_class, self.onproperty_dist[anonymous_class], self.onclass_dist[anonymous_class], '>=' + str(self.minqc_dict[anonymous_class])]
                        if axiom not in self.axioms:
                            self.axioms.append(axiom)
                            self.class2axioms[current_class].append([self.onproperty_dist[anonymous_class], self.onclass_dist[anonymous_class], '>=' + str(self.minqc_dict[anonymous_class])])
                            #add axiom for current_class's sub-current_class
                            for subclass in self.class2subclass[current_class]:
                                axiom = [subclass, self.onproperty_dist[anonymous_class], self.onclass_dist[anonymous_class], '>=' + str(self.minqc_dict[anonymous_class])]
                                if axiom not in self.axioms:
                                    self.axioms.append(axiom)
                                    self.class2axioms[subclass].append([self.onproperty_dist[anonymous_class], self.onclass_dist[anonymous_class], '>=' + str(self.minqc_dict[anonymous_class])])
                        if self.onclass_dist[anonymous_class][0:4] != 'http':
                            new_anonymous_class = self.onclass_dist[anonymous_class]
                            self.classes.append(new_anonymous_class)
                            self.__parse_anonymous_class(new_anonymous_class, new_anonymous_class)
                if anonymous_class in self.maxqc_dict.keys():
                    if anonymous_class in self.ondatarange_dict.keys():
                        axiom = [current_class, self.onproperty_dist[anonymous_class], self.ondatarange_dict[anonymous_class], '<=' + str(self.maxqc_dict[anonymous_class])]
                        if axiom not in self.axioms:
                            self.axioms.append(axiom)
                            self.class2axioms[current_class].append([self.onproperty_dist[anonymous_class], self.ondatarange_dict[anonymous_class], '<=' + str(self.maxqc_dict[anonymous_class])])
                            #add axiom for current_class's sub-current_class
                            for subclass in self.class2subclass[current_class]:
                                axiom = [subclass, self.onproperty_dist[anonymous_class], self.ondatarange_dict[anonymous_class], '<=' + str(self.maxqc_dict[anonymous_class])]
                                if axiom not in self.axioms:
                                    self.axioms.append(axiom)
                                    self.class2axioms[subclass].append([self.onproperty_dist[anonymous_class], self.ondatarange_dict[anonymous_class], '<=' + str(self.maxqc_dict[anonymous_class])])
                    else:
                        axiom = [current_class, self.onproperty_dist[anonymous_class], self.onclass_dist[anonymous_class], '<=' + str(self.maxqc_dict[anonymous_class])]
                        if axiom not in self.axioms:
                            self.axioms.append(axiom)
                            self.class2axioms[current_class].append([self.onproperty_dist[anonymous_class], self.onclass_dist[anonymous_class], '<=' + str(self.maxqc_dict[anonymous_class])])
                            #add axiom for current_class's sub-current_class
                            for subclass in self.class2subclass[current_class]:
                                axiom = [subclass, self.onproperty_dist[anonymous_class], self.onclass_dist[anonymous_class], '<=' + str(self.maxqc_dict[anonymous_class])]
                                if axiom not in self.axioms:
                                    self.axioms.append(axiom)
                                    self.class2axioms[subclass].append([self.onproperty_dist[anonymous_class], self.onclass_dist[anonymous_class], '<=' + str(self.maxqc_dict[anonymous_class])])
                        if self.onclass_dist[anonymous_class][0:4] != 'http':
                            new_anonymous_class = self.onclass_dist[anonymous_class]
                            self.classes.append(new_anonymous_class)
                            self.__parse_anonymous_class(new_anonymous_class, new_anonymous_class)
            else:
                if anonymous_class in self.first_dict.keys():
                    first_element = self.first_dict[anonymous_class]
                    rest_element = self.rest_dict[anonymous_class]
                    self.__parse_anonymous_class(current_class, first_element)
                    if rest_element != prefixes['rdfs:nil']:
                        self.__parse_anonymous_class(current_class, rest_element)
                else:
                    self.subsumption.append([current_class, anonymous_class])
                    self.class2superclass[current_class].append(anonymous_class)
                    self.class2subclass[anonymous_class].append(current_class)
    # to parse a super-sub tree
    def __parse_tree(self):
        for c in self.classes:
            if c not in self.class2superclass.keys() and c in self.class2subclass.keys():
                self.__get_subclasses(c)
            if c in self.class2superclass.keys() and c not in self.class2subclass.keys():
                self.__get_superclasses(c)
        print('TREE',self.class2subclass)

    # to get all the super classes by the current class
    def __get_superclasses(self, current_class):
        if current_class in self.class2superclass.copy().keys():
            superclasses = self.class2superclass.copy()[current_class]
            for superclass in superclasses:
                temp = self.__get_superclasses(superclass)
                superclasses = superclasses + temp
            # the flag is used to ensure each node is recursed only once
            if self.class2superclass_flag[current_class] == -1:
                self.class2superclass[current_class] = list(set(self.class2superclass[current_class] + superclasses))
                self.class2superclass_flag[current_class] = 0
            return superclasses
        else:
            return []

    # to get all the sub classes by the current class
    def __get_subclasses(self, current_class):
        if current_class in self.class2subclass.copy().keys():
            subclasses = self.class2subclass.copy()[current_class]
            for subclass in subclasses:
                temp = self.__get_subclasses(subclass)
                subclasses = subclasses + temp
            # the flag is used to ensure each node is recursed only once
            if self.class2subclass_flag[current_class] == -1:
                self.class2subclass[current_class] = list(set(self.class2subclass[current_class] + subclasses))
                self.class2subclass_flag[current_class] = 0
            return subclasses
        else:
            return []

    def print(self):
        print('Classes', self.classes)
        print('-------------------')
        print('Data Types', self.datatypes)
        print('-------------------')
        print('Data Properties', self.data_properties)
        print('-------------------')
        print('Object Properties', self.object_properties)
        print('-------------------')
        print('Subsumptions', self.subsumption, len(self.subsumption))
        #print(self.class2superclass)
        #print(self.class2subclass)
        print('-------------------')
        print('Axioms', self.axioms, len(self.axioms))
    def output_ontology(self):
        return self.classes, self.datatypes, self.data_properties, self.object_properties, self.subsumption, self.axioms, self.class2superclass, self.class2axioms
       
'''
g = utils.parse_owl('testcoreQ.ttl')

o = Ontology()
o.construct(g)
#o.__parse_general_axioms()
o.print_subsumption_axiom()
#print(o.output_ontology())
'''