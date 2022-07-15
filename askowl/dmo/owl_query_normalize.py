#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Normalize the Extracted OWL Query Data """


from rdflib import Graph

from baseblock import BaseObject


class OwlQueryNormalize(BaseObject):
    """ Normalize the Extracted OWL Query Data """

    def __init__(self,
                 graph: Graph):
        """ Change History

        Created:
            13-Oct-2021
            craig@grafflr.ai
            *   refactored out of 'owl-data-extract'
                https://github.com/grafflr/graffl-core/issues/38
        Updated:
            25-May-2022
            craig@grafflr.ai
            *   refactor into 'ask-owl' repo
                https://github.com/grafflr/ask-owl/issues/1

        Args:
            graph (Graph): an instantiated RDF graph
        """
        BaseObject.__init__(self, __name__)
        self._graph = graph

    def process(self,
                d_results: dict,
                all_subjects: bool = True) -> dict:

        d_normalized = {}

        # Represent all Subjects
        if all_subjects:
            for subject, _, _ in self._graph:
                subject = subject.title().split('#')[-1].strip().lower()
                if subject.startswith('http'):
                    continue  # this is the root entity
                d_normalized[subject] = set()

        # Add Query Results
        for k in d_results:
            d_normalized[k] = d_results[k]

        # # Sort Values
        d_normalized = {k: d_normalized[k] for k in d_normalized
                        if len(d_normalized[k])}

        return d_normalized
