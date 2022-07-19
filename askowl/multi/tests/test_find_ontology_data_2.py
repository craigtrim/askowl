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

    def requires_by_entity(self):
        assert self.bp.requires_by_entity('alpha') == ['beta']
        assert self.bp.requires_by_entity('beta') == ['gamma']
        assert self.bp.requires_by_entity('gamma') == ['delta']

    def required_by_entity(self):
        assert self.bp.required_by_entity('beta') == ['alpha']
        assert self.bp.required_by_entity('gamma') == ['beta']
        assert self.bp.required_by_entity('delta') == ['gamma']

    def similar(self):
        assert sorted(self.bp.similar_by_entity('alpha')) == ['eta', 'theta']

    def implies_by_entity(self):
        assert self.bp.implies_by_entity('epsilon') == ['beta']

    def implied_by_entity(self):
        assert self.bp.implied_by_entity('eta') == ['digamma']

    def label_by_entity(self):
        assert self.bp.label_by_entity('eta') == "Eta"


def runner(ontology_name: str) -> None:
    bp = TestFindOntologyData(ontology_name)
    bp.requires_by_entity()
    bp.required_by_entity()
    bp.similar()
    bp.implies_by_entity()
    bp.implied_by_entity()
    bp.label_by_entity()


def test_normal_ontology():
    """ This is considerd a 'typical' Ontology

    and should flex out the primary functionality in a 'happy-path' manner
    """
    runner('normal')


def main():
    test_normal_ontology()


if __name__ == "__main__":
    main()
