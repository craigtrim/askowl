#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" View Generator: Perform Synonym Transformation """


from collections import defaultdict

from baseblock import BaseObject
from baseblock import TextUtils


class GenerateViewSynonyms(BaseObject):
    """ View Generator: Perform Synonym Transformation """

    __punkt = [
        '!',
        '?',
        '.',
    ]

    def __init__(self):
        """ Change Log
        Created:
            7-Oct-2021
            craigtrim@gmail.com
            *   Create Owl2PY Util Service 
        Updated:
            2-Feb-2022
            craigtrim@gmail.com
            *   augment forms by removing punctuation
                Defect in Synonym Swapping when Punctuation is Present 
        Updated:
            27-May-2022
            craigtrim@gmail.com
            *   ported to ask-owl
                https://github.com/craigtrim/askowl/issues/6
        Updated:
            2-Jun-2022
            craigtrim@gmail.com
            *   tokenize spaces in synonyms
                https://github.com/craigtrim/askowl/issues/7
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
                reverse: bool = False) -> dict:
        d = {}

        for k in d_results:

            s = set()
            for value in d_results[k]:
                s.add(value.lower())

                # Reference: Defect in Synonym Swapping when Punctuation is Present
                # https://github.com/craigtrim/askowl/issues/11
                for punkt in self.__punkt:
                    if value.endswith(punkt):
                        s.add(value[:len(value) - len(punkt)])

                # Reference: Tokenization of Space Required
                # https://github.com/craigtrim/askowl/issues/7
                # TODO: likely need better testing around period vs ellipses vs multiple periods here
                if '.' in value and '...' not in value:
                    _value = value.replace('.', ' . ')
                    _value = TextUtils.update_spacing(_value)
                    s.add(_value)

            d[k.lower()] = sorted(s, key=len)

        if reverse:
            return self._reverse(d)

        return d
