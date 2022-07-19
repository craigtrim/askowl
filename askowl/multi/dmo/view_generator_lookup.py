#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" View Generator: Lookup Spans using N-Gram Input """


from baseblock import Stopwatch
from baseblock import BaseObject

from askowl.multi.dmo.span import OwlSpanGenerate
from askowl.multi.dmo.span import OwlSpanAugment


class ViewGeneratorLookup(BaseObject):
    """ View Generator: Lookup Spans using N-Gram Input """

    def __init__(self):
        """ Change Log

        Created:
            26-May-2022
            craig@graffl.ai
            *   https://github.com/grafflr/ask-owl/issues/4
        Created:
            30-May-2022
            craig@graffl.ai
            *   migrated from 'askowl' into 'deepnlu'
                https://github.com/grafflr/deepnlu/issues/21#issuecomment-1141518333
        """
        BaseObject.__init__(self, __name__)

    @staticmethod
    def _sort(tokens: list) -> list:
        values = sorted(set(tokens), key=len)
        values.reverse()
        return values

    def process(self,
                d_results: dict) -> dict:

        sw = Stopwatch()

        d_results = OwlSpanGenerate().process(d_results)
        d_results = OwlSpanAugment().process(d_results)

        d_results[1] = self._sort(d_results[1])
        d_results[2] = self._sort(d_results[2])
        d_results[3] = self._sort(d_results[3])
        d_results[4] = self._sort(d_results[4])
        d_results[5] = self._sort(d_results[5])
        d_results[6] = self._sort(d_results[6])

        if self.isEnabledForInfo:
            self.logger.info('\n'.join([
                "Generated OWL Spans",
                f"\tTotal Time: {str(sw)}",
                f"\tTotal Size: {len(d_results)}"]))

        return d_results
