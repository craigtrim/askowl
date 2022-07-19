# !/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Merge Multiple Model results into a single and cohesive structure """


from collections import defaultdict

from baseblock import BaseObject

from askowl.single.dto import QueryResultType


class ModelResultMerge(BaseObject):
    """ Merge Multiple Model results into a single and cohesive structure """

    def __init__(self):
        """ Change Log

        Created:
            26-May-2022
            craig@graffl.ai
            *   https://github.com/grafflr/deepnlu/issues/2
        """
        BaseObject.__init__(self, __name__)

    def _merge(self,
               results: list,
               result_type: QueryResultType) -> list:

        results = [x for x in results if x is not None and len(x)]

        if result_type == QueryResultType.DICT_OF_STR2LIST:
            d_merge = defaultdict(list)
            for d_result in results:
                for k in d_result:
                    if k not in d_merge:
                        d_merge[k] = []

                    for value in d_result[k]:
                        if value not in d_merge[k]:
                            d_merge[k].append(value)

            return dict(d_merge)

        elif result_type == QueryResultType.DICT_OF_STR2DICT:
            d_merge = defaultdict(list)
            for d_result in results:
                for k in d_result:
                    for value in d_result[k]:
                        d_merge[k].append(value)

            return dict(d_merge)

        else:
            raise NotImplementedError

    def process(self,
                results: list,
                result_type: QueryResultType) -> list:

        d_model = self._merge(
            results=results,
            result_type=result_type)

        return d_model
