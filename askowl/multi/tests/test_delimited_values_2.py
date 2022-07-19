import os

from baseblock import Enforcer

from askowl.multi.bp import FindOntologyData


ONTOLOGIES = ['normal']

absolute_path = os.path.normpath(
    os.path.join(os.getcwd(), 'resources/tests'))


def test_synonyms():
    """ Critical Test Case

    Reference:
        https://github.com/grafflr/deepnlu/issues/21
        https://github.com/grafflr/deepnlu/issues/21#issuecomment-1141518333

    Purpose:
        The entity 'increase' has multiple synonyms
        -   some from the external text file
        -   others from rdfs:seeAlso
        -   per the latter, some of these are comma delimited

    Demonstrate that we can accurately match a synonym via all these sources
    """

    bp = FindOntologyData(
        ontologies=ONTOLOGIES,
        absolute_path=absolute_path)
    assert bp

    d_syn = bp.synonyms()
    Enforcer.is_dict(d_syn)

    print (d_syn['increase'])

    assert sorted(d_syn['increase']) == [
        'doubled',  # << delimited.txt
        'increase',  # actual entity name
        'increased',  # << delimited.txt
        'increases',  # << delimited.txt
        'increasing',  # << delimited.txt
        'quadrupled',  # << rdfs:seeAlso<CSV>
        'tripled'  # << rdfs:seeAlso<CSV>
    ]


def main():
    test_synonyms()


if __name__ == "__main__":
    main()
