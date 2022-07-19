#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" View Generator: Trie Grams """


from collections import defaultdict

from baseblock import BaseObject


class GenerateViewTrie(BaseObject):
    """ View Generator: Trie Grams """

    def __init__(self):
        """ Change Log

        Created:
            27-May-2022
            craigtrim@gmail.com
            *   https://github.com/craigtrim/askowl/issues/8
        """
        BaseObject.__init__(self, __name__)

    @staticmethod
    def _to_gramsize_dict(d_results: dict) -> dict:
        d = defaultdict(list)
        for k in d_results:

            name = k.replace('_', ' ')
            gram_size = len(name.split(' '))
            d[gram_size].append(name)

        return d

    @staticmethod
    def _sort(tokens: list) -> list:
        values = sorted(set(tokens), key=len)
        values.reverse()
        return values

    def _trie(self,
              tokens: list) -> dict:
        d = defaultdict(list)

        for k in tokens:
            values = k.split(' ')
            d[values[0]].append(' '.join(values[1:]))

        def decide(obj):

            if type(obj) == list:
                if ' ' in obj[0]:
                    return self._trie(obj)
                return self._sort(obj)
            raise NotImplementedError(type(obj))

        return {k: decide(d[k]) for k in d}

    def process(self,
                d_results: dict) -> dict:

        d_gramsize = self._to_gramsize_dict(d_results)

        d_gramsize[1] = self._sort(d_gramsize[1])
        d_gramsize[2] = self._trie(d_gramsize[2])
        d_gramsize[3] = self._trie(d_gramsize[3])
        d_gramsize[4] = self._trie(d_gramsize[4])
        d_gramsize[5] = self._trie(d_gramsize[5])
        d_gramsize[6] = self._trie(d_gramsize[6])

        return dict(d_gramsize)
