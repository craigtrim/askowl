#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" View Generator: Generate NER Taxonomy """


from collections import defaultdict

from baseblock import BaseObject


class ViewGeneratorNerTaxo(BaseObject):
    """ View Generator: Generate NER Taxonomy """

    def __init__(self):
        """ Change Log

        Created:
            27-Oct-2021
            craig.@graffl.ai
            *   https://github.com/grafflr/graffl-core/issues/94
        Updated:
            27-May-2022
            craig@graffl.ai
            *   ported to 'deepnlu'
                https://github.com/grafflr/deepnlu/issues/12
        """
        BaseObject.__init__(self, __name__)

    @staticmethod
    def _reverse(d: dict) -> dict:
        d_rev = defaultdict(list)
        for k in d:
            for v in d[k]:
                d_rev[v].append(k)

        return dict(d_rev)

    def process(self,
                d_results: dict,
                reverse: bool) -> dict:
        d = {}

        for k in d_results:
            for ner in d_results[k]:
                d[k.upper().strip()] = [ner.upper().strip()]

        if reverse:
            return self._reverse(d)

        return d
