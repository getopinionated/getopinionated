#!/usr/bin/env python

from os.path import realpath, dirname, join

def abspath(relativepath):
    """ Returns the path as an absolute path, assuming the relativepath parameter starts from siteroot """
    return join(dirname(realpath(__file__)), relativepath)
