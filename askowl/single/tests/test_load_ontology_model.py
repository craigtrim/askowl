import os
from rdflib import Graph


from askowl.single.svc import LoadOntologyModel


absolute_path = os.path.normpath(os.path.join(os.getcwd(), 'resources/tests'))


def test_service():
    
    svc = LoadOntologyModel(
        ontology_name='askowltest',
        absolute_path=absolute_path)
    
    assert svc

    g = svc.process()
    assert g
    assert type(g) == Graph


def main():
    test_service()


if __name__ == "__main__":
    main()
