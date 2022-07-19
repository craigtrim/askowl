

import os


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

    def adhoc(self):
        query = """
            SELECT 
                ?label ?NER 
            WHERE 
            { 
                ?entity owl:backwardCompatibleWith ?NER
                {
                    ?child rdfs:subClassOf* ?entity
                    { ?child rdfs:label ?label }
                    UNION
                    { ?child rdfs:seeAlso ?label }
                }
                OPTIONAL
                {
                    { ?entity rdfs:label ?label }
                    UNION
                    { ?entity rdfs:seeAlso ?label }        
                }
                
                FILTER 
                ( 
                    datatype(?NER) = askowltest:grafflNER
                )
            }
        """
        from rdflib.plugins.sparql.processor import SPARQLResult

        results = self.api.adhoc(query, to_lowercase=True)
        assert type(results) == SPARQLResult


def runner(ontology_name: str) -> None:
    dmo = TestOntology(ontology_name)
    dmo.adhoc()


def test_normal_ontology():
    """ This is considerd a 'typical' Ontology

    and should flex out the primary functionality in a 'happy-path' manner 
    """
    runner('askowltest')


def main():
    test_normal_ontology()


if __name__ == "__main__":
    main()
