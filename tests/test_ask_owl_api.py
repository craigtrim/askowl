from audioop import reverse
from askowl import __version__

import os
from pprint import pprint

from rdflib import Graph
from baseblock import Enforcer
from askowl.bp import AskOwlAPI


# Path to Test OWL files
absolute_path = os.path.normpath(os.path.join(os.getcwd(), 'resources/tests'))


class TestOntology(object):

    def __init__(self,
                 ontology_name: str):
        self.api = AskOwlAPI(
            ontology_name=ontology_name,
            absolute_path=absolute_path)
        assert self.api

    def api_state(self):
        Enforcer.is_str(self.api.ontology_name)
        Enforcer.is_str(self.api.absolute_path)

        g = self.api.graph
        assert g
        assert type(g) == Graph

    def labels(self):
        print(self.api.labels())
        Enforcer.is_optional_list(self.api.labels())
        Enforcer.is_optional_dict(self.api.by_predicate("rdfs:label"))
        Enforcer.is_optional_dict(
            self.api.by_predicate("rdfs:label", reverse=True))

    def types(self):
        Enforcer.is_list(self.api.types())

    def comments(self):
        Enforcer.is_dict(self.api.comments())

    def predicate(self):
        results = self.api.by_predicate('implies')
        Enforcer.is_optional_dict(results)

        results_rev = self.api.by_predicate('implies', reverse=True)
        Enforcer.is_optional_dict(results_rev)

    def see_also(self):
        Enforcer.is_optional_list(self.api.see_also())

    def ngrams(self):
        for i in range(6):
            Enforcer.is_optional_list(self.api.ngrams(i))

    def backward_compatible_with(self):
        Enforcer.is_optional_list(self.api.backward_compatible_with())

    def trie(self):
        Enforcer.is_optional_dict(self.api.trie())

    def synonyms(self):
        Enforcer.is_optional_dict(self.api.synonyms())
        Enforcer.is_optional_dict(self.api.synonyms_rev())

    def spans(self):
        Enforcer.is_optional_dict(self.api.spans())


def runner(ontology_name: str) -> None:
    dmo = TestOntology(ontology_name)
    dmo.api_state()
    dmo.labels()
    dmo.types()
    dmo.predicate()
    dmo.see_also()
    dmo.ngrams()
    dmo.backward_compatible_with()
    dmo.trie()
    dmo.synonyms()
    dmo.spans()


def test_normal_ontology():
    """ This is considerd a 'typical' Ontology

    and should flex out the primary functionality in a 'happy-path' manner 
    """
    runner('askowltest')


def test_sparse_ontology():
    """ Test a Sparse Ontology

    Very little information, but what does exist is accurate 
    """
    runner('sparse')


def test_empty_ontology():
    """ Test an empty Ontology 

    Ensure that the askowl microservice does not throw unhandled exceptions
    """
    runner('empty')


def test_error_ontology():
    """ Test an Ontology with Possible Errors or Mis-Configurations

    This can be entities without equivalent rdfs:label objects, for example

    Anything unexpected is placed in this OWL file
    """
    runner('error')


def main():
    test_normal_ontology()
    test_sparse_ontology()
    test_empty_ontology()
    test_error_ontology()


if __name__ == "__main__":
    main()
