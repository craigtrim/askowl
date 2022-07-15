#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from enum import Enum


class QueryResultType(Enum):

    DO_NOT_TRANSFORM = 0

    LIST_OF_STRINGS = 10

    DICT_OF_STR2STR = 20
    DICT_OF_STR2LIST = 21
    DICT_OF_STR2DICT = 22
