#!/usr/bin/python

"""
run_leveleditor.py - Used to run game level editor
"""

import sys, os
mainpath = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(mainpath)
sys.path.append(os.path.join(mainpath,"src"))
import level_editor
level_editor.main(mainpath)
