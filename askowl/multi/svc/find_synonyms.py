# !/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Generic Facade to find Synonym Data on Disk """

from pprint import pprint


from baseblock import BaseObject
from baseblock import Enforcer

class FindSynonyms(BaseObject):

    """ Generic Facade to find Synonym Data on Disk """

    def __init__(self,
                 d_synonyms_fwd: dict,
                 d_synonyms_rev: dict):
        """ Change Log

        Created:
            7-Oct-2021
            craig@graffl.ai
            *   https://github.com/grafflr/graffl-core/issues/8
        Updated:
            11-Oct-2021
            craig@graffl.ai
            *   support args for 1..* names in param
                https://github.com/grafflr/graffl-core/issues/30#issuecomment-940252993
        Updated:
            25-Jan-2022
            craig@graffl.ai
            *   pass ontology-name as optional param
                https://github.com/grafflr/graffl-core/issues/135
        Updated:
            1-Feb-2022
            craig@graffl.ai
            *   use baseblock ontology name loader
                https://github.com/grafflr/graffl-core/issues/135
            *   a finder initialization is a contract
                https://github.com/grafflr/graffl-core/issues/135#issuecomment-1027474785
        Updated:
            26-May-2022
            craig@graffl.ai
            *   treat 'ontologies' param as a list
                https://github.com/grafflr/deepnlu/issues/7
        Updated:
            27-May-2022
            craig@graffl.ai
            *   migrated to 'owlblock' in pursuit of
                https://github.com/grafflr/deepnlu/issues/13
        Updated:
            30-May-2022
            craig@graffl.ai
            *   resilience testing
                https://github.com/grafflr/deepnlu/issues/20

        Args:
            ontologies (list): one-or-more Ontology models to use in processing
        """
        BaseObject.__init__(self, __name__)
        self._d_synonyms_fwd = d_synonyms_fwd
        self._d_synonyms_rev = d_synonyms_rev

    def d_synonyms_fwd(self):
        return self._d_synonyms_fwd

    def d_synonyms_rev(self):
        return self._d_synonyms_rev

    def _cleanse_canon(self,
                       input_text: str) -> str:
        if ' ' in input_text:
            input_text = input_text.replace(' ', '_')
        return input_text.lower().strip()

    def _cleanse_variant(self,
                         input_text: str) -> str:
        if '_' in input_text:
            input_text = input_text.replace('_', ' ')
        return input_text.lower().strip()

    def _has_synonyms_fwd(self) -> bool:
        """ No Synonyms Exist
        This result is unusual outside of unit-testing; but could happen

        Reference:    
            https://github.com/grafflr/deepnlu/issues/20

        Returns:
            bool: True if synonyms exist
        """
        return self._d_synonyms_fwd and len(self._d_synonyms_fwd)

    def _has_synonyms_rev(self) -> bool:
        """ No Synonyms Exist
        This result is unusual outside of unit-testing; but could happen

        Reference:    
            https://github.com/grafflr/deepnlu/issues/20

        Returns:
            bool: True if synonyms exist
        """
        return self._d_synonyms_fwd and len(self._d_synonyms_fwd)

    def is_canon(self,
                 input_text: str) -> bool:
        """Check if Input Text is Canonical Entity

        Args:
            input_text (str): any input string

        Returns:
            bool: True if the input string is a Nursing Entity
        """
        if not self._has_synonyms_fwd():
            return False

        return self._cleanse_canon(input_text) in self._d_synonyms_fwd

    def is_variant(self,
                   input_text: str) -> bool:
        """Check if Input Text is known variant for at least one Canonical Entry

        Args:
            input_text (str): any input string

        Returns:
            bool: True if the input string is a known synonym to a Nursing Entity
        """
        if not self._has_synonyms_rev():
            return False

        return self._cleanse_variant(input_text) in self._d_synonyms_rev

    def find_canon(self,
                   input_text: str) -> str or None:
        """Find the Canonical Representation of the Input String

        Args:
            input_text (str): any input string

        Returns:
            str or None: The Canonical Entity
        """

        input_text = self._cleanse_canon(input_text)
        if not input_text or not len(input_text):
            return None

        def find() -> str or None:

            # is canon
            if self._has_synonyms_fwd() and input_text in self._d_synonyms_fwd:
                return input_text

            # is variant
            if self._has_synonyms_rev():
                if input_text in self._d_synonyms_rev:
                    return self._d_synonyms_rev[input_text]
                if '_' in input_text:
                    temp = input_text.replace('_', ' ')
                    if temp in self._d_synonyms_rev:
                        return self._d_synonyms_rev[temp]

        result = find()
        if not result or not len(result):
            return None  # no canonical form exists

        def get_result() -> str:
            if type(result) == list:
                if len(result) > 1:
                    self.logger.warning('\n'.join([
                        f"Multi Typed Result (total={len(result)})",
                        f"\tInput: {input_text}",
                        f"\tTypes: {result}"]))
                return result[0]
            return result

        result = get_result()
        if self.isEnabledForDebug:
            Enforcer.is_str(result)

        return result

    def find_variants(self,
                      input_text: str) -> list:
        """Find the Synonyms for a known Entity

        Args:
            input_text (str): any input string

        Returns:
            list or None: a list of synonyms for the input entity
        """

        input_text = self._cleanse_variant(input_text)
        if not input_text or not len(input_text):
            return None

        def get_values() -> list:

            # is canon

            if self._has_synonyms_fwd() and input_text in self._d_synonyms_fwd:
                return self._d_synonyms_fwd[input_text]

            # is variant
            if self._has_synonyms_rev():
                if input_text in self._d_synonyms_rev:
                    s = set()
                    for canon in self._d_synonyms_rev[input_text]:
                        [s.add(x) for x in self._d_synonyms_fwd[canon]]
                    return sorted(s, key=len)

            return []

        values = [x for x in get_values() if x and len(x)]

        return values
