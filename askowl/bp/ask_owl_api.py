#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" API for the ask-owl Microservice """


from functools import lru_cache
from collections import defaultdict

from rdflib.plugins.sparql.processor import SPARQLResult

from baseblock import BaseObject

from askowl.svc import LoadOntologyModel
from askowl.svc import QueryOntologyModel
from askowl.svc import GenerateViewTrie
from askowl.svc import GenerateViewSpans
from askowl.svc import GenerateViewSynonyms
from askowl.dto import QueryResultType


class AskOwlAPI(BaseObject):
    """ API for the ask-owl Microservice """

    def __init__(self,
                 ontology_name: str,
                 absolute_path: str):
        """ Change Log

        Created:
            25-May-2022
            craigtrim@gmail.com
            *   https://github.com/craigtrim/askowl/issues/1
        Created:
            6-Jun-2022
            craigtrim@gmail.com
            *   simplify __init__ method in pursuit of
                https://github.com/craigtrim/askowl/issues/2

        Args:
            ontology_name (str): the name of the Ontology (OWL) model
            absolute_path (str): the absolute path to the OWL model

        Raises:
            ValueError: OWL Model Not Found
        """
        BaseObject.__init__(self, __name__)
        self.ontology_name = ontology_name
        self.absolute_path = absolute_path

        self.graph, self.prefix, self.namespace = self._load_models(
            ontology_name=ontology_name,
            absolute_path=absolute_path)

        self._execute_query = QueryOntologyModel(self.graph).process

    def _load_models(self,
                     ontology_name: str,
                     absolute_path: str):
        try:

            dmo = LoadOntologyModel(
                ontology_name=ontology_name,
                absolute_path=absolute_path)

            return dmo.process(), dmo.prefix, dmo.namespace

        except FileNotFoundError as e:
            self.logger.error('\n'.join([
                "OWL Model Not Found",
                f"\tName: {ontology_name}",
                f"\tAbsolute Path: {absolute_path}"]))

        raise ValueError

    # def prefix(self) -> str:
    #     return self._model_loader.prefix

    def adhoc(self,
              sparql_query: str,
              to_lowercase: bool,
              result_type: QueryResultType = QueryResultType.DO_NOT_TRANSFORM) -> SPARQLResult:
        """ Execute an ad-hoc SPARQL query on the OWL model

        Args:
            sparql_query (str): the SPARQL query
                no validation will occur on this query

        Returns:
            SPARQLResult: the SPARQL result set
        """
        return self._execute_query(
            reverse=False,
            sparql=sparql_query,
            result_type=result_type,
            to_lowercase=to_lowercase)

    @lru_cache(maxsize=6, typed=False)
    def ngrams(self,
               gram_level: 1) -> list or None:
        """ Generate n-Grams by Size

        Args:
            gram_level (1): the gram level to query for

        Returns:
            list or None: the n-Gram results (if any)
        """
        sparql = "SELECT ?a WHERE { ?a rdfs:subClassOf ?b }"

        results = self._execute_query(
            sparql=sparql,
            to_lowercase=True,
            result_type=QueryResultType.LIST_OF_STRINGS,
        )

        if not results or not len(results):
            return None

        return [x for x in results if x.count('_') == gram_level - 1]

    @lru_cache
    def trie(self) -> dict or None:
        """ Generate Entities in a Trie View

        Sample Input:
            ['First Quarter Results', 'First Quarter GDP', 'First Time']

        Sample Output:
            {
                'First': {
                    'Quarter': ['Results', 'GDP'],
                    'Time': [],
                }
            }

        Reference:
            https://github.com/craigtrim/askowl/issues/8

        Args:
            to_lowercase (bool, optional): lowercase all data. Defaults to True.

        Returns:
            dict: dictionary of values keyed by n-gram size
        """
        sparql = "SELECT ?a ?b WHERE  {  ?a rdfs:subClassOf ?b }"
        d_results = self._execute_query(
            sparql=sparql,
            to_lowercase=True,
            result_type=QueryResultType.DICT_OF_STR2LIST,
        )

        if not d_results or not len(d_results):
            return None

        return GenerateViewTrie().process(d_results)

    @lru_cache(typed=False)
    def by_subject_predicate(self,
                             predicate: str,
                             subject: str,
                             to_lowercase: bool = True) -> list:
        """ Retrieve a list of values by custom subject and custom predicate

        Args:
            predicate (str): the predicate name
            subject (str): the subject name
            to_lowercase (str, optional): optionally lowercase all results.  Defaults to True.

        Returns:
            list: a list of values for this predicate
        """
        sparql = "SELECT ?b WHERE { #PREFIX:#SUBJECT rdf:type owl:Class ; #PREFIX:#PREDICATE ?b }"
        sparql = sparql.replace('#PREFIX', self.prefix)
        sparql = sparql.replace('#PREDICATE', predicate)
        sparql = sparql.replace('#SUBJECT', subject)

        d_results = self._execute_query(
            sparql=sparql,
            to_lowercase=to_lowercase,
            result_type=QueryResultType.LIST_OF_STRINGS,
        )

        return d_results

    @lru_cache(typed=False)
    def by_predicate(self,
                     predicate: str,
                     to_lowercase: bool = True,
                     reverse: bool = False) -> list:
        """ Retrieve a list of values by custom predicate

        Args:
            predicate (str): the predicate name
            to_lowercase (str, optional): optionally lowercase all results.  Defaults to True.
            reverse (bool, optional): reverses the subject/object order. Defaults to False.
                if "?x implies ?y" and reverse=False
                    the results will be { ?x: [?y-1, ?y-2, ..., ?y-N]}
                if "?x implies ?y" and reverse=True
                    the results will be { ?y-1: [x], ?y-2: [x], ?y-N: [x]}

        Returns:
            dict: a dict of values for this predicate
        """
        sparql = "SELECT ?a ?b WHERE { ?a #PREFIX:#PREDICATE ?b }"

        def get_prefix() -> str:
            if ':' in predicate:
                return predicate.split(':')[0].strip()
            return self.prefix

        def get_predicate() -> str:
            if ':' in predicate:
                return predicate.split(':')[-1].strip()
            return predicate

        _prefix = get_prefix()
        _predicate = get_predicate()

        sparql = sparql.replace('#PREFIX', _prefix)
        sparql = sparql.replace('#PREDICATE', _predicate)

        d_results = self._execute_query(
            sparql=sparql,
            reverse=reverse,
            to_lowercase=to_lowercase,
            result_type=QueryResultType.DICT_OF_STR2LIST,
        )

        return d_results

    @lru_cache
    def labels(self) -> list:
        """ Retrieve rdfs:label values from the Graph

        Returns:
            list: a list of labels
        """
        sparql = "SELECT ?a WHERE { ?x rdfs:label ?a }"
        return self._execute_query(
            sparql=sparql,
            to_lowercase=False,
            result_type=QueryResultType.LIST_OF_STRINGS)

    @lru_cache
    def comments(self) -> list:
        """ Retrieve rdfs:comment values from the Graph

        Returns:
            list: a list of labels
        """
        sparql = "SELECT ?a ?b WHERE { ?a rdfs:comment ?b }"

        d_results = self._execute_query(
            sparql=sparql,
            to_lowercase=False,
            result_type=QueryResultType.DICT_OF_STR2LIST,
        )

        return d_results

    @lru_cache
    def see_also(self,
                 to_lowercase: bool = True) -> list:
        """ Retrieve rdfs:seeAlso values from the Graph

        Args:
            to_lowercase (str, optional): optionally lowercase all results.  Defaults to True.

        Returns:
            list: a list of see-also values
        """
        sparql = "SELECT ?a WHERE { ?x rdfs:seeAlso ?a }"
        return self._execute_query(
            sparql=sparql,
            to_lowercase=to_lowercase,
            result_type=QueryResultType.LIST_OF_STRINGS)

    @lru_cache
    def backward_compatible_with(self,
                                 to_lowercase: bool = True) -> list:
        """ Retrieve owl:backwardCompatibleWith values from the Graph

        Args:
            to_lowercase (str, optional): optionally lowercase all results.  Defaults to True.

        Returns:
            list: a list of see-also values
        """
        sparql = "SELECT ?a WHERE { ?x rdfs:seeAlso ?a }"
        return self._execute_query(
            sparql=sparql,
            to_lowercase=to_lowercase,
            result_type=QueryResultType.LIST_OF_STRINGS)

    @lru_cache
    def types(self,
              to_lowercase: bool = True) -> list:
        """ Retrieve rdf:type values from the Graph

        Args:
            to_lowercase (str, optional): optionally lowercase all results.  Defaults to True.

        Returns:
            list: a list of labels
        """
        sparql = "SELECT ?a WHERE { ?a rdf:type ?x }"
        return self._execute_query(
            sparql=sparql,
            to_lowercase=to_lowercase,
            result_type=QueryResultType.LIST_OF_STRINGS)

    @lru_cache
    def _synonym_query(self) -> dict or None:
        """ Generate n-Gram Spans suitable for Synonym Matching

        Reference:
            https://github.com/craigtrim/askowl/issues/8

        Returns:
            dict: dictionary of values keyed by n-gram size
        """
        sparql = """
        SELECT 
            ?a ?b 
        WHERE 
        { 
            {
                { ?a rdfs:label ?b }
                OPTIONAL {?a rdfs:seeAlso ?b}
            } UNION
            {
                { ?a rdfs:seeAlso ?b }
                OPTIONAL {?a rdfs:label ?b}

            }
        }
        """
        d_results = self._execute_query(
            sparql=sparql,
            to_lowercase=True,
            result_type=QueryResultType.DICT_OF_STR2LIST,
        )

        if not d_results or not len(d_results):
            return None

        d_normalized = defaultdict(list)
        for k in d_results:
            for synonym in d_results[k]:
                synonyms = [x.strip() for x in synonym.split(',')]
                synonyms = [x for x in synonyms if x and len(x)]
                [d_normalized[k].append(x) for x in synonyms]

        return d_normalized

    @lru_cache
    def synonyms(self) -> dict or None:
        """ Generate a Dictionary of Entities keyed to Synonym Lists

        Reference:
            https://github.com/craigtrim/askowl/issues/8

        Returns:
            dict: dictionary of entities keyed by synonym
        """
        d_results = self._synonym_query()

        if not d_results or not len(d_results):
            return None

        return GenerateViewSynonyms().process(d_results)

    @lru_cache
    def synonyms_rev(self) -> dict:
        """ Reverse Synonym Dictionary:
        Synonyms are keyed to one-or-more Entities

        Reference:
            https://github.com/craigtrim/askowl/issues/8

        Returns:
            dict: dictionary of synonyms keyed by entity
        """
        d_results = self._synonym_query()

        if not d_results or not len(d_results):
            return None

        return GenerateViewSynonyms().process(d_results, reverse=True)

    @lru_cache
    def spans(self) -> dict or None:
        """ Entity Spans for Long-Range Matching

        Reference:
            https://github.com/craigtrim/askowl/issues/5

        Returns:
            dict: dictionary of spans keyed by entity name
        """
        sparql = "SELECT ?a ?b WHERE { { ?a rdfs:label ?b } UNION { ?a rdfs:seeAlso ?b } }"

        d_results = self._execute_query(
            sparql=sparql,
            to_lowercase=True,
            result_type=QueryResultType.DICT_OF_STR2LIST,
        )

        if not d_results or not len(d_results):
            return None

        return GenerateViewSpans().process(d_results)
