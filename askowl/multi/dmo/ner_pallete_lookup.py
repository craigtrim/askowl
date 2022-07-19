# !/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Find a Pallete to associate to NER types """


import os
from random import randint

from baseblock import FileIO
from baseblock import BaseObject


class NerPalleteLookup(BaseObject):
    """ Find a Pallete to associate to NER types """

    _d_merge_taxorev = None

    def __init__(self,
                 d_ner_taxonomy_rev: dict):
        """ Change Log

        Created:
            27-Oct-2021
            craig@graffl.ai
            *   https://github.com/grafflr/graffl-core/issues/94
        Updated:
            1-Feb-2022
            craig@graffl.ai
            *   enforce ontologies as a list param in domain components
                https://github.com/grafflr/graffl-core/issues/135#issuecomment-1027464370
        Updated:
            27-May-2022
            craig@graffl.ai
            *   migrated into 'owlblock' in pursuit of 
                https://github.com/grafflr/deepnlu/issues/13

        Args:
            d_ner_taxonomy_rev (dict): reversed NER Taxonomy dictionary
        """
        BaseObject.__init__(self, __name__)
        self._d_palletes = self._load_config()

        self._d_ner_taxonomy_rev = d_ner_taxonomy_rev
        self._ner_taxonomy_keys = sorted(self._d_ner_taxonomy_rev.keys())

        self._d_assoc = self._configure()

    @staticmethod
    def _load_config() -> dict:
        path = os.path.normpath(os.path.join(
            os.getcwd(),
            'resources/palletes.yaml'))

        FileIO.exists_or_error(path)

        return FileIO.read_yaml(path)['palletes']

    def _configure(self) -> int or None:

        d_assoc = {}
        used_keys = []

        pallete_keys = sorted(self._d_palletes.keys())

        for i in range(len(self._ner_taxonomy_keys)):

            def pallete_key(n: int) -> int:
                x = randint(0, len(pallete_keys) - 1)
                if x not in used_keys:
                    used_keys.append(x)
                    return x
                if n > len(pallete_keys):
                    return 0
                return pallete_key(n + 1)

            ners = self._d_ner_taxonomy_rev[self._ner_taxonomy_keys[i]]
            pallete = pallete_keys[pallete_key(0)]
            colors = self._d_palletes[pallete]['colors']

            for j in range(len(ners)):
                if ners[j] not in d_assoc:

                    def color_key() -> int:
                        if j >= len(colors):
                            return 0
                        return j

                    d_assoc[ners[j]] = f"#{colors[color_key()]}"

        return d_assoc

    def lookup(self,
               input_text: str) -> str:
        return self._d_assoc[input_text]

    def colors(self) -> dict:
        return self._d_assoc
