import os

from baseblock import FileIO
from baseblock import Enforcer
from baseblock import Stopwatch

from askowl.multi.bp import FindOntologyData


absolute_path = os.path.normpath(
    os.path.join(os.getcwd(), 'resources/tests'))
FileIO.exists_or_error(absolute_path)


class TestFindOntologyData(object):

    def __init__(self,
                 ontology_name: str):
        self.bp = FindOntologyData(
            ontologies=[ontology_name],
            absolute_path=absolute_path)
        assert self.bp

    def find_comments(self):
        Enforcer.is_optional_dict(self.bp.comments())

    def find_labels(self):
        Enforcer.is_optional_dict(self.bp.labels())
        Enforcer.is_optional_dict(self.bp.labels_rev())

    def find_types(self):
        Enforcer.is_optional_dict(self.bp.types())
        Enforcer.is_optional_dict(self.bp.types_rev())

        Enforcer.is_bool(self.bp.has_parent('alpha', 'beta'))
        Enforcer.is_bool(self.bp.has_ancestor('alpha', 'beta'))

        Enforcer.is_bool(self.bp.entity_exists('nowayjoseicantexist'))

        Enforcer.is_optional_list(self.bp.children('test_entity_1'))

        Enforcer.is_optional_list(self.bp.descendants('test_entity_1'))
        Enforcer.is_optional_list(
            self.bp.descendants_and_self('test_entity_1'))

        Enforcer.is_optional_list(self.bp.parents('test_entity_1'))
        Enforcer.is_optional_list(self.bp.parents_and_self('test_entity_1'))

        Enforcer.is_optional_list(self.bp.ancestors('test_entity_1'))
        Enforcer.is_optional_list(self.bp.ancestors_and_self('test_entity_1'))

    def find_uses(self):
        Enforcer.is_optional_dict(self.bp.uses())
        Enforcer.is_optional_dict(self.bp.uses_rev())

    def find_effects(self):
        Enforcer.is_optional_dict(self.bp.effects())
        Enforcer.is_optional_dict(self.bp.effects_rev())

    def lookup(self):
        Enforcer.is_optional_dict(self.bp.lookup())

    def synonyms(self):
        Enforcer.is_optional_dict(self.bp.synonyms())
        Enforcer.is_optional_dict(self.bp.synonyms_rev())

    def spans(self):
        Enforcer.is_optional_dict(self.bp.spans())

    def trie(self):
        Enforcer.is_optional_dict(self.bp.trie())

    def graffl_ner(self):
        Enforcer.is_optional_dict(self.bp.graffl_ner())
        Enforcer.is_optional_dict(self.bp.graffl_ner_rev())

    def spacy_ner(self):
        Enforcer.is_optional_dict(self.bp.spacy_ner())
        Enforcer.is_optional_dict(self.bp.spacy_ner_rev())

    def ner_depth(self):
        Enforcer.is_optional_dict(self.bp.ner_depth())
        Enforcer.is_optional_dict(self.bp.ner_depth_rev())

    def ner_taxonomy(self):
        Enforcer.is_optional_dict(self.bp.ner_taxonomy())
        Enforcer.is_optional_dict(self.bp.ner_taxonomy_rev())

    def ner_pallete_lookup(self):
        Enforcer.is_optional_str(self.bp.ner_pallete_lookup('EVENT'))

    def find_ner(self):
        Enforcer.is_optional_str(self.bp.find_ner('staff'))

    def find_synonyms(self):
        Enforcer.is_optional_str(self.bp.find_canon('set to close'))
        Enforcer.is_optional_list(self.bp.find_variants('closure'))
        Enforcer.is_bool(self.bp.is_canon('closure'))
        Enforcer.is_bool(self.bp.is_variant('set to close'))


def runner(ontology_name: str) -> None:
    bp = TestFindOntologyData(ontology_name)
    bp.find_labels()
    bp.lookup()
    bp.find_comments()
    bp.find_types()
    bp.find_uses()
    bp.find_effects()
    bp.synonyms()
    bp.spans()
    bp.trie()
    bp.graffl_ner()
    bp.spacy_ner()
    bp.ner_depth()
    bp.ner_taxonomy()
    bp.ner_pallete_lookup()
    bp.find_ner()
    bp.find_synonyms()


def test_normal_ontology():
    """ This is considerd a 'typical' Ontology

    and should flex out the primary functionality in a 'happy-path' manner 
    """
    runner('normal')


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
