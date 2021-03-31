from collections import defaultdict
import json

class RML_Mapping(object):
	def __init__(self, mapping_file):
		self.rml_mapping = self.__read_mappings(mapping_file)
		self.dbsources = self.rml_mapping['DBSources']
		self.logical_sources = self.rml_mapping['LogicalSources']
		self.mappings = self.rml_mapping['Mappings']
	
	def __read_mappings(self, file): 
		with open(file) as f:
			data = json.load(f)
			return data

	def getMappingsByType(self, Type):
		result_mappings = []
		for m in self.mappings:
			if m['subjectMap']['class'] == Type:
				result_mappings.append(m)
		return result_mappings

	def getLogicalSourceByMapping(self, mapping):
		logical_source = None
		for ls in self.logical_sources:
			if ls['name'] == mapping['logicalSource']:
				logical_source = ls
				break
		return logical_source
	
	def getSubjectTemplateByMapping(self,mapping):
		return mapping['subjectMap']['template']
	
	def getLSType(self, logicalSource):
		return logicalSource['referenceFormulation']
	
	def getSource(self, logicalSource):
		return logicalSource['source']
	
	def getDBSource(self, logicalsource):
		query = logicalsource['query']
		server_info = None
		for db_source in self.dbsources:
			if db_source['name'] == logicalsource['source']:
				server_info = db_source
				break
		return server_info, query

	def getJSONIterator(self, logicalSource):
		iterator = logicalSource['iterator']
		if '[*]' in iterator:
			position = iterator.index('[*]')
			return iterator[1:position]
		else:
			return iterator[1:]
	
	def getPredicateObjectMapByPred(self, mapping, predicates):
		poms = self.getPredicateObjectMap(mapping)
		poms = [pom for pom in poms if pom['predicate'] in predicates]
		return poms
	
	def parsePOM(self, pom):
		return pom['predicate'], pom['objectMap']
	
	def getReference(self, termMap):
		return termMap['reference']
	
	def parseROM(self, objectMap):
		mapping_name = objectMap['parentTriplesMap']
		joinCondition = objectMap['joinCondition']
		parentMapping = self.getMappingsByName(mapping_name)
		return parentMapping, joinCondition
	
	def parseJoinCondition(self, joinCondition):
		return joinCondition['child'], joinCondition['parent']
	
	def TypeOfObjectMap(self, objectMap):
		if 'reference' in objectMap.keys():
			return 1
		if 'constant' in objectMap.keys():
			return 2
		if 'parentTriplesMap' in objectMap.keys():
			return 3
		return 0
	
	def getPredicateObjectMap(self, mapping):
		return mapping['predicateObjectMap']
	
	def getMappingsByName(self, mapping_name):
		result_mapping = None
		for m in self.mappings:
			if m['name'] == mapping_name:
				result_mapping = m
				break
		return result_mapping