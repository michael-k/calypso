# -*- coding: utf-8 -*-
#
# This file is part of Calypso - CalDAV/CardDAV/WebDAV Server
# Copyright © 2011 Keith Packard
# Copyright © 2008-2011 Guillaume Ayoub
# Copyright © 2008 Nicolas Kandel
# Copyright © 2008 Pascal Halter
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Calypso.  If not, see <http://www.gnu.org/licenses/>.

import urllib
import os
import os.path
import posixpath
import logging

from . import config

log = logging.getLogger()

#
# Various URL manipulation routines
#

# The first element of the URL is always the object owner

def url_to_owner(path):
    return path.strip("/").split("/")[0]

#
# Given a URL, convert it to an absolute path name by
# prepending the storage folder name
#

def url_to_file(url):
    folder = os.path.expanduser(config.get("storage", "folder"))
    tail = urllib.url2pathname(url.strip("/"))
    file = os.path.join(folder, tail)
    return file

#
# Does the provided URL reference a collection? This
# is done by seeing if the resulting path is a directory
#

def is_collection(url):
    path = os.path.join (url_to_file(url), ".git")
    return os.path.isdir(path)

#
# Given a URL, return the parent URL by stripping off
# the last path element
#

def parent_url(path):
    path_parts = path.strip("/").split("/")
    path_parent = path_parts[0:len(path_parts)-1]
    new_path = "/" + "/".join(path_parent)
    return new_path

#
# If the given URL references a resource, then
# return the name of that resource. Otherwise,
# return None
#

log = logging.getLogger()

def resource_from_path(path):
    """Return Calypso item name from ``path``."""
    if is_collection(path):
        name = None
    else:
        name = urllib.unquote(path.strip("/").split("/")[-1])
    log.debug('Path %s results in name: %s', path, name)
    return name

#
# Return the collection name for the given URL. That's
# just the URL if it refers to a collection itself, otherwise
# it's the parent of the provided URL
#

def collection_from_path(path):
    """Returns Calypso collection name from ``path``."""

    collection = path
    if not is_collection(collection):
        collection = parent_url(collection)
        if not is_collection(collection):
            return None

    # unquote, strip off any trailing slash, then clean up /../ and // entries
    collection = "/" + urllib.unquote(collection).strip("/")

    log.debug('Path %s results in collection: %s', path, collection)
    return collection
    
class UrlPath(object):

    def __init__(self, path):
        parts = urllib.unquote(path.strip("/")).split("/", 2)

        self.principal = None
        self.collection = None
        self.resource = None
        if len(parts) > 0:
            self.principal = parts[0]
            if len(parts) > 1:
                self.collection = parts[1]
                if len(parts) > 2:
                    self.resource = parts[2]
        print "UrlPath %s %s %s" % (self.principal, self.collection, self.resource)

    def dir(self):
        e=[]
        if self.principal:
            e.append(self.principal)
        if self.collection:
            e.append(self.collection)
        return url_to_file("/".join(e))

    def __str(self):
        e=[]
        if self.principal:
            e.append(self.principal)
        if self.collection:
            e.append(self.collection)
        if self.resource:
            e.append(self.resource)
        return urllib.quote("/".join(e))

    
