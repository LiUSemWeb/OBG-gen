import requests
import csv
import codecs
from contextlib import closing
import mapping_utils as mu
from collections import defaultdict

#map between ontology's terms  and GraphQL schema's terms
ontology_GraphQLschema = {'Calculation': 'Calculation', 'CalculatedProperty':'CalculatedProperty', 'Structure':'Structure', 'Composition':'Composition', 'QuantityValue': 'QuantityValue',
                          'hasOutputStructure': 'hasOutputStructure', 'hasComposition': 'hasComposition', 'hasOutputCalculatedProperty': 'hasOutputCalculatedProperty','quantityValue': 'quantityValue',
                          'ID': 'ID', 'ReducedFormula': 'ReducedFormula', 'AnonymousFormula': 'AnonymousFormula', 'PropertyName': 'PropertyName', 'numericValue': 'numericValue'}

GraphQLschema_Ontology = {'Calculation': 'Calculation', 'CalculatedProperty':'CalculatedProperty', 'Structure':'Structure', 'Composition':'Composition', 'QuantityValue': 'QuantityValue',
                          'hasOutputStructure': 'hasOutputStructure', 'hasComposition': 'hasComposition', 'hasOutputCalculatedProperty': 'hasOutputCalculatedProperty','quantityValue': 'quantityValue',
                          'ID': 'ID', 'ReducedFormula': 'ReducedFormula', 'AnonymousFormula': 'AnonymousFormula', 'PropertyName': 'PropertyName', 'numericValue': 'numericValue'}

scalar_types = ['Int', 'Float', 'String', 'Boolean', 'ID', 'CUSTOM_SCALAR_TYPE']

def parseIterator(iterator):
    iterator_elements = iterator.split('.')
    iterator_elements = list(filter(None, iterator_elements))
    return iterator_elements

def getJSONData(URL, iterator = None, ref = None):
    r = requests.get(url = URL)
    data = r.json()
    if iterator is not None:
        keys = parseIterator(iterator)
        temp_data = data
        for i in range(len(keys)):
            temp_data = temp_data[keys[i]]
        return temp_data
    else:
        return data

def getCSVData(URL, ref = None):
    ref_condition, ref_data = [], []
    if ref is not None:
        ref_condition = ref[1]
        ref_data = [ record[ref_condition['child']] for record in ref[0] ]
        #print(ref_data)
    records = []
    result = []
    with closing(requests.get(URL, stream=True)) as r:
        reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'), delimiter=';')
        for record in reader:
            records.append(record)
    header = records[0]
    num_fields = len(header)
    for record in records[1:]:
        element = dict()
        if ref is not None:
            if record[header.index(ref_condition['parent'])] in ref_data:
                for i in range(num_fields):
                    element[header[i]] = record[i]
            else:
                break
        else:
            for i in range(num_fields):
                element[header[i]] = record[i]
        result.append(element)
    #if ref is not None: print(result)
    return result

def parseAST(AST):
    concept_type = AST['type']
    queryFields = []
    for field in AST['fields']:
        queryFields.append(field['name'])
    return concept_type, queryFields

def getSubAST(AST, predicate):
    fields = AST['fields']
    newAST = None
    for field in fields:
        if field['name'] == predicate:
            newAST = field
            break
    return newAST

def getMappings(concept_type):
    return mu.getMappingsByType(concept_type)

def getLogicalSource(mapping):
    return mu.getLogicalSourceByMapping(mapping)    

def getTemplate(mapping):
    return mu.getSubjectTemplateByMapping(mapping)


def Phi(ontology_term):
    return ontology_GraphQLschema[ontology_term]

def Phi_inverse(GraphQL_term):
    return GraphQLschema_Ontology[GraphQL_term]

def Translate(queryFields):
    predicates = []
    for field in queryFields:
        predicates.append(Phi_inverse(field))
    return predicates

def Execute(logicalSource, ref = None):
    source_type = mu.getLSType(logicalSource)
    source_request = mu.getSource(logicalSource)
    result = []
    if source_type == 'ql:CSV':
        result = getCSVData(source_request, ref)
    if source_type == 'ql:JSONPath':
        iterator = mu.getJSONIterator(logicalSource)
        result = getJSONData(source_request, iterator, ref)
    return result

def getPredicateObjectMap(mapping, predicates):
    return mu.getPredicateObjectMapByPred(mapping, predicates)

def parsePOM(pom):
    return mu.parsePOM(pom)

def parseROM(objectMap):
    return mu.parseROM(objectMap)

def getReference(termMap):
    return mu.getReference(termMap)

def parseJoinCondition(joinCondition):
    return mu.parseJoinCondition(joinCondition)

def getChildData(tempResult, childField):
    return [ {childField: record[childField]} for record in tempResult ]

def parseTemplate(template):
    start_pos = template.index('{')
    end_pos = template.index('}')
    key = template[start_pos + 1: end_pos]
    newtemplate = template.replace(key,'')
    return key, newtemplate

def Refine(tempResult, attr_pred_lst, constant, template):
    key, template = parseTemplate(template)
    for record in tempResult:
        record['iri'] = template.format(record[key])
        for attr_pred_tuple in attr_pred_lst:
            if '.' in attr_pred_tuple[0]:
                keys = parseIterator(attr_pred_tuple[0])
                temp_data = record
                for i in range(len(keys)):
                    temp_data = temp_data[keys[i]]
                del record[keys[0]]
                record[attr_pred_tuple[1]] = temp_data
            else:
                if attr_pred_tuple[0] in record.keys():
                    record[attr_pred_tuple[1]] = record.pop(attr_pred_tuple[0])
    return tempResult

def IncrementalJoin(tempResult, result2join):
    result = []
    if len(result2join) > 0: 
        for (joinData, joinCondition, field) in result2join:
            #print(joinData)
            for join_record in joinData: 
                for record in tempResult:
                    if record[joinCondition['child']] == join_record[joinCondition['parent']]:
                        new_record = record
                        new_record[field] = join_record
                        result.append(new_record)
        #this join has duplicates
        return result
    else: 
        return tempResult

def Merge(result, tempResult):
    #print(result, tempResult)
    return result + tempResult

def DuplicateDetectionFusion(result):
    return result

def TypeOfObjectMap(objectMap):
    return mu.TypeOfObjectMap(objectMap)

def DataFetcher(AST, mapping = None, ref= None):
    result, mappings = [], []
    concept_type, queryFields = parseAST(AST)
    #print(concept_type, queryFields)
    if mapping == None:
        mappings = getMappings(concept_type)
        #print(mappings)
    else:
        mappings.append(mapping)
    predicates = Translate(queryFields)
    for mapping in mappings:
        logicalSource = getLogicalSource(mapping)
        template = getTemplate(mapping)
        tempResult = Execute(logicalSource, ref)
        poms = getPredicateObjectMap(mapping, predicates)
        attr_pred, result2join, constant = [], [], []
        for pom in poms:
            predicate, objectMap = parsePOM(pom)
            if TypeOfObjectMap(objectMap) == 1:
                referenceAttribute = getReference(objectMap)
                attr_pred.append((referenceAttribute, Phi(predicate)))
            if TypeOfObjectMap(objectMap) == 2:
                print('Constant')
            if TypeOfObjectMap(objectMap) == 3:
                newAST = getSubAST(AST, Phi(predicate))
                parentMapping, joinCondition = parseROM(objectMap)
                childField, parentField = parseJoinCondition(joinCondition)
                childData = getChildData(tempResult, childField)
                ref = (childData, joinCondition)
                parentData = DataFetcher(newAST, parentMapping, ref)
                result2join.append((parentData, joinCondition, Phi(predicate)))
        #print(tempResult)
        tempResult = Refine(tempResult, attr_pred, constant, template)
        tempResult = IncrementalJoin(tempResult, result2join)
        #print('break here')
        #print(tempResult)
        #break
        result = Merge(result, tempResult)
    return DuplicateDetectionFusion(result)



query_context_1 = {
    "name": "CalculationList",
    "type": "Calculation",
    "fields":[
        {
            "name": "hasID",
            "type": "String",
            "fields":[]
        },
        {
            "name": "hasOutputStructure",
            "type": "Structure",
            "fields":[
                {
                    "name": "hasComposition",
                    "type": "Composition",
                    "fields":[
                        {
                            "name": "ReducedFormula",
                            "type": "String",
                            "fields":[]
                        }
                    ]
                }
            ]
        }
    ]   
}

query_context_2 = {
    "name": "CompositionList",
    "type": "Composition",
    "fields": [
        {
            "name": "ReducedFormula",
            "type": "String",
            "fields":[]
        },
        {
            "name": "AnonymousFormula",
            "type": "String",
            "fields":[]
        }
    ]
}

query_context_3 = {
    "name": "StructureList",
    "type": "Structure",
    "fields": [
        {
            "name": "hasComposition",
            "type": "Composition",
            "fields":[
                {
                    "name": "ReducedFormula",
                    "type": "String",
                    "fields":[]
                },
                {
                    "name": "AnonymousFormula",
                    "type": "String",
                    "fields":[]
                }
            ]
        }
    ]
}
query_context_4 = {
    "name": "CalculationList",
    "type": "Calculation",
    "fields": [
        {
            "name": "hasOutputStructure",
            "type": "Structure",
            "fields": [
                {
                    "name": "hasComposition",
                    "type": "Composition",
                    "fields":[
                        {
                            "name": "ReducedFormula",
                            "type": "String",
                            "fields":[]
                        },
                        {
                            "name": "AnonymousFormula",
                            "type": "String",
                            "fields":[]
                        }
                    ]
                }
            ]
        },
        {
            "name": "ID",
            "type": "String",
            "fields":[]
        }
    ]
}


result = DataFetcher(query_context_3)
print(result)
#getSubAST(query_context_1, 'hasOutputStructure')

#print(getJSONData('https://huanyu-li.github.io/data/calculation.json', 'Calculation'))
#getCSVData('https://huanyu-li.github.io/data/calculation_volume.csv')#