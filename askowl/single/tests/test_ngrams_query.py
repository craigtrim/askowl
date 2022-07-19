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

    def ngrams(self):

        # ngram pattern: "Alpha"
        unigrams = self.api.ngrams(1)
        Enforcer.is_optional_list(unigrams)
        assert sum([x.count('_') for x in unigrams]) == 0

        # ngram pattern: "Alpha_Beta"
        bigrams = self.api.ngrams(2)
        Enforcer.is_list(bigrams)
        assert sum([x.count('_') for x in bigrams]) == len(bigrams)

        # ngram pattern: "Alpha_Beta_Gamma"
        trigrams = self.api.ngrams(3)
        Enforcer.is_list(trigrams)
        assert sum([x.count('_') for x in trigrams]) == len(trigrams) * 2


def runner(ontology_name: str) -> None:
    dmo = TestOntology(ontology_name)
    dmo.ngrams()


def test_normal_ontology():
    """ This is considerd a 'typical' Ontology

    and should flex out the primary functionality in a 'happy-path' manner 
    """
    runner('askowltest')


def main():
    test_normal_ontology()


if __name__ == "__main__":
    main()
