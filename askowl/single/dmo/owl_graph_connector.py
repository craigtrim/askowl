#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Connect to an RDF Graph (Ontology) """


import os

from rdflib import Graph
from rdflib import Namespace

from baseblock import FileIO
from baseblock import BaseObject


class OwlGraphConnector(BaseObject):
    """ Connect to an RDF Graph (Ontology) """

    def __init__(self,
                 prefix: str,
                 namespace: str,
                 ontology_name: str,
                 absolute_path: str):
        """ Change Log

        Created:
            6-Oct-2021
            craigtrim@gmail.com
            *   Create Owl2PY Util Service
        Updated:
            25-May-2022
            craigtrim@gmail.com
            *   refactor into 'ask-owl' repo
                https://github.com/craigtrim/askowl/issues/1

        Args:
            prefix (str): the query prefix
            namespace (str): the ontology namespace
            ontology_name (str): the ontology name (phsyical file name)
            absolute_path (str): the absolute path to the OWL model
        """
        BaseObject.__init__(self, __name__)

        self._format = "ttl"
        self._prefix = prefix
        self._namespace = namespace
        self._ontology_name = ontology_name
        self._absolute_path = absolute_path

        self._graph = self._process()

        if self.isEnabledForDebug:
            self.logger.debug('\n'.join([
                f"Loading Ontology",
                f"\tNamespace: {self._namespace}",
                f"\tName: {self._ontology_name}",
                f"\tPrefix: {self._prefix}",
                f"\tFormat: {self._format}",
                f"\tAbsolute Path: {self._absolute_path}"]))

    def _process(self) -> Graph:
        """ Load the OWL Model from disk as an RDF Graph

        Returns:
            Graph: an instantiated and in-memory RDF Graph
        """
        g = Graph()

        input_path = os.path.normpath(
            os.path.join(
                self._absolute_path,
                self._ontology_name))

        FileIO.exists_or_error(input_path)

        g.parse(input_path,
                format=self._format)

        g.bind(self._prefix,
               Namespace(self._namespace))

        return g

    def graph(self) -> Graph:
        return self._graph
