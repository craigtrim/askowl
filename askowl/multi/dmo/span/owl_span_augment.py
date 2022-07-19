#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Perform Runtime KB Transformation """


from baseblock import BaseObject


class OwlSpanAugment(BaseObject):
    """Augment Lookup with Possible Permuations

    Sample Input:
        {
            2: [
                'clinical outcome',
                'outcome evaluation',
            ],
            3: [
                'clinical outcome evaluation'
            ]
        }

    Sample Output:
        {
            2: [
                'clinical outcome',
                'clinical_outcome evaluation',
                'clinical outcome_evaluation',
                'outcome evaluation',
            ],
            3: [
                'clinical outcome evaluation'
            ]
        }

    Purpose:
        given this input text:
            "clinical outcome evaluations"

        there is no trigram for this exact match

        these swaps occur:
            "clinical outcome"      -->     "clinical_outcome"
            "evaluations"           -->     "evaluation"

        which leaves
            clinical_outcome evaluation

        but this term does not match
            clinical outcome evaluation

        so this algorithm will augment the possible choices by 
            adding in possible swaps that can occur in the context
            of longer gram choices
    """

    __blacklist = [
        'and',
        'for',
        'of',
        'to',
    ]

    def __init__(self):
        """ Change Log

        Created:
            15-Oct-2021
            craig.@graffl.ai
            *   https://github.com/grafflr/graffl-core/issues/54
        Updated:
            26-May-2022
            craig@graffl.ai
            *   migrated to ask-owl in pursuit of
                https://github.com/grafflr/ask-owl/issues/4
        """
        BaseObject.__init__(self, __name__)

    def _to_result_set(self,
                       buffer: list) -> list:

        def is_valid(a_tuple: tuple) -> bool:
            for item in self.__blacklist:
                if item in a_tuple:
                    return False
            return True

        results = set()

        buffer = [x for x in buffer if is_valid(x)]
        [results.add(' '.join(x).strip()) for x in buffer]

        return sorted(results, key=len)

    def _grams_by_n(self,
                    n: int,
                    values: list) -> list:
        buffer = []

        for value in values:
            tokens = value.split(' ')
            for i in range(len(tokens)):
                if i + n < len(tokens):
                    gramresult = []
                    j = 0
                    while j < n:
                        gramresult.append(tokens[i+j])
                        j += 1
                    buffer.append(gramresult)

        return self._to_result_set(buffer)

    def process(self,
                d_gramsize: dict) -> dict:

        gram2 = set(d_gramsize[2])
        gram3 = set(d_gramsize[3])
        gram4 = set(d_gramsize[4])
        gram5 = set(d_gramsize[5])

        def augment(value: str) -> None:
            size = len(value.split(' '))
            if size == 2:
                gram2.add(value)
            elif size == 3:
                gram3.add(value)
            elif size == 4:
                gram4.add(value)
            elif size == 5:
                gram5.add(value)

        def iterate(func, n, values) -> None:
            grams = func(n, values)
            for value in values:
                for gram in grams:
                    if gram in value:

                        _gram = gram.replace(' ', '_')
                        _value = value.replace(gram, _gram)
                        augment(_value)

        iterate(self._grams_by_n, 5, d_gramsize[6])
        iterate(self._grams_by_n, 4, d_gramsize[5])
        iterate(self._grams_by_n, 3, d_gramsize[4])
        iterate(self._grams_by_n, 2, d_gramsize[3])

        d_gramsize[2] = gram2
        d_gramsize[3] = gram3
        d_gramsize[4] = gram4
        d_gramsize[5] = gram5

        return dict(d_gramsize)
