# -*- coding: utf-8 -*-
# ***************************************************************************
# *   Copyright (c) 2021 sliptonic <shopinthewoods@gmail.com>               *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

import FreeCAD
import PathFeedRate
import PathMachineState
import Path
import PathScripts.PathToolController as PathToolController

from PathTests.PathTestUtils import PathTestBase


class TestPathHelpers(PathTestBase):
    def setUp(self):
        self.doc = FreeCAD.newDocument("TestPathUtils")

        c1 = Path.Command("G0 Z10")
        c2 = Path.Command("G0 X20 Y10")
        c3 = Path.Command("G1 X20 Y10 Z5")
        c4 = Path.Command("G1 X20 Y20")

        self.commandlist = [c1, c2, c3, c4]

    def tearDown(self):
        FreeCAD.closeDocument("TestPathUtils")

    def test00(self):
        """Test that FeedRate Helper populates horiz and vert feed rate based on TC"""
        t = Path.Tool("test", "5.0")
        tc = PathToolController.Create("TC0", t)
        tc.VertRapid = 5
        tc.HorizRapid = 10
        tc.VertFeed = 15
        tc.HorizFeed = 20

        resultlist = PathFeedRate.setFeedRate(self.commandlist, tc)
        print(resultlist)

        self.assertTrue(resultlist[0].Parameters["F"] == 5)
        self.assertTrue(resultlist[1].Parameters["F"] == 10)
        self.assertTrue(resultlist[2].Parameters["F"] == 15)
        self.assertTrue(resultlist[3].Parameters["F"] == 20)

    def test01(self):
        """Test that Machine State initializes and stores position correctly"""

        machine = PathMachineState.MachineState()
        state = machine.getState()
        self.assertTrue(state['X'] == 0 )
        self.assertTrue(state['Y'] == 0 )
        self.assertTrue(state['Z'] == 0 )
        self.assertTrue(machine.WCS == "G54")

        for c in self.commandlist:
            result = machine.addCommand(c)

        state = machine.getState()
        self.assertTrue(state['X'] == 20 )
        self.assertTrue(state['Y'] == 20 )
        self.assertTrue(state['Z'] == 5 )

        machine.addCommand(Path.Command("M3 S200"))
        self.assertTrue(machine.S == 200)
        self.assertTrue(machine.Spindle == "CW")

        machine.addCommand(Path.Command("M4 S200"))
        self.assertTrue(machine.Spindle == "CCW")

        machine.addCommand(Path.Command("M2"))
        self.assertTrue(machine.Spindle == "off")
        self.assertTrue(machine.S == 0)

        machine.addCommand(Path.Command("G57"))
        self.assertTrue(machine.WCS == "G57")

        machine.addCommand(Path.Command("M6 T5"))
        self.assertTrue(machine.T == 5)

        # Test that non-change commands return false
        result = machine.addCommand(Path.Command("G0 X20"))
        self.assertFalse(result)

        result = machine.addCommand(Path.Command("G0 X30"))
        self.assertTrue(result)

        # Test that Drilling moves are handled correctly
        result = machine.addCommand(Path.Command("G81 X50 Y50 Z0"))
        state = machine.getState()
        self.assertTrue(state['X'] == 50 )
        self.assertTrue(state['Y'] == 50 )
        self.assertTrue(state['Z'] == 5 )

