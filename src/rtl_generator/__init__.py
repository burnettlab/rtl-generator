#!/usr/bin/env python3
f''' 
RTL Generator/Parameterizer

Written by Brandon Hippe (bhippe@pdx.edu)
'''

from .arguments import add_args
from .generator import rtl_generator, replace_includes
from .format import format_rtl

__all__ = ['rtl_generator', 'add_args', 'replace_includes', 'format_rtl']