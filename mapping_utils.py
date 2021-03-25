from collections import defaultdict
import json

def read_mappings(file): 
    with open(file) as f:
      data = json.load(f)
    return data

logical_sources = [
    {'name': 'Calculation_CSVSource_1', 'source': 'https://huanyu-li.github.io/data/calculation1.csv', 'referenceFormulation': 'ql:CSV', 'iterator': ''},
    {'name': 'Calculation_JSONSource_1', 'source': 'https://huanyu-li.github.io/data/calculation1.json', 'referenceFormulation': 'ql:JSONPath', 'iterator': '$.Calculations[*]'},
    {'name': 'Structure_CSVSource_1', 'source': 'https://huanyu-li.github.io/data/structure1.csv', 'referenceFormulation': 'ql:CSV', 'iterator': ''},
    {'name': 'Structure_JSONSource_1', 'source': 'https://huanyu-li.github.io/data/structure1.json', 'referenceFormulation': 'ql:JSONPath', 'iterator': '$.Structures[*]'},
    {'name': 'Composition_CSVSource_1', 'source': 'https://huanyu-li.github.io/data/composition1.csv', 'referenceFormulation': 'ql:CSV', 'iterator': ''},
    {'name': 'Composition_JSONSource_1', 'source': 'https://huanyu-li.github.io/data/composition1.json', 'referenceFormulation': 'ql:JSONPath', 'iterator': '$.Compositions[*]'},
    {'name': 'Composition_CSVSource_2', 'source': 'https://huanyu-li.github.io/data/composition2.csv', 'referenceFormulation': 'ql:CSV', 'iterator': ''},
    {'name': 'Composition_JSONSource_2', 'source': 'https://huanyu-li.github.io/data/composition2.json', 'referenceFormulation': 'ql:JSONPath', 'iterator': '$.data.Compositions[*]'}

]

mappings_0 = [
    {
        'name': 'Calculation_Mapping_1',
        'logicalSource': 'Calculation_CSVSource_1',
        'subjectMap': {'template': 'http://example.com/{id}/Calculation', 'class': 'Calculation'},
        'predicateObjectMap': 
        [
            {'predicate': 'ID', 'objectMap': {'reference': 'id', 'datatype': 'xsd:string'}},
            {'predicate': 'hasOutputStructure', 'objectMap': {'parentTriplesMap': 'Structure_Mapping_1', 'joinCondition': {'child': 'output_sid', 'parent': 'structure_id'}}}
        ]
    },
    {
        'name': 'Structure_Mapping_1',
        'logicalSource': 'Structure_CSVSource_1',
        'subjectMap': {'template': 'http://example.com/structure/{structure_id}', 'class': 'Structure'},
        'predicateObjectMap': 
        [
            {'predicate': 'hasComposition', 'objectMap': {'parentTriplesMap': 'Composition_Mapping_1', 'joinCondition': {'child': 'composition_id', 'parent': 'composition_id'}}},
            {'predicate': 'hasComposition', 'objectMap': {'parentTriplesMap': 'Composition_Mapping_2', 'joinCondition': {'child': 'composition_id', 'parent': 'formula_id'}}}
        ]
    },
    {
        'name': 'Composition_Mapping_1',
        'logicalSource': 'Composition_CSVSource_1',
        'subjectMap': {'template': 'http://example.com/composition/{composition_id}', 'class': 'Composition'},
        'predicateObjectMap': 
        [
            {'predicate': 'ReducedFormula', 'objectMap': {'reference': 'Reduced_formula', 'datatype': 'xsd:string'}},
            {'predicate': 'AnonymousFormula', 'objectMap': {'reference': 'Composition_generic', 'datatype': 'xsd:string'}}
        ]
    },
    {
        'name': 'Composition_Mapping_2',
        'logicalSource': 'Composition_CSVSource_2',
        'subjectMap': {'template': 'http://example.com/composition/{formula_id}', 'class': 'Composition'},
        'predicateObjectMap': 
        [
            {'predicate': 'ReducedFormula', 'objectMap': {'reference': 'Reduced_formula', 'datatype': 'xsd:string'}},
            {'predicate': 'AnonymousFormula', 'objectMap': {'reference': 'Generic_formula', 'datatype': 'xsd:string'}}
        ]
    }
]

mappings = [
    {
        'name': 'Calculation_Mapping_1',
        'logicalSource': 'Calculation_JSONSource_1',
        'subjectMap': {'template': 'http://example.com/{id}/Calculation', 'class': 'Calculation'},
        'predicateObjectMap': 
        [
            {'predicate': 'ID', 'objectMap': {'reference': 'id', 'datatype': 'xsd:string'}},
            {'predicate': 'hasOutputStructure', 'objectMap': {'parentTriplesMap': 'Structure_Mapping_1', 'joinCondition': {'child': 'output_sid', 'parent': 'structure_id'}}}
        ]
    },
    {
        'name': 'Structure_Mapping_1',
        'logicalSource': 'Structure_JSONSource_1',
        'subjectMap': {'template': 'http://example.com/structure/{structure_id}', 'class': 'Structure'},
        'predicateObjectMap': 
        [
            {'predicate': 'hasComposition', 'objectMap': {'parentTriplesMap': 'Composition_Mapping_1', 'joinCondition': {'child': 'composition_id', 'parent': 'composition_id'}}},
            {'predicate': 'hasComposition', 'objectMap': {'parentTriplesMap': 'Composition_Mapping_2', 'joinCondition': {'child': 'composition_id', 'parent': 'formula_id'}}}
        ]
    },
    {
        'name': 'Composition_Mapping_1',
        'logicalSource': 'Composition_JSONSource_1',
        'subjectMap': {'template': 'http://example.com/composition/{composition_id}', 'class': 'Composition'},
        'predicateObjectMap': 
        [
            {'predicate': 'ReducedFormula', 'objectMap': {'reference': 'Reduced_formula', 'datatype': 'xsd:string'}},
            {'predicate': 'AnonymousFormula', 'objectMap': {'reference': 'Composition_generic', 'datatype': 'xsd:string'}}
        ]
    },
    {
        'name': 'Composition_Mapping_2',
        'logicalSource': 'Composition_JSONSource_2',
        'subjectMap': {'template': 'http://example.com/composition/{formula_id}', 'class': 'Composition'},
        'predicateObjectMap': 
        [
            {'predicate': 'ReducedFormula', 'objectMap': {'reference': 'Reduced_formula', 'datatype': 'xsd:string'}},
            {'predicate': 'AnonymousFormula', 'objectMap': {'reference': 'Generic_formula.name', 'datatype': 'xsd:string'}}
        ]
    }
]

rml_mapping = read_mappings('./mappings.json')
logical_sources = rml_mapping['sources']
mappings = rml_mapping['mappings']

print('here')
print(logical_sources, mappings)

def getMappingsByType(Type):
    result_mappings = []
    for m in mappings:
        if m['subjectMap']['class'] == Type:
            result_mappings.append(m)
    return result_mappings

def getMappingsByName(mapping_name):
    result_mapping = None
    for m in mappings:
        if m['name'] == mapping_name:
            result_mapping = m
            break
    return result_mapping

#def getSubjectByMapping(mapping):
#    return mapping['subjectMap']

def getLogicalSourceByMapping(mapping):
    logical_source = None
    for ls in logical_sources:
        if ls['name'] == mapping['logicalSource']:
            logical_source = ls
            break
    return logical_source

def getSubjectTemplateByMapping(mapping):
    return mapping['subjectMap']['template']
    #return getIRITemplate(mapping['subjectMap']['template'])

def getIRITemplate(IRITemplate):
    #Example IRI template http://www.mdo.com/mp/calculation/{entry_id}
    start_position = IRITemplate.index('{')
    end_position = IRITemplate.index('}')
    return IRITemplate[0:start_position] + IRITemplate[end_position+1:]


def getPredicateObjectMapByPred(mapping, predicates):
    poms = getPredicateObjectMap(mapping)
    poms = [pom for pom in poms if pom['predicate'] in predicates]
    return poms

def parsePOM(pom):
    return pom['predicate'], pom['objectMap']

def TypeOfObjectMap(objectMap):
    if 'reference' in objectMap.keys():
        return 1
    if 'constant' in objectMap.keys():
        return 2
    if 'parentTriplesMap' in objectMap.keys():
        return 3
    return 0

def getReference(termMap):
    return termMap['reference']

def parseROM(objectMap):
    mapping_name = objectMap['parentTriplesMap']
    joinCondition = objectMap['joinCondition']
    parentMapping = getMappingsByName(mapping_name)
    return parentMapping, joinCondition

def parseJoinCondition(joinCondition):
    return joinCondition['child'], joinCondition['parent']

def getPredicateObjectMap(mapping):
    return mapping['predicateObjectMap']

def getLSType(logicalSource):
    return logicalSource['referenceFormulation']

def getSource(logicalSource):
    return logicalSource['source']

def getJSONIterator(logicalSource):
    iterator = logicalSource['iterator']
    if '[*]' in iterator:
        position = iterator.index('[*]')
        return iterator[1:position]
    else:
        return iterator[1:]

def getLogicalSourceByName(name):
    for ls in logical_sources:
        if ls['name'] == name:
            return ls

def getTemplateByType(Type):
    templates = []
    for m in mappings:
        if m['subjectMap']['class'] == Type:
            templates.append(m['subjectMap']['template'])
    return templates



def getMappingNameLogicalSourceByType(Type):
    mapping_name_ls = []
    for m in mappings:
        if m['subjectMap']['class'] == Type:
            mapping_name_ls.append({m['name']: getLogicalSourceByName(m['logicalSource'])})
    return mapping_name_ls

def getSourcesByType(Type):
    sources = defaultdict(list)
    for m in mappings:
        if m['subjectMap']['class'] == Type:
            sources[getIRITemplate(m['subjectMap']['template'])].append(getLogicalSourceByName(m['logicalSource']))
    return sources

def getPOMByMappingName(name):
    poms = []
    for m in mappings:
        if m['name'] == name:
            poms.append(m['predicateObjectMap'])
    return poms

def getPredicatesByMappingName(name):
    predicates = []
    for m in mappings:
        if m['name'] == name:
            for pom in m['predicateObjectMap']:
                predicates.append(pom['predicate'])
    return predicates

def getJCByMappingNameandPredicate(mapping_name, predicate_name):
    join_condition = None
    for m in mappings:
        if m['name'] == mapping_name:
            for pom in m['predicateObjectMap']:
                if pom['predicate'] == predicate_name and pom['objectMap']['parentTriplesMap']:
                    join_condition = pom['objectMap']['joinCondition']
    return join_condition

def getMappingNamesByType(Type):
    result_mapping_names = []
    for m in mappings:
        if m['subjectMap']['class'] == Type:
            result_mapping_names.append(m['name'])
    return result_mapping_names

#print(getJCByMappingNameandPredicate('#CalculationMapping1','hasICSDStructure'))
#print(getIRITemplate('http://www.mdo.com/mp/calculation/{entry_id}/test'))

#print(getIRITemplate('http://www.mdo.com/mp/calculation/{entry_id}'))
#print(getSourcesByType('Calculation').keys())

        

