# -*- coding: utf-8 -*-
#
# This file is part of Calypso - CalDAV/CardDAV/WebDAV Server
# Copyright © 2013 Guido Günther <agx@sigxcpu.org>
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

"""
Gssapi module.

This module handles kerberos authenticatien via gssapi
"""

import os

from . import config

# pylint: disable=F0401
try:
    import kerberos as krb
except ImportError:
    krb = None
# pylint: disable=F0401

class Negotiate(object):
    _gssapi = False

    def __init__(self, log):
        self.log = log
        try:
            self.servicename = os.path.expanduser(config.get("server",
                                                             "servicename"))
        except:
            self.servicename = None

        if self.servicename and krb:
            self._gssapi = True

    def enabled(self):
        return self._gssapi

    def step(self, authorization, request):
        """
        Try to authenticate the client and if succesful authenticate
        ourselfes to the client.
        """
        user = None

        if not self.enabled():
            return (None, False)

        try:
            (neg, challenge) = authorization.split()
            if neg.lower().strip() != 'negotiate':
                return (None, False)

            self.log.debug("Negotiate header found, trying Kerberos")
            result, context = krb.authGSSServerInit(self.servicename);
            result = krb.authGSSServerStep(context, challenge);

            if result == -1:
                return (None, False)

            response = krb.authGSSServerResponse(context)
            # Client authenticated successfully, so authenticate to the client:
            request.queue_header("www-authenticate",
                                 "negotiate " + response)
            user = krb.authGSSServerUserName(context)

            self.log.debug("Negotiate: found user %s" % user)
            result = krb.authGSSServerClean(context)
            if result != 1:
                self.log.error("Failed to cleanup gss context")
            return (user, True)
        except krb.GSSError, err:
            self.log.error("gssapi error: %s", err)

        return None, False

