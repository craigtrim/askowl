import os

from baseblock import Enforcer
from askowl.single.bp import AskOwlAPI


# Path to Test OWL files
absolute_path = os.path.normpath(os.path.join(os.getcwd(), 'resources/tests'))


class TestOntology(object):

    def __init__(self,
                 ontology_name: str):
        self.api = AskOwlAPI(
            ontology_name=ontology_name,
            absolute_path=absolute_path)
        assert self.api

    def by_subject_predicate(self):
        results = self.api.by_subject_predicate(
            subject='Master_of_Science_in_Nursing',
            predicate='implies')

        print(results)
        Enforcer.is_list(results)


def runner(ontology_name: str) -> None:
    dmo = TestOntology(ontology_name)
    dmo.by_subject_predicate()


def test_normal_ontology():
    """ This is considerd a 'typical' Ontology

    and should flex out the primary functionality in a 'happy-path' manner 
    """
    runner('askowltest')


def main():
    test_normal_ontology()


if __name__ == "__main__":
    main()
