#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" View Generator: Entity Spans for Long-Range Synonym Swapping """


from collections import defaultdict

from baseblock import EnvIO
from baseblock import BaseObject


## ---------------------------------------------------------- ##
# Purpose:    List of Stopwords
# Reference:  https://github.com/craigtrim/askowl/issues/10
# Source:     https://gist.github.com/sebleier/554280#gistcomment-2596130
# Notes:      this list will likely be refined as needed over time
#             the 'stopwords' represented here are likely too coarse-grained
## ---------------------------------------------------------- ##
stopwords = [
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because', 'been', 'before',
    'between', 'both', 'but', 'by', 'can', 'did', 'do', 'does', 'doing', 'don', 'down', 'during', 'each', 'few', 'for', 'from', 'further',
    'had', 'has', 'have', 'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'itself',
    'just', 'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'now', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out',
    'over', 'own', 's', 'same', 'she', 'should', 'so', 'some', 'such', 't', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there',
    'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while',
    'who', 'whom', 'why', 'will', 'with', 'you', 'your', 'yours', 'yourself', 'yourselves'
]


class GenerateViewSpans(BaseObject):
    """ View Generator: Entity Spans for Long-Range Synonym Swapping """

    def __init__(self):
        """ Change History

        Created:
            25-Oct-2021
            craigtrim@gmail.com
            *   Automate Long Distance Matching in Multi Gram Entities
        Updated:
            27-May-2022
            craigtrim@gmail.com
            *   ported to ask-owl
                https://github.com/craigtrim/askowl/issues/5
        """
        BaseObject.__init__(self, __name__)

    @classmethod
    def _normalize(self,
                   d_results: dict) -> dict:
        """Normalize the Result of the OWL Query

        Sample Input
            'nurse_practitioner':   {   'Np':                       None,
                                        'Nps':                      None,
                                        'Nursing Practitioner':     None },
            'nursing':              {   'Nursing':                  None },
            'nursing_diploma':      {   'Nursing Diploma':          None },
            'nursing_education':    {   'Nursing Education':        None },

        Sample Output:
            {   'nurse_practitioner': [ 'Nursing Practitioner' ],
                'nursing_diploma    : []'
                'nursing_education' : []}

        Args:
            d_results (dict): [description]

        Returns:
            list: Terms to Span Over
        """
        d = {}

        def is_valid(term: str) -> bool:
            return ' ' in term or '_' in term

        keys = [k for k in d_results if is_valid(k)]
        for key in keys:

            values = [v for v in d_results[key] if is_valid(v)]
            values = [v.lower().replace(' ', '_') for v in values]
            values = [v for v in values if v != key]
            d[key] = values

        return d

    def _to_dict(self,
                 canon: str,
                 tokens: list) -> dict:

        def content() -> set:
            t = [x for x in tokens[1:] if x.lower() not in stopwords]
            return set(t)

        tokens2 = content()
        if not len(tokens2):
            return None

        # TODO: all these values have to be default only when not otherwise specified
        distance = EnvIO.int_or_default('SPAN_DISTANCE', 3)
        return {
            "content": content(),
            "distance": distance,
            "forward": True,
            "reverse": True,
            "canon": canon}

    def process(self,
                d_results: dict) -> dict:

        d = defaultdict(list)
        d_results = self._normalize(d_results)

        def update(canon: str,
                   term: str) -> None:
            tokens = term.split('_')
            trigger = tokens[0]

            d_result = self._to_dict(canon, tokens)
            if d_result:
                d[trigger].append(d_result)

        for k in d_results:
            update(canon=k, term=k)
            for v in d_results[k]:
                update(canon=k, term=v)

        return dict(d)
