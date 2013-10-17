#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
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

# test/GrampsLogger/ErrorReportAssistant_Test.py
# $Id$

import unittest
import logging
import sys
import os

log = logging.getLogger('Gramps.Tests.GrampsLogger')
import const
const.rootDir = os.path.join(os.path.dirname(__file__), '../../src')
sys.path.append(os.path.join(const.rootDir, 'test'))
try:
    from guitest.gtktest import GtkTestCase
    TestCaseBase = GtkTestCase
    log.info("Using guitest")
except:
    TestCaseBase = unittest.TestCase

sys.path.append(const.rootDir)
sys.path.append(os.path.join(const.rootDir, 'GrampsLogger'))

from GrampsLogger import RotateHandler

import _ErrorReportAssistant

class ErrorReportAssistantTest(TestCaseBase):
    """Test the ErrorReportAssistant."""

    def test_buffer_recall(self):
        """Test that simple recall of messages works."""

        rh = RotateHandler(10)
        l = logging.getLogger("ErrorReportAssistantTest")
        l.setLevel(logging.DEBUG)

        l.addHandler(rh)
        l.info("info message")

        error_detail="Test error"
        ass = _ErrorReportAssistant.ErrorReportAssistant(error_detail=error_detail,
                                                               rotate_handler=rh)

        assert ass._error_detail == error_detail

        l.removeHandler(rh)

def testSuite():
    suite = unittest.makeSuite(ErrorReportAssistantTest,'test')
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner().run(testSuite())
