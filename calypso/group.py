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

class Group(object):

    def __init__(self, group):
        self.group = group
        self.members = {}

    # Add a principal to a group
    def add(self, principal):
        self.members[principal] = True

    def is_member(self, principal):
        return principal in self.members

class GroupList(object):

    def add(self, group, principal):
        if not group in self.groups:
            self.groups[group] = Group(group)
        self.groups[group].add(principal)

    # group:principal,...

    def add_string(self, string):
        string = string.strip()
        if string.startswith("#"):
            return
        elements = string.split(":")
        if len(elements) < 2:
            return
        group = elements[0]
        principals = elements[1].split(",")
        for principal in principals:
            self.add(group, principal)
        
    def set_file(self, filename):
        self.groups = {}
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

    def __expand(self,principal):
        principals=[principal]
        for group in self.groups:
            g = self.groups[group]
            if g.is_member(principal):
                principals.extend(self.expand(group))
        return principals

    def expand(self, principal):
        self.check_file()
        return self.__expand(principal)
        
    def __init__(self, filename=None):
        self.set_file(filename)
