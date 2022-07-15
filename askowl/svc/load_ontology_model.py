#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Load the Ontology Model into Memory """


from rdflib import Graph
from baseblock import BaseObject


from askowl.dmo import OwlGraphConnector


class LoadOntologyModel(BaseObject):
    """ Load the Ontology Model into Memory """

    def __init__(self,
                 ontology_name: str,
                 absolute_path: str,
                 prefix: str = None,
                 namespace: str = None):
        """ Change History

        Created:
            25-May-2022
            craigtrim@gmail.com
            *   https://github.com/craigtrim/askowl/issues/1
        Updated:
            6-Jun-2022
            craigtrim@gmail.com
            *   refactored in pursuit of
                https://github.com/craigtrim/askowl/issues/2

        Args:
            ontology_name (str): the name of the Ontology
                used to infer the file path
            prefix (str, optional): the prefix. Defaults to None.
                assumed to the ontology_name unless specified otherwise
            namespace (str, optional): the model namespace. Defaults to None.
                assumed to be "http://graffl.ai/<ontology_name>" unless specified otherwise
            absolute_path (str): the absolute path to the OWL model
        """
        BaseObject.__init__(self, __name__)

        self._absolute_path = absolute_path
        self.ontology_name = self._get_ontology_name(ontology_name)
        self.prefix = self._get_prefix(prefix, ontology_name)
        self.namespace = self._get_namespace(namespace, ontology_name)

        if self.isEnabledForDebug:
            self.logger.debug('\n'.join([
                "Intialized Loader",
                f"\tPrefix: {self.prefix}",
                f"\tOntology Name: {self.ontology_name}",
                f"\tNamespace: {self.namespace}"]))

    @staticmethod
    def _get_ontology_name(ontology_name: str) -> str:
        if not ontology_name.endswith('.owl'):
            return f"{ontology_name}.owl"
        return ontology_name

    @staticmethod
    def _get_prefix(prefix: str,
                    ontology_name: str) -> str:
        if not prefix:
            prefix = ontology_name
            if prefix.endswith('.owl'):
                prefix = prefix.split('.owl')[0].strip()
        return prefix

    @staticmethod
    def _get_namespace(namespace: str,
                       ontology_name: str) -> str:
        if not namespace:
            namespace = f"http://graffl.ai/{ontology_name}#"
        return namespace

    def process(self) -> Graph:

        dmo = OwlGraphConnector(
            prefix=self.prefix,
            namespace=self.namespace,
            ontology_name=self.ontology_name,
            absolute_path=self._absolute_path)

        return dmo.graph()
