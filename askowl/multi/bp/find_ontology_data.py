# !/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Generic Facade to Find Data in 1..* Ontology Models """


from functools import lru_cache

from baseblock import Enforcer
from baseblock import BaseObject

from askowl.single.bp import AskOwlAPI
from askowl.single.dto import QueryResultType

from askowl.multi.svc import QueryNerLabel
from askowl.multi.svc import QueryNerDepth
from askowl.multi.svc import QueryNerTaxo
from askowl.multi.svc import FindNER
from askowl.multi.svc import FindSynonyms
from askowl.multi.svc import FindTypes
from askowl.multi.svc import LoadSynonyms

from askowl.multi.dmo import ViewGeneratorLookup
from askowl.multi.dmo import ModelResultMerge
from askowl.multi.dmo import NerPalleteLookup


class FindOntologyData(BaseObject):
    """ Generic Facade to Find Data in 1..* Ontology Models """

    def __init__(self,
                 ontologies: list,
                 absolute_path: str):
        """ Change Log

        Created:
            26-May-2022
            craig@graffl.ai
            *   https://github.com/grafflr/deepnlu/issues/2

        Args:
            ontologies (list): one-or-more Ontology models to use in processing
            absolute_path (str): an absolute path that applies to all the OWL models
        """
        BaseObject.__init__(self, __name__)
        if self.isEnabledForDebug:
            Enforcer.is_list(ontologies)

        self._ontologies = ontologies
        self._absolute_path = absolute_path

        self._d_ontologies = self._load(
            ontologies=ontologies,
            absolute_path=absolute_path)

        self._merge = ModelResultMerge().process

        self._query_ner_label = QueryNerLabel(self._d_ontologies).process
        self._query_ner_depth = QueryNerDepth(self._d_ontologies).process
        self._query_ner_taxo = QueryNerTaxo(self._d_ontologies).process

        self._load_synonyms = LoadSynonyms(
            d_ontologies=self._d_ontologies,
            model_result_merge=self._merge)

        self._find_synonyms = FindSynonyms(
            d_synonyms_fwd=self.synonyms(),
            d_synonyms_rev=self.synonyms_rev())

        self._find_types = FindTypes(
            d_types_fwd=self.types(),
            d_types_rev=self.types_rev())

    def ontologies(self) -> list:
        return self._ontologies

    def absolute_path(self) -> str:
        return self._absolute_path

    def _load(self,
              ontologies: list,
              absolute_path: str) -> dict:
        d = {}
        for ontology_name in ontologies:
            d[ontology_name] = AskOwlAPI(
                ontology_name=ontology_name,
                absolute_path=absolute_path)
        return d

    @staticmethod
    def _to_entity_name(input_text: str) -> str:
        input_text = input_text.lower().strip()
        if ' ' in input_text:
            input_text = input_text.replace(' ', '_')
        return input_text

    @lru_cache
    def _by_predicate(self,
                      predicate_name: str,
                      to_lowercase: bool = True) -> dict:
        results = []
        for ontology_name in self._d_ontologies:
            results.append(
                self._d_ontologies[ontology_name].by_predicate(
                    predicate=predicate_name,
                    to_lowercase=to_lowercase))

        if not results:
            return None
        elif len(results) == 1:
            return results[0]
        return self._merge(results, QueryResultType.DICT_OF_STR2LIST)

    @lru_cache
    def _by_predicate_rev(self,
                          predicate_name: str,
                          to_lowercase: bool = True) -> dict:
        results = []
        for ontology_name in self._d_ontologies:
            results.append(
                self._d_ontologies[ontology_name].by_predicate(
                    reverse=True,
                    predicate=predicate_name,
                    to_lowercase=to_lowercase))

        if not results:
            return None
        elif len(results) == 1:
            return results[0]
        return self._merge(results, QueryResultType.DICT_OF_STR2LIST)

    @lru_cache
    def comments(self) -> dict:
        results = []
        for ontology_name in self._d_ontologies:
            results.append(self._d_ontologies[ontology_name].comments())

        if not results:
            return None
        elif len(results) == 1:
            return results[0]
        return self._merge(results, QueryResultType.DICT_OF_STR2LIST)

    def effects(self) -> dict:
        """ Find Effects Relationships

        Sample:
            Given   ?a effects ?b
            Return  ?a : [?b]

        Returns:
            list or None: a list of zero-or-more entities that the incoming entity effects
        """
        return self._by_predicate('effects')

    @lru_cache
    def effects_rev(self) -> dict:
        """ Find Effected By relationships

        Sample:
            Given   ?a effected by ?b
            Return  ?b : [?a]

        Returns:
            dict: reverse of effected by function
        """
        return self._by_predicate_rev('effects')

    @lru_cache
    def requires(self) -> dict:
        """ Find Requires Relationships

        Sample:
            Given   ?a requires ?b
            Return  ?a : [?b]

        Returns:
            list or None: a list of zero-or-more entities that the incoming entity requires
        """
        return self._by_predicate('requires')

    @lru_cache
    def required_by(self) -> dict:
        """ Find Required By relationships

        Sample:
            Given   ?a requires ?b
            Return  ?b : [?a]

        Returns:
            dict: reverse of requires function
        """
        return self._by_predicate_rev('requires')

    def requires_by_entity(self,
                           input_text: str) -> list or None:
        """ Retrict Requires Relationship to a Single Entity

        Args:
            input_text (str): the entity to search for

        Returns:
            list or None: a list of zero-or-more the incoming entity requires
        """
        input_text = self._to_entity_name(input_text)
        if self.requires() and input_text in self.requires():
            return self.requires()[input_text]

    def required_by_entity(self,
                           input_text: str) -> list or None:
        """ Retrict Required-By Relationship to a Single Entity

        Args:
            input_text (str): the entity to search for

        Returns:
            list or None: a list of zero-or-more entities that the incoming entity is required by
        """
        input_text = self._to_entity_name(input_text)
        if self.required_by() and input_text in self.required_by():
            return self.required_by()[input_text]

    @lru_cache
    def similar(self) -> dict:
        """ Find Similar Relationships

        Sample:
            Given       ?a similar ?b
            Return      ?a : [?b]

        Returns:
            list or None: a list of zero-or-more entities that the incoming entity is similar to
        """
        return self._by_predicate('similarTo')

    @lru_cache
    def similar_rev(self) -> dict:
        """ Find Similar Inverse Relationships

        Sample:
            Given       ?a similar ?b
            Return      ?b : [?a]

        Returns:
            list or None: a list of zero-or-more entities that the incoming entity is similar to
       """
        return self._by_predicate_rev('similarTo')

    def similar_by_entity(self,
                          input_text: str) -> dict:
        """ Find Similarity Relationships on a per-Entity basis
        This relationship is bi-directional

        Sample:
            Given       ?a similar ?b
                        ?x similar ?a
            Return      ?a : [?b, ?x]

        Rationale:
            if      ?x is similar to ?a
            then    ?a is similar to ?x

        Args:
            input_text (str): the entity to search for

        Returns:
            list or None: a list of zero-or-more entities that the incoming entity is similar to
        """
        results = []
        input_text = self._to_entity_name(input_text)

        if self.similar() and input_text in self.similar():
            [results.append(x) for x in self.similar()[input_text]]

        if self.similar_rev() and input_text in self.similar_rev():
            [results.append(x) for x in self.similar_rev()[input_text]]

        return results

    @lru_cache
    def implies(self) -> dict:
        """ Find Implied Relationships

        Sample:
            Given       ?a implies ?b
            Return      ?a : [?b]

        Returns:
            list or None: a list of zero-or-more entities that the incoming entity implies
        """
        return self._by_predicate('implies')

    @lru_cache
    def implies_by_entity(self,
                          input_text: str) -> dict:
        """ Retrict Implies Relationship to a Single Entity

        Args:
            input_text (str): the entity to search for

        Returns:
            list or None: a list of zero-or-more entities that the incoming entity implies
        """
        input_text = self._to_entity_name(input_text)
        if self.implies() and input_text in self.implies():
            return self.implies()[input_text]

    @lru_cache
    def implied_by(self) -> dict:
        """ Find Implied By relationships

        Sample:
            Given   ?a requires ?b
            Return  ?b : [?a]

        Returns:
            list or None: a list of zero-or-more entities that are implied by this entity 
        """
        return self._by_predicate_rev('implies')

    @lru_cache
    def implied_by_entity(self,
                          input_text: str) -> dict:
        """ Retrict Implied By Relationship to a Single Entity

        Args:
            input_text (str): the entity to search for

        Returns:
            list or None: a list of zero-or-more entities that are implied by this entity 
        """
        input_text = self._to_entity_name(input_text)
        if self.implied_by() and input_text in self.implied_by():
            return self.implied_by()[input_text]

    @lru_cache(maxsize=512, typed=False)
    def is_canon(self,
                 input_text: str) -> bool:
        """Check if Input Text is Canonical Entity

        Args:
            input_text (str): any input string

        Returns:
            bool: True if the input string is a Nursing Entity
        """
        return self._find_synonyms.is_canon(input_text)

    @lru_cache(maxsize=512, typed=False)
    def find_canon(self,
                   input_text: str) -> str or None:
        """Find the Canonical Representation of the Input String

        Args:
            input_text (str): any input string

        Returns:
            str or None: The Canonical Entity
        """
        return self._find_synonyms.find_canon(input_text)

    @lru_cache(maxsize=512, typed=False)
    def is_variant(self,
                   input_text: str) -> bool:
        """Check if Input Text is known variant for at least one Canonical Entry

        Args:
            input_text (str): any input string

        Returns:
            bool: True if the input string is a known synonym to a Nursing Entity
        """
        return self._find_synonyms.is_variant(input_text)

    @lru_cache(maxsize=512, typed=False)
    def find_variants(self,
                      input_text: str) -> list or None:
        """Find the Synonyms for a known Entity

        Args:
            input_text (str): any input string

        Returns:
            list or None: a list of synonyms for the input entity
        """
        return self._find_synonyms.find_variants(input_text)

    @lru_cache(maxsize=512, typed=False)
    def find_ner(self,
                 input_text: str) -> str or None:

        svc = FindNER(
            d_ner_depth=self.ner_depth(),
            d_ner_taxo=self.ner_taxonomy(),
            d_graffl_ner=self.graffl_ner(),
            d_spacy_ner=self.spacy_ner())

        return svc.find_ner(input_text)

    @lru_cache
    def graffl_ner(self) -> dict:
        return self._query_ner_label('grafflNER')

    @lru_cache
    def graffl_ner_rev(self) -> dict:
        return self._query_ner_label('grafflNER', reverse=True)

    @lru_cache
    def spacy_ner(self) -> dict:
        return self._query_ner_label('spacyNER')

    @lru_cache
    def spacy_ner_rev(self) -> dict:
        return self._query_ner_label('spacyNER', reverse=True)

    @lru_cache
    def ner_depth(self) -> dict:
        return self._query_ner_depth(reverse=False)

    @lru_cache
    def ner_depth_rev(self) -> dict:
        return self._query_ner_depth(reverse=True)

    @lru_cache
    def infer_by_requires(self) -> dict:
        raise NotImplementedError

    @lru_cache
    def labels(self) -> dict or None:
        """Find all the Labels keyed by Entity Name

        Returns:
            dict or None: a list of entity names with label string values
        """
        # the challenge with using 'to_lowercase=False' is that both the key and value retain their original case
        d_labels = self._by_predicate('rdfs:label', to_lowercase=False)
        if not d_labels or not len(d_labels):
            return None

        d = {}
        for k in d_labels:
            d[k.lower()] = d_labels[k]

        return d

    @lru_cache
    def labels_rev(self) -> dict:
        """Find all the Entity Names keyed by Label

        Returns:
            dict or None: a list of labels with entity name values
        """
        return self._by_predicate_rev('rdfs:label')

    def label_by_entity(self,
                        input_text: str) -> str or None:
        """Find the Label for a known Entity

        Args:
            input_text (str): any input string

        Returns:
            str or None: a label for the entity (if found)
        """
        input_text = self._to_entity_name(input_text)
        if input_text not in self.labels():
            pass

        if input_text in self.labels():
            results = self.labels()[input_text]
            if results and len(results):
                return results[0]

    @lru_cache
    def ner_taxonomy(self) -> dict:
        return self._query_ner_taxo(reverse=False)

    @lru_cache
    def ner_taxonomy_rev(self) -> dict:
        return self._query_ner_taxo(reverse=True)

    @lru_cache
    def ner_pallete_lookup(self,
                           input_text: str) -> dict or None:
        d_result = self.ner_taxonomy_rev()

        if not d_result or not len(d_result):
            return None

        return NerPalleteLookup(d_result).lookup(input_text)

    @lru_cache
    def ner_pallete_colors(self) -> dict or None:
        d_result = self.ner_taxonomy_rev()

        if not d_result or not len(d_result):
            return None

        return NerPalleteLookup(d_result).colors()

    @lru_cache
    def spans(self) -> dict:
        results = []
        for ontology_name in self._d_ontologies:
            results.append(self._d_ontologies[ontology_name].spans())

        if not results:
            return None
        elif len(results) == 1:
            return results[0]

        return self._merge(results, QueryResultType.DICT_OF_STR2DICT)

    @lru_cache
    def span_keys(self) -> list:
        """ Return Span Keys sorted by Length

        Returns:
            list: list of span keys sorted by length
        """
        return sorted(self.spans().keys(), key=len)

    def synonyms(self) -> dict:
        """ Return Synonyms keyed by Entity Name

        Returns:
            dict: dictionary of entities associated to a list of zero-or-more synonyms
        """
        return self._load_synonyms.synonyms()

    def synonyms_rev(self) -> dict:
        """ Return Entities keyed by Synonyms

        Returns:
            dict: dictionary of synonyms associated to a list of one-or-more entities
        """
        return self._load_synonyms.synonyms_rev()

    @lru_cache
    def trie(self) -> dict:
        results = []
        for ontology_name in self._d_ontologies:
            results.append(self._d_ontologies[ontology_name].trie())

        if not results:
            return None
        elif len(results) == 1:
            return results[0]
        return self._merge(results, QueryResultType.DICT_OF_STR2LIST)

    @lru_cache
    def types(self) -> dict:
        return self._by_predicate('rdfs:subClassOf')

    @lru_cache
    def types_rev(self) -> dict:
        return self._by_predicate_rev('rdfs:subClassOf')

    @lru_cache
    def uses(self) -> dict:
        return self._by_predicate('uses')

    @lru_cache
    def uses_rev(self) -> dict:
        return self._by_predicate_rev('uses')

    @lru_cache
    def has_parent(self,
                   input_text: str,
                   parent: str) -> bool:
        """ Simple Truth check
            Does the incoming input entity have the incoming parent as a parent?

        Args:
            input_text (str): a candidate concept

        Returns:
            bool: True if the described relationship exists
        """
        return self._find_types.has_parent(
            parent=parent,
            input_text=input_text)

    @lru_cache
    def has_ancestor(self,
                     input_text: str,
                     parent: str) -> bool:
        """ Simple Truth check
            Does the incoming input entity have the incoming parent as an ancestor?

        Args:
            input_text (str): a candidate concept

        Returns:
            bool: True if the described relationship exists
        """
        return self._find_types.has_ancestor(
            parent=parent,
            input_text=input_text)

    @lru_cache
    def entity_exists(self,
                      input_text: str) -> bool:
        """ Simple Truth check
            Does this value exist anywhere in the Ontology?

        Args:
            input_text (str): a candidate concept

        Returns:
            bool: True if the concept exists in the Ontology
        """
        return self._find_types.exists(input_text)

    @lru_cache
    def children(self,
                 input_text: str) -> list:
        """ Return the Children for an Entity

        Args:
            input_text (str): the input entity

        Returns:
            list: the list of results (if any)
        """
        return self._find_types.children(input_text)

    @lru_cache
    def children_and_self(self,
                          input_text: str) -> list:
        """ Return the Children for an Entity, 
            and the Entity itself, in a list of results

        Args:
            input_text (str): the input entity

        Returns:
            list: the list of results (if any)
        """
        return self._find_types.children(input_text)

    @lru_cache
    def descendants(self,
                    input_text: str) -> list:
        """ Return the Descendants for an Entity

        Args:
            input_text (str): the input entity

        Returns:
            list: the list of results (if any)
        """
        return self._find_types.descendants(input_text)

    @lru_cache
    def descendants_and_self(self,
                             input_text: str) -> list:
        """ Return the Descendants for an Entity, 
            and the Entity itself, in a list of results

        Args:
            input_text (str): the input entity

        Returns:
            list: the list of results (if any)
        """
        return self._find_types.descendants_and_self(input_text)

    @lru_cache
    def parents(self,
                input_text: str) -> list:
        """ Return the Parents for an Entity

        Args:
            input_text (str): the input entity

        Returns:
            list: the list of results (if any)
        """
        return self._find_types.parents(input_text)

    @lru_cache
    def parents_and_self(self,
                         input_text: str) -> list:
        """ Return the Parents for an Entity, 
            and the Entity itself, in a list of results

        Args:
            input_text (str): the input entity

        Returns:
            list: the list of results (if any)
        """
        return self._find_types.parents_and_self(input_text)

    @lru_cache
    def ancestors(self,
                  input_text: str) -> list:
        """ Return the Ancestors for an Entity

        Args:
            input_text (str): the input entity

        Returns:
            list: the list of results (if any)
        """
        return self._find_types.ancestors(input_text)

    @lru_cache
    def ancestors_and_self(self,
                           input_text: str) -> list:
        """ Return the Ancestors for an Entity, 
            and the Entity itself, in a list of results

        Args:
            input_text (str): the input entity

        Returns:
            list: the list of results (if any)
        """
        return self._find_types.ancestors_and_self(input_text)

    @lru_cache
    def lookup(self) -> dict or None:
        """ Generate n-Gram Spans suitable for Synonym Matching

        Reference:
            https://github.com/grafflr/ask-owl/issues/4
            https://github.com/grafflr/deepnlu/issues/21#issuecomment-1141524102

        Returns:
            dict: dictionary of values keyed by n-gram size
        """
        d_synonyms_fwd = self.synonyms()

        if not d_synonyms_fwd or not len(d_synonyms_fwd):
            return None

        return ViewGeneratorLookup().process(d_synonyms_fwd)
