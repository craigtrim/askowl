
import os

from random import sample

from baseblock import Enforcer


from askowl.single.svc import LoadOntologyModel
from askowl.single.svc import QueryOntologyModel
from askowl.single.dto import QueryResultType

absolute_path = os.path.normpath(os.path.join(os.getcwd(), 'resources/tests'))

graph = LoadOntologyModel(
    ontology_name='askowltest',
    absolute_path=absolute_path).process()

svc = QueryOntologyModel(graph)
assert svc


def sample_from_dict(d, n=5):
    keys = sample(list(d), n)
    values = [d[k] for k in keys]
    return dict(zip(keys, values))


def test_LIST_OF_STRINGS():

    sparql = """
SELECT 
    ?b ?a
WHERE 
{ 
    ?a rdfs:label ?b
}
    """.strip()

    results = svc.process(sparql, QueryResultType.LIST_OF_STRINGS)
    Enforcer.is_list(results)

    print("Sample: ")
    print(sample(results, 5))


def test_DICT_OF_STR2STR():

    sparql = """
SELECT 
    ?b ?a
WHERE 
{ 
    ?a rdfs:label ?b
}
    """.strip()

    results = svc.process(sparql, QueryResultType.DICT_OF_STR2STR)
    Enforcer.is_dict(results)

    print("Sample: ")
    print(sample_from_dict(results))


def main():
    test_LIST_OF_STRINGS()
    test_DICT_OF_STR2STR()


if __name__ == "__main__":
    main()
