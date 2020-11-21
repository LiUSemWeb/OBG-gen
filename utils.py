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