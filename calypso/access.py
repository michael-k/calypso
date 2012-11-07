# -*- coding: utf-8 -*-
#
# This file is part of Calypso - CalDAV/CardDAV/WebDAV Server
# Copyright © 2012 Keith Packard
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

class Access(object):

    read_access = 1
    write_access = 2

    @classmethod
    def rights(self, string):
        r = 0
        if "r" in string:
            r |= Access.read_access
        if "w" in string:
            r |= Access.write_access
        return r
    
    def __init__(self, owner, collection):
        self.owner = owner
        self.collection = collection
        self.rights = {}

    # Add rights
    def add(self, principal, rights):
        if principal in self.rights:
            rights |= self.rights[principal]
        self.rights[principal] = rights

    # Delete rights
    def delete(self, principal, rights):
        if principal in self.rights:
            new_rights = self.rights[principal] & ~rights
            if new_rights == 0:
                self.remove(principal)
            else:
                self.rights[principal] = new_rights
            
    # Merge another set of access rights in
    def merge(self, access):
        for principal in access.rights:
            self.add(principal, access.rights[principal])

    def unmerge(self, access):
        for principal in access.rights:
            self.delete(principal, access.rights[principal])

    # Remove a principal entirely
    def remove(self, principal):
        del self.access[principal]

    def check(self, principal, rights):
        if principal in self.rights:
            return (self.rights[principal] & rights) == rights
        return False

class AccessList(object):

    def add_access(self, access):
        if access.collection in self.accesses:
            self.accesses[access.collection].merge(access)
        else:
            self.accesses[access.collection] = access

    def add(self, owner, collection, principal, rights):
        if not (owner, collection) in self.accesses:
            self.accesses[(owner,collection)] = Access(owner, collection)
        self.accesses[(owner,collection)].add (principal, rights)

    
    #
    # owner:collection:rights:principal,...
    #
    def add_string(self, string):
        string = string.strip()
        if string.startswith("#"):
            return
        elements = string.split(":")
        if len(elements) < 4:
            return
        owner = elements[0]
        collection = elements[1]
        rights = Access.rights(elements[2])
        principals = elements[3].split(",")
        print "access %s %s %d %s" % (owner, collection, rights, principals)
        for principal in principals:
            self.add(owner, collection, principal, rights)

    def set_file(self, filename):
        self.accesses = {}
        self.filename = filename
        if not filename:
            return
        try:
            f = open(filename, "r")
            self.filename = filename
            self.mtime = os.path.getmtime(filename)
            for line in f:
                self.add_string(line)
            f.close()
        except IOError:
            return

    def check_file(self):
        if not self.filename:
            return
        if os.path.getmtime(self.filename) != self.mtime:
            self.set_file(self.filename)

    def check(self, owner, collection, principals, rights):
        if owner in principals:
            return True
        self.check_file()
        if not collection in self.accesses:
            return False
        access = self.accesses[collection]
        for principal in principals:
            if access.check(principal, rights):
                return True
        return False

    def collections(self, principals, rights):
        c = []
        for (owner,collection) in self.accesses:
            if self.check(owner, collection, principals, rights):
                c.append((owner, collection))
        return c

    def __init__(self, filename=None):
        self.set_file(filename)
