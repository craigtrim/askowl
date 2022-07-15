

import os


from baseblock import FileIO
from baseblock import Enforcer
from askowl.bp import AskOwlAPI


# Path to Test OWL files
absolute_path = os.path.normpath(os.path.join(os.getcwd(), 'resources/tests'))
FileIO.exists_or_error(absolute_path)


class TestOntology(object):

    def __init__(self,
                 ontology_name: str):
        self.api = AskOwlAPI(
            ontology_name=ontology_name,
            absolute_path=absolute_path)
        assert self.api

    def synonyms(self):

        d_fwd = self.api.synonyms()
        Enforcer.is_dict(d_fwd)

        # Test that rdfs:seeAlso is properly delimited
        assert 'seealsotestcase' in d_fwd

        # NOTE: this is an important test case
        #       if it breaks, please fix it
        #       we need to prove "rdfs:seeAlso a,b,c" is properly tokenzied
        actual_results = sorted(d_fwd['seealsotestcase'])

        assert actual_results == [
            'seealso1',
            'seealso2',
            'seealso3',
            'seealso4',
            'seealso5',
            'seealsotestcase'
        ]

        Enforcer.is_dict(self.api.synonyms_rev())


def test_runner():
    """ Required for PyTest """
    TestOntology('askowltest').synonyms()


def main():
    test_runner()


if __name__ == "__main__":
    main()
