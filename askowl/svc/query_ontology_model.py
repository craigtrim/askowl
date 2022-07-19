#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Query the in-memory Ontology Model """


from rdflib import Graph
from collections import defaultdict

from baseblock import Stopwatch
from baseblock import BaseObject

from askowl.dmo import OwlQueryExtract
from askowl.dto import QueryResultType


class QueryOntologyModel(BaseObject):
    """ Query the in-memory Ontology Model """

    def __init__(self,
                 graph: Graph):
        """ Change Log

        Created:
            25-May-2022
            craigtrim@gmail.com
            *   https://github.com/craigtrim/askowl/issues/1
        Updated:
            27-May-2022
            craigtrim@gmail.com
            *   expose ability to lowercase output
                https://github.com/craigtrim/askowl/issues/4

        Args:
            graph (Graph): the instantiated RDF graph
        """
        BaseObject.__init__(self, __name__)
        self._execute_query = OwlQueryExtract(graph).process

    @staticmethod
    def _reverse_order(d_results: dict,
                       result_type: QueryResultType) -> dict:

        if result_type == QueryResultType.DICT_OF_STR2LIST:
            d_rev = defaultdict(list)
            for k in d_results:
                for v in d_results[k]:
                    d_rev[v].append(k)
            return dict(d_rev)

        raise NotImplementedError

    def process(self,
                sparql: str,
                result_type: QueryResultType,
                reverse: bool = False,
                to_lowercase: bool = True) -> dict or list:
        """ Execute a SPARQL query on the RDF Graph

        Args:
            sparql (str): the SPARQL query to execute
            result_type (QueryResultType): the type of transformation to perform on the result set
            reverse (bool, optional): reverses the subject/object order. Defaults to False.
                if "?x implies ?y" and reverse=False
                    the results will be { ?x: [?y-1, ?y-2, ..., ?y-N]}
                if "?x implies ?y" and reverse=True
                    the results will be { ?y-1: [x], ?y-2: [x], ?y-N: [x]}
            to_lowercase (bool, optional): Ensures all output is lower-cased. Defaults to True.

        Returns:
            dict or list: the result set
        """

        sw = Stopwatch()

        d_results = self._execute_query(
            query=sparql,
            to_lowercase=to_lowercase,
            result_type=result_type)

        if not d_results or not len(d_results):
            if self.isEnabledForDebug:
                self.logger.info('\n'.join([
                    "Ontology Model Service Completed",
                    f"\tTotal Time: {str(sw)}",
                    f"\t*** No Results Found ***",
                    f"\tSPARQL Query: {sparql}"]))
            return None

        if reverse:
            d_results = self._reverse_order(
                d_results=d_results,
                result_type=result_type)

        if self.isEnabledForInfo:
            self.logger.info('\n'.join([
                "Ontology Model Service Completed",
                f"\tTotal Time: {str(sw)}",
                f"\tTotal Results: {len(d_results)}",
                f"\tSPARQL Query: {sparql}"]))

        return d_results
