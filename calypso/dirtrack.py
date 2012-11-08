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

class DirTrack(object):

    def scan(self):
        self._dirs=[]
        self._files=[]
        self.mtime = os.path.getmtime(self.path)
        ents = os.listdir(self.path)
        for ent in ents:
            path=os.path.join(self.path, ent)
            if os.path.isdir(path):
                self._dirs.append(ent)
            else:
                self._files.append(ent)

    def check(self):
        if os.path.getmtime(self.path) != self.mtime:
            self.scan();
            return True
        return False

    @property
    def dirs(self):
        self.check()
        return self._dirs

    @property
    def files(self):
        self.check()
        return self._files

    def __init__(self, path):
        self.path = path
        self.scan()
