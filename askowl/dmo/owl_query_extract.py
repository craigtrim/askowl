#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Perform the RDF Query """


from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.plugins.sparql.processor import SPARQLResult

from collections import defaultdict

from baseblock import BaseObject

from askowl.dto import QueryResultType


class OwlQueryExtract(BaseObject):
    """ Perform the RDF Query """

    def __init__(self,
                 graph: Graph):
        """ Change History

        Created:
            13-Oct-2021
            craig@grafflr.ai
            *   refactored out of 'owl-data-extract'
                https://github.com/grafflr/graffl-core/issues/38
        Updated:
            2-Feb-2022
            craig@grafflr.ai
            *   do not split designated string datatypes
                https://github.com/grafflr/graffl-core/issues/156
        Updated:
            25-May-2022
            craig@grafflr.ai
            *   refactor into 'ask-owl' repo
                https://github.com/grafflr/ask-owl/issues/1
        Updated:
            27-May-2022
            craig@grafflr.ai
            *   expose ability to lowercase output
                https://github.com/grafflr/ask-owl/issues/9

        Args:
            graph (Graph): an instantiated RDF graph
        """
        BaseObject.__init__(self, __name__)
        self._graph = graph

    def _log_no_rows_found(self,
                           query_type: QueryResultType) -> None:
        
        self.logger.warning('\n'.join([
            "Result Set Transformation Failure",
            f"\tReason: No Rows Found",
            f"\tTransform: {query_type.name}"]))

    def _transform(self,
                   value: object,
                   to_lowercase: bool) -> str:
        _type = type(value)

        if _type == URIRef:
            value = value.title().split('#')[-1].strip()
            if to_lowercase:
                value = value.lower()
            return value

        elif _type == Literal:
            value = str(value).strip()
            if to_lowercase:
                value = value.lower()
            return value

        else:
            self.logger.error('\n'.join([
                "DataType Not Recognized",
                f"\tActual Type: {_type}"]))
            raise NotImplementedError

    def _list_of_strings(self,
                         query_results: SPARQLResult,
                         to_lowercase: bool) -> list:
        results = []

        rows = [x for x in query_results if len(x) >= 1]

        if not len(rows):
            self._log_no_rows_found(QueryResultType.LIST_OF_STRINGS)
            return None

        for row in rows:
            results.append(self._transform(row[0], to_lowercase))

        return results

    def _dict_of_str2str(self,
                         query_results: SPARQLResult,
                         to_lowercase: bool) -> dict:
        d = {}

        rows = [x for x in query_results if len(x) >= 2]
        if not len(rows):
            self._log_no_rows_found(QueryResultType.DICT_OF_STR2STR)
            return None

        for row in rows:
            key = self._transform(row[0], to_lowercase)
            value = self._transform(row[1], to_lowercase)
            d[key] = value

        return d

    def _dict_of_str2list(self,
                          query_results: SPARQLResult,
                          to_lowercase: bool) -> dict:
        d = defaultdict(list)

        rows = [x for x in query_results if len(x) >= 2]
        if not len(rows):
            self._log_no_rows_found(QueryResultType.DICT_OF_STR2LIST)
            return None

        for row in rows:
            key = self._transform(row[0], to_lowercase)
            value = self._transform(row[1], to_lowercase)
            d[key].append(value)

        return dict(d)

    def _update(self,
                query_results: SPARQLResult,
                to_lowercase: bool,
                result_type: QueryResultType) -> object:

        if result_type == QueryResultType.LIST_OF_STRINGS:
            return self._list_of_strings(query_results, to_lowercase)

        elif result_type == QueryResultType.DICT_OF_STR2STR:
            return self._dict_of_str2str(query_results, to_lowercase)

        elif result_type == QueryResultType.DICT_OF_STR2LIST:
            return self._dict_of_str2list(query_results, to_lowercase)

        else:
            raise NotImplementedError

    def process(self,
                query: str,
                to_lowercase: bool,
                result_type: QueryResultType) -> dict:
        try:

            result = self._graph.query(query)
            if result_type == QueryResultType.DO_NOT_TRANSFORM:
                return result

            svcresult = self._update(
                query_results=result,
                to_lowercase=to_lowercase,
                result_type=result_type)

            return svcresult
        except Exception as e:
            print(e)
            self.logger.error('\n'.join([
                "Parsing Exception",
                f"\tQuery:\n{query}"]))
            raise ValueError('OWL Query Failed')
