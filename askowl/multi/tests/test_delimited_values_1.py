import os
from pprint import pprint


from askowl.multi.bp import FindOntologyData


absolute_path = os.path.normpath(
    os.path.join(os.getcwd(), 'resources/tests'))


def test_synonyms():
    """ Critical Test Case

    Demonstrates:
        1.  Proper Loading of external synonyms from file
            https://github.com/grafflr/deepnlu/issues/18

    Reinforces:
        1.  Proper Tokenization of rdfs:seeAlso values
            https://github.com/grafflr/ask-owl/issues/13
    """

    bp = FindOntologyData(
        ontologies=['unitest'],
        absolute_path=absolute_path)
    assert bp

    d_syn = bp.synonyms()

    actual_values = sorted(d_syn['alpha'])

    print (actual_values)

    expected_values = [
        'alpha',
        'alpha1',  # << delimited value
        'alpha2',  # << delimited value
        'alpha3',  # << delimited value
        'alpha4',
        'alpha5',
        'alpha6',
        'alpha7',  # << external value
        'alpha8',  # << external value
        'alpha9'  # << external value
    ]

    assert actual_values == expected_values


def main():
    test_synonyms()


if __name__ == "__main__":
    main()
