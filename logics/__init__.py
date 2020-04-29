"""
logics is a domain-specific expressional language with a Python-styled syntax,
that can be compiled and executed in any of ViUR's runtime contexts.
"""

__author__ = "Jan Max Meyer"
__copyright__ = "Copyright 2015-2020 by Mausbrand Informationssysteme GmbH"
__version__ = "3.0.0"
__license__ = "LGPLv3"
__status__ = "Production"

from .logics import Parser, Interpreter
from . import parser, utility
