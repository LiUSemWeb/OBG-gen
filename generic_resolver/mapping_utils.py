import json


class RML_Mapping(object):
    def __init__(self, mapping_file):
        self.rml_mapping = self.read_mappings(mapping_file)
        self.db_sources = self.rml_mapping['DBSources']
        self.logical_sources = self.rml_mapping['LogicalSources']
        self.mappings = self.rml_mapping['Mappings']

    @staticmethod
    def read_mappings(file):
        with open(file) as f:
            data = json.load(f)
            return data

    def get_mappings_by_type(self, concept_type):
        result_mappings = []
        for m in self.mappings:
            if m['subjectMap']['class'] == concept_type:
                result_mappings.append(m)
        return result_mappings

    def get_mappings_by_names(self, names):
        result_mappings = []
        for m in self.mappings:
            if m['name'] in names:
                result_mappings.append(m)
        return result_mappings

    def get_logical_source_by_mapping(self, mapping):
        logical_source = None
        for ls in self.logical_sources:
            if ls['name'] == mapping['logicalSource']:
                logical_source = ls
                break
        return logical_source

    @staticmethod
    def get_subject_template_by_mapping(mapping):
        return mapping['subjectMap']['template']

    @staticmethod
    def get_logical_source_type(logical_source):
        return logical_source['referenceFormulation']

    @staticmethod
    def get_source(logical_source):
        return logical_source['source']

    def get_db_source(self, logical_source):
        query = logical_source['query']
        server_info = None
        for db_source in self.db_sources:
            if db_source['name'] == logical_source['source']:
                server_info = db_source
                break
        return server_info, query
    @staticmethod
    def get_json_iterator(logical_source):
        iterator = logical_source['iterator']
        if '[*]' in iterator:
            position = iterator.index('[*]')
            return iterator[1:position]
        else:
            return iterator[1:]

    def get_pom_by_predicates(self, mapping, predicates):
        poms = self.get_pom(mapping)
        poms = [pom for pom in poms if pom['predicate'] in predicates]
        return poms

    @staticmethod
    def parse_pom(pom):
        return pom['predicate'], pom['objectMap']

    @staticmethod
    def get_reference(term_map):
        return term_map['reference']

    @staticmethod
    def get_constant_value_type(term_map):
        return term_map['constant'], term_map['datatype']

    def parse_rom(self, object_map):
        mapping_name = object_map['parentTriplesMap']
        join_condition = object_map['joinCondition']
        parent_mapping = self.get_mapping_by_name(mapping_name)
        return parent_mapping, join_condition

    @staticmethod
    def parse_join_condition(join_condition):
        return join_condition['child'], join_condition['parent']

    @staticmethod
    def type_of_object_map(object_map):
        if 'reference' in object_map.keys():
            return 1
        if 'constant' in object_map.keys():
            return 2
        if 'parentTriplesMap' in object_map.keys():
            return 3
        return 0

    @staticmethod
    def get_pom(mapping):
        return mapping['predicateObjectMap']

    def get_mapping_by_name(self, mapping_name):
        result_mapping = None
        for m in self.mappings:
            if m['name'] == mapping_name:
                result_mapping = m
                break
        return result_mapping
