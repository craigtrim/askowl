# !/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Generic Facade to Find Data in 1..* Ontology Models """


from baseblock import BaseObject

from askowl.single.dto import QueryResultType

from askowl.multi.dmo import ModelResultMerge
from askowl.multi.dmo import ViewGeneratorNerLabel


class QueryNerLabel(BaseObject):
    """ Generic Facade to Find Data in 1..* Ontology Models """

    __SPARQL_QUERY = """
            SELECT 
                ?label ?NER 
            WHERE 
            { 
                ?entity owl:backwardCompatibleWith ?NER
                {
                    ?child rdfs:subClassOf* ?entity
                    { ?child rdfs:label ?label }
                    UNION
                    { ?child rdfs:seeAlso ?label }
                }
                OPTIONAL
                {
                    { ?entity rdfs:label ?label }
                    UNION
                    { ?entity rdfs:seeAlso ?label }        
                }
                
                FILTER 
                ( 
                    datatype(?NER) = $PREFIX:$NER
                )
            }
        """

    def __init__(self,
                 d_ontologies: list):
        """ Change Log

        Created:
            27-May-2022
            craig@graffl.ai
            *   https://github.com/grafflr/deepnlu/issues/13

        Args:
            d_ontologies (list): in-memory graph model keyed by name
        """
        BaseObject.__init__(self, __name__)
        self._merge = ModelResultMerge().process
        self._d_ontologies = d_ontologies
        self._generate_view = ViewGeneratorNerLabel().process

    def _get_results(self,
                     ner_type: str) -> list:
        results = []
        for ontology_name in self._d_ontologies:

            ask_owl_api = self._d_ontologies[ontology_name]

            sparql_query = self.__SPARQL_QUERY

            sparql_query = sparql_query.replace(
                '$PREFIX', ontology_name)

            sparql_query = sparql_query.replace(
                '$NER', ner_type)

            results.append(ask_owl_api.adhoc(
                sparql_query=sparql_query,
                to_lowercase=True,
                result_type=QueryResultType.DICT_OF_STR2LIST))

        if not results:
            return None

        elif len(results) == 1:
            return results[0]

        return self._merge(results, QueryResultType.DICT_OF_STR2LIST)

    def process(self,
                ner_type: str,
                reverse: bool = False) -> dict or None:

        d_results = self._get_results(ner_type)

        if not d_results or not len(d_results):
            return None

        return self._generate_view(
            reverse=reverse,
            d_results=d_results)
