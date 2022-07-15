import os
from rdflib import Graph


from askowl.dmo import OwlGraphConnector


def test_component():
    absolute_path = os.path.normpath(os.path.join(os.getcwd(), 'resources/tests'))

    dmo = OwlGraphConnector(prefix='askowltest',
                            namespace='http://graffl.ai/askowltest#',
                            ontology_name='askowltest.owl',
                            absolute_path=absolute_path)
    assert dmo

    g = dmo.graph()
    assert g
    assert type(g) == Graph


def main():
    test_component()


if __name__ == "__main__":
    main()
