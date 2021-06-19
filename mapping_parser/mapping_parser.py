import sys
import json
from collections import defaultdict
from rdflib import Graph

triples = defaultdict(lambda: defaultdict(list))

class_dict = defaultdict()
constant_dict = defaultdict()
datatype_dict = defaultdict()
iterator_dict = defaultdict()
logicalSource_dict = defaultdict()
objectMap_dict = defaultdict()
parentTriplesMap_dict = defaultdict()
predicate_dict = defaultdict()
predicateObjectMap_dict = defaultdict(list)
reference_dict = defaultdict()
referenceFormulation_dict = defaultdict()
source_dict = defaultdict()
subjectMap_dict = defaultdict()
templateMap_dict = defaultdict()
joinCondition_dict = defaultdict()
child_dict = defaultdict()
parent_dict = defaultdict()

source_server_dict = defaultdict()
server_schema_dict = defaultdict()
server_username_dict = defaultdict()
server_password_dict = defaultdict()
#rr:tableName  "review";
table_name_dict = defaultdict()
query_dict = defaultdict()


def read_file(file_name):
	content = ''
	with open(file_name) as f:
		content = f.read()
	return content


def remove_prefix(s):
	if 'http' in s:
		if '#' in s:
			return s.split('#')[1]
		else:
			return s.split('/')[-1]
	else:
		return s


def parse_mapping(mapping_file='venue-mapper.ttl', mapping_format='n3'):
	mapping_graph = Graph()
	file = open('all_triples.txt', 'w')
	mapping_graph.parse(mapping_file, format=mapping_format)
	for subj, pred, obj in mapping_graph:
		subj = remove_prefix(subj.toPython())
		pred = remove_prefix(pred.toPython())
		# obj = remove_prefix(obj.toPython())
		triples[pred][subj].append(obj)
		file.writelines('{} {} {}\n'.format(subj, pred, obj))
		if pred == 'class':
			obj = remove_prefix(obj.toPython())
			class_dict[subj] = obj
		if pred == 'constant':
			obj = remove_prefix(obj.toPython())
			constant_dict[subj] = obj
		if pred == 'datatype':
			obj = remove_prefix(obj.toPython())
			datatype_dict[subj] = obj
		if pred == 'iterator':
			obj = remove_prefix(obj.toPython())
			iterator_dict[subj] = obj
		if pred == 'logicalSource':
			obj = remove_prefix(obj.toPython())
			logicalSource_dict[subj] = obj
		if pred == 'tableName':
			obj = remove_prefix(obj.toPython())
			table_name_dict[subj] = obj
		if pred == 'objectMap':
			obj = remove_prefix(obj.toPython())
			objectMap_dict[subj] = obj
		if pred == 'parentTriplesMap':
			obj = remove_prefix(obj.toPython())
			parentTriplesMap_dict[subj] = obj
		if pred == 'predicate':
			obj = remove_prefix(obj.toPython())
			predicate_dict[subj] = obj
		if pred == 'predicateObjectMap':
			obj = remove_prefix(obj.toPython())
			predicateObjectMap_dict[subj].append(obj)
		if pred == 'reference' or pred == 'column':
			obj = remove_prefix(obj.toPython())
			reference_dict[subj] = obj
		if pred == 'referenceFormulation':
			obj = remove_prefix(obj.toPython())
			referenceFormulation_dict[subj] = obj
		if pred == 'source':
			source_dict[subj] = obj.toPython()
		if pred == 'subjectMap':
			obj = remove_prefix(obj.toPython())
			subjectMap_dict[subj] = obj
		if pred == 'template':
			# obj = remove_prefix(obj.toPython())
			templateMap_dict[subj] = obj.toPython()
		if pred == 'joinCondition':
			obj = remove_prefix(obj.toPython())
			joinCondition_dict[subj] = obj
		if pred == 'child':
			obj = remove_prefix(obj.toPython())
			child_dict[subj] = obj
		if pred == 'parent':
			obj = remove_prefix(obj.toPython())
			parent_dict[subj] = obj
		if pred == 'server':
			source_server_dict[subj] = obj.toPython()
		if pred == 'username':
			server_username_dict[subj] = obj.toPython()
		if pred == 'password':
			server_password_dict[subj] = obj.toPython()
		if pred == 'jdbcDSN':
			server_schema_dict[subj] = obj.toPython()
		if pred == 'query':
			query_dict[subj] = obj.toPython()
	return mapping_graph


def generateSourceList():
	return 0


def getDBSourceList():
	db_source_lst = []
	for (key, value) in server_schema_dict.items():
		source_rec = {'name': key, 'server': value, 'username': server_username_dict[key], 'password': server_password_dict[key]}
		db_source_lst.append(source_rec)
	return db_source_lst


def generateLogicalSourceList():
	logical_source_lst = []
	iterator_str = ''
	for (key, value) in source_dict.items():
		if key in iterator_dict.keys():
			iterator_str = iterator_dict[key]	
		if remove_prefix(value) in server_schema_dict.keys():
			table_name = ''
			query = ''
			if key in table_name_dict.keys():
				table_name = table_name_dict[key]
			if key in query_dict.keys():
				query = query_dict[key]
			ls_record = {'name': key, 'source': remove_prefix(value), 'referenceFormulation': 'ql:' + referenceFormulation_dict[key], 'table': table_name, 'query': query, 'iterator': iterator_str}
		else:
			ls_record = {'name': key, 'source': value, 'referenceFormulation': 'ql:' + referenceFormulation_dict[key], 'iterator': iterator_str}
		logical_source_lst.append(ls_record)
	return logical_source_lst


def generateMappingList():
	mappings_lst = []
	for (key, value) in logicalSource_dict.items():
		mapping_dict = dict()
		# render 'name' and 'logicalSource' fields
		mapping_dict['name'] = key
		mapping_dict['logicalSource'] = value
		# render 'subjectMap' field
		subject_map_key = subjectMap_dict[key]
		template = templateMap_dict[subject_map_key]
		class_of = class_dict[subject_map_key]
		poms_lst = []
		for pom_anonymous_name in predicateObjectMap_dict[key]:
			pom_dict = dict()
			pom_dict['predicate'] = predicate_dict[pom_anonymous_name]
			om_anonymous_name = objectMap_dict[pom_anonymous_name]
			if om_anonymous_name in reference_dict.keys():
				reference_field = reference_dict[om_anonymous_name]
				data_type = ''
				if om_anonymous_name in datatype_dict.keys():
					data_type = datatype_dict[om_anonymous_name]
				pom_dict['objectMap'] = {'reference': reference_field, 'datatype': data_type}
			if om_anonymous_name in constant_dict.keys():
				# this if block is not yet tested
				constant_value = constant_dict[om_anonymous_name]
				#data_type = ''
				#if om_anonymous_name in datatype_dict.keys():
				data_type = datatype_dict[om_anonymous_name]
				pom_dict['objectMap'] = {'constant': constant_value, 'datatype': data_type}
			if om_anonymous_name in parentTriplesMap_dict.keys():
				parent_mapping_name = parentTriplesMap_dict[om_anonymous_name]
				jc_anonymous_name = joinCondition_dict[om_anonymous_name]
				child_filed = child_dict[jc_anonymous_name]
				parent_field = parent_dict[jc_anonymous_name]
				pom_dict['objectMap'] = {'parentTriplesMap': parent_mapping_name, 'joinCondition': {'child': child_filed, 'parent': parent_field}}
			poms_lst.append(pom_dict)
		mapping_dict['subjectMap'] = {'template': template, 'class': class_of}
		mapping_dict['predicateObjectMap'] = poms_lst
		mappings_lst.append(mapping_dict)
	return mappings_lst

def write_json(mapping, output_file_name = 'mappings.json'):
	file_name = './' + output_file_name
	with open(file_name, 'w') as fp:
		json.dump(mapping, fp)


if __name__ == '__main__':
	g = parse_mapping(str(sys.argv[1]))
	output_file_name = str(sys.argv[2])
	logicalSource_lst = generateLogicalSourceList()
	mappings = generateMappingList()
	db_source = getDBSourceList()
	rml_mapping = {'DBSources': db_source, 'LogicalSources': logicalSource_lst, 'Mappings': mappings}
	write_json(rml_mapping, output_file_name)
