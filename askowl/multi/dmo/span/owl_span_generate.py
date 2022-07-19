#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Create Ontology Spans using N-Gram Input """


from pprint import pprint
from collections import defaultdict

from baseblock import BaseObject


class OwlSpanGenerate(BaseObject):
    """ Create Ontology Spans using N-Gram Input """

    __punkt = [
        '!',
        '?',
        '.',
    ]

    def __init__(self):
        """ Change Log

        Created:
            26-May-2022
            craig@graffl.ai
            *   https://github.com/grafflr/ask-owl/issues/4
        Updated:
            1-Jun-2022
            craig@graffl.ai
            *   add dedupe function
                https://github.com/grafflr/deepnlu/issues/28#issuecomment-1144270515

        """
        BaseObject.__init__(self, __name__)

    def _to_gramsize_dict(self,
                          d_results: dict) -> dict:
        d = defaultdict(list)
        for k in d_results:

            name = k.replace('_', ' ')
            gram_size = len(name.split(' '))
            d[gram_size].append(name)

            for v in d_results[k]:
                name = v.replace('_', ' ')
                gram_size = len(name.split(' '))
                d[gram_size].append(name)

                for punkt in self.__punkt:  # GRAFFL-155
                    if v.endswith(punkt):
                        d[gram_size].append(v[:len(v) - len(punkt)])

        return d

    @staticmethod
    def _lower(d_results: dict) -> dict:
        d = {}
        for k in d_results:
            d[k.lower()] = [v.lower().strip() for v in d_results[k]]

        return d

    @staticmethod
    def _dedupe(d_results: dict) -> dict:
        return {k: sorted(set(d_results[k])) for k in d_results}

    def process(self,
                d_results: dict) -> dict:

        d_results = self._lower(d_results)
        d_gramsize = self._to_gramsize_dict(d_results)

        # Rationale: https://github.com/grafflr/deepnlu/issues/28#issuecomment-1144270515
        d_gramsize = self._dedupe(d_gramsize)

        # enforce keys
        for i in range(1, 7):
            if i not in d_gramsize:
                d_gramsize[i] = []

        return d_gramsize
