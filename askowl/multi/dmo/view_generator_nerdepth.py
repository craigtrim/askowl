#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" View Generator: Graffl NER Types """


from collections import defaultdict

from baseblock import BaseObject


class ViewGeneratorNerDepth(BaseObject):
    """ View Generator: Graffl NER Types """

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
        """Find the depth of each NER entity to root

        The higher the associated number, the more specific the NER is

        Args:
            d_results (dict): [description]
            Sample Format:
                [
                    'competency':   {'2': 'integer'},
                    'condition':    {'0': 'integer'},
                    'continent':    {'1': 'integer'},
                ]

        Returns:
            dict: owl2py dictionary
        """
        d = {
            'NER': '0'  # default
        }

        for k in d_results:
            depth = int(d_results[k][0])
            d[k.upper()] = str(depth + 1)

        if reverse:
            return self._reverse(d)

        return dict(d)
