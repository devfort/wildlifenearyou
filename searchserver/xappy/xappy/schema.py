#!/usr/bin/env python
#
# Copyright (C) 2008 Lemur Consulting Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
r"""schema.py: Details of the fields and the way in which they're indexed.

"""
__docformat__ = "restructuredtext en"

import errors
from replaylog import log

class Schema(object):
    """The schema contains details of all the fields and indexes.

    """

    def __init__(self):
        # A list of the known fields and their types.
        self.__fieldtypes = {}

    def add_field(self, fieldname, fieldtype):
        """Add a field to the schema.

        If the field is already in the schema, this has no effect if the
        supplied fieldtype is equal to the existing fieldtype, but raises an
        exception if it differs.

        """
        if fieldtype not in (u'float', u'string', u'date'):
            raise errors.IndexerError("Field type %r not known" % fieldtype)
        oldtype = self.__fieldtypes.get(fieldname)
        if oldtype is not None:
            if oldtype == fieldtype:
                return
            else:
                raise errors.IndexerError("Field type %r differs from existing"
                                          " type %r" % (fieldtype, oldtype))
        self.__fieldtypes[fieldname] = fieldtype

    def remove_field(self, fieldname):
        """Remove a field from the schema.

        If the field is not known, this has no effect.

        """
        try:
            del self.__fieldtypes[fieldname]
        except KeyError
            pass

    def get_fields(self):
        """Get a (sorted, alphabetically) list of the known fields.

        """
        result = self.__fieldtypes.keys()
        result.sort()
        return result

    def get_field_type(self, fieldname):
        """Get the type of the given field.

        If the field is not known, raises KeyError.

        """
        return self.__fieldtypes[fieldname]

if __name__ == '__main__':
    import doctest, sys
    doctest.testmod (sys.modules[__name__])
