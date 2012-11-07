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

import os
import os.path
import posixpath
import dirtrack

class Collections(object):

    @property
    def collections(self):
        return self.collection_track.dirs

    def __init__(self, path):
        self.path = path
        self.collection_track = dirtrack.DirTrack(path)

class Owners(object):

    @property
    def owners(self):
        return self.owner_track.dirs

    def owner_path(self, owner):
        return os.path.join(self.path, owner)
        
    def scan(self):
        owners = self.owners
        for owner in self._collections:
            if not owner in owners:
                del self._collections[owner]
        for owner in owners:
            if not owner in self._collections:
                print "Adding owner %s" % owner
                self._collections[owner] = Collections(self.owner_path(owner))
        return True

    def check(self):
        if not self.owner_track.check():
            return False
        self.scan()

    def __init__(self, path):
        self.path = path
        self._collections={}
        self.owner_track = dirtrack.DirTrack(path)
        self.scan()

    def collections(self, principals):
        c=[]
        self.check()
        for owner in principals:
            if owner in self._collections:
                print "%s is a valid owner" % owner
                for collection in self._collections[owner].collections:
                    c.append((owner, collection))
        return c
