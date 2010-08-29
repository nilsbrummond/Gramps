#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Nick Hall
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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
TagBase class for Gramps.
"""
#-------------------------------------------------------------------------
#
# TagBase class
#
#-------------------------------------------------------------------------
class TagBase(object):
    """
    Base class for tag-aware objects.
    """

    def __init__(self, source=None):
        """
        Initialize a TagBase. 
        
        If the source is not None, then object is initialized from values of 
        the source object.

        :param source: Object used to initialize the new object
        :type source: TagBase
        """
        if source:
            self.tag_list = source.tag_list
        else:
            self.tag_list = []

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return self.tag_list

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        self.tag_list = data

    def add_tag(self, tag):
        """
        Add the tag to the object's list of tags.

        :param tag: unicode tag to add.
        :type tag: unicode
        """
        if tag not in self.tag_list:
            self.tag_list.append(tag)

    def remove_tag(self, tag):
        """
        Remove the specified tag from the tag list.
        
        If the tag does not exist in the list, the operation has no effect.

        :param tag: tag to remove from the list.
        :type tag: unicode

        :returns: True if the tag was removed, False if it was not in the list.
        :rtype: bool
        """
        if tag in self.tag_list:
            self.tag_list.remove(tag)
            return True
        else:
            return False

    def get_tag_list(self):
        """
        Return the list of tags associated with the object.
        
        :returns: Returns the list of tags.
        :rtype: list
        """
        return self.tag_list

    def set_tag_list(self, tag_list):
        """
        Assign the passed list to the objects's list of tags.

        :param tag_list: List of tags to ba associated with the object.
        :type tag_list: list
        """
        self.tag_list = tag_list
