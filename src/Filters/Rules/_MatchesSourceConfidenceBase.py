#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011  Jerome Rapinat
# Copyright (C) 2011  Douglas S. Blank
# Copyright (C) 2011  Benny Malengier
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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from Filters.Rules._Rule import Rule

#-------------------------------------------------------------------------
# "Confidence level"
# Sources of an attribute of an event are ignored
#-------------------------------------------------------------------------
class MatchesSourceConfidenceBase(Rule):
    """Objects with a specific confidence level on 'direct' Source references"""

    labels    = [_('Confidence level:')]
    name        = _('Object with at least one direct source >= <confidence level>')
    description = _("Matches objects with at least one direct source with confidence level(s)")
    category    = _('General filters')
    
    def apply(self, db, obj):
        for source in obj.get_source_references():
            required_conf = int(self.list[0])
            if required_conf <= source.get_confidence_level():
                return True
        return False