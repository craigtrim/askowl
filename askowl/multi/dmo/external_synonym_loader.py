#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Load a Supplementary External File of Synonyms """


import logging

from baseblock import FileIO
from baseblock import Stopwatch
from baseblock import BaseObject


class ExternalSynonymLoader(BaseObject):
    """ Load a Supplementary External File of Synonyms """

    def __init__(self,
                 synonym_file_path: str):
        """ Change Log

        Created:
            8-Oct-2021
            craig@graffl.ai
            *   https://github.com/grafflr/graffl-core/issues/13#issuecomment-939103068
        Updated:
            29-May-2022
            craig@graffl.ai
            *   migrated out of graffl-core in pursuit of 
                https://github.com/grafflr/deepnlu/issues/18

        Args:
            synonym_file_path (str): absolute (and verified) path to the external synonyms file
        """
        BaseObject.__init__(self, __name__)
        self._synonym_file_path = synonym_file_path

    def _process(self) -> dict:
        d_file = {}

        def is_valid(line: str) -> bool:
            if not len(line):
                return False
            if line.startswith('#'):
                return False
            if '~' not in line:
                return False
            return True

        lines = FileIO.read_lines(self._synonym_file_path)
        lines = [x.strip() for x in lines if x]
        lines = [x for x in lines if is_valid(x)]

        for line in lines:
            tokens = line.lower().split('~')
            canon = tokens[0]

            variants = tokens[-1].split(',')
            variants = [x.strip() for x in variants if x]
            variants = sorted(set([x for x in variants if len(x)]), key=len)
            variants.reverse()

            d_file[canon] = variants

        return d_file

    def process(self) -> dict:
        sw = Stopwatch()

        d_file = self._process()

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug('\n'.join([
                "Loaded External File",
                f"\tFile Path: {self._synonym_file_path}",
                f"\tTotal Size: {len(d_file)}",
                f"\tTotal Time: {str(sw)}"]))

        return d_file
