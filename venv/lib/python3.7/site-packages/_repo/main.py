#! /usr/bin/env python
# coding: utf-8
#
# PYTHON_ARGCOMPLETE_OK
#
# github_hg.py
#
# (C) 2013 Anthon van der Neut <a.van.der.neut@ruamel.eu>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

"""repo: handle complex repository workflow in a repeatable way"""

__version__ = '0.1.0'

import sys

def main():
    from _repo.repo import Repo
    program = Repo(auto=False)
    program.parser_setup()
    res = program.parser_parse()
    sys.exit(res)
