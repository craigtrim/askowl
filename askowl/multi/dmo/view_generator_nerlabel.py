#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" View Generator: Associate NERs to Labels """


from collections import defaultdict

from baseblock import BaseObject


class ViewGeneratorNerLabel(BaseObject):
    """ View Generator: Associate NERs to Labels """

    def __init__(self):
        """ Change Log

        Created:
            12-Oct-2021
            craig.@graffl.ai
            *   https://github.com/grafflr/graffl-core/issues/38
        Updated:
            15-Oct-2021
            craig.@graffl.ai
            *   renamed from 'spacy-ner-transform'
                https://github.com/grafflr/graffl-core/issues/55
        Updated:
            27-May-2022
            craig@graffl.ai
            *   ported to 'deepnlu'
                https://github.com/grafflr/deepnlu/issues/10
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
        d = defaultdict(list)

        for k in d_results:
            for ner in d_results[k]:
                d[k.lower()].append(ner.upper().strip())

        if reverse:
            return self._reverse(d)

        return dict(d)
