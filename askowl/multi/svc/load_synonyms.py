# !/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Generic Facade to find Synonym Data on Disk """

import os
from typing import Callable
from collections import defaultdict
from pprint import pprint
from functools import lru_cache

from baseblock import BaseObject
from baseblock import FileIO
from baseblock import Enforcer

from askowl.single import AskOwlAPI
from askowl.single.dto import QueryResultType
from askowl.multi.dmo import ExternalSynonymLoader


class LoadSynonyms(BaseObject):
    """ Generic Facade to find Synonym Data on Disk """

    def __init__(self,
                 d_ontologies: dict,
                 model_result_merge: Callable):
        """ Change Log

        Created:
            29-May-2022
            craig@graffl.ai
            *   in pursuit of
                https://github.com/grafflr/deepnlu/issues/18

        Args:
            d_ontologies (dict): a key:value dictionary of 'ontology_name<str> : AskOwlAPI()'
            model_result_merge (Callable): a callback to the model-result-merge component
        """
        BaseObject.__init__(self, __name__)
        self._merge = model_result_merge
        self._d_ontologies = d_ontologies

        self._d_external_fwd, self._d_external_rev = self._external_synonyms()

    def _external_synonyms(self) -> tuple:
        """ Load External Synonyms from File

        It's common for an ontology to have a complementary text file
            with entity names keyed by a list of synonyms

        The file name and location are identical to the OWL model
            with the exception of the file extension (.txt instead of .owl)

        Returns:
            _type_: a dictionary of external synonyms
        """

        d_external_fwd = {}
        d_external_rev = {}

        for ontology_name in self._d_ontologies:

            def api_instance() -> AskOwlAPI:
                return self._d_ontologies[ontology_name]

            ask_owl_api = api_instance()

            synonym_file_path = os.path.normpath(os.path.join(
                ask_owl_api.absolute_path,
                f"{ask_owl_api.ontology_name}.txt"))

            def get_synonyms() -> dict:
                if FileIO.exists(synonym_file_path):
                    return ExternalSynonymLoader(synonym_file_path).process()
                return {}  # the file is optional

            def get_reverse(d_fwd: dict) -> dict:
                d_rev = defaultdict(list)
                for k in d_fwd:
                    for v in d_fwd[k]:
                        d_rev[v].append(k)
                return dict(d_rev)

            d_fwd = get_synonyms()
            d_external_fwd[ontology_name] = d_fwd
            d_external_rev[ontology_name] = get_reverse(d_fwd)

        return d_external_fwd, d_external_rev

    @lru_cache
    def synonyms(self) -> dict:
        results = []
        for ontology_name in self._d_ontologies:

            d_owl_synonyms = self._d_ontologies[ontology_name].synonyms()
            if d_owl_synonyms and len(d_owl_synonyms):
                results.append(d_owl_synonyms)

            d_txt_synonyms = self._d_external_fwd[ontology_name]
            if d_txt_synonyms and len(d_txt_synonyms):
                results.append(d_txt_synonyms)

        if not results or not len(results):
            return None
        # elif len(results) == 1:
        #     return results[0]

        return self._merge(results, QueryResultType.DICT_OF_STR2LIST)

    @lru_cache
    def synonyms_rev(self) -> dict:
        results = []
        for ontology_name in self._d_ontologies:

            d_owl_synonyms = self._d_ontologies[ontology_name].synonyms_rev()
            if d_owl_synonyms and len(d_owl_synonyms):
                results.append(d_owl_synonyms)

            d_txt_synonyms = self._d_external_rev[ontology_name]
            if d_txt_synonyms and len(d_txt_synonyms):
                results.append(d_txt_synonyms)

        if not results:
            return None
        # elif len(results) == 1:
        #     return results[0]

        return self._merge(results, QueryResultType.DICT_OF_STR2LIST)
