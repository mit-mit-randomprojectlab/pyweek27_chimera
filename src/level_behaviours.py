#!/usr/bin/python

"""
level_behaviours.py: classes for scripts to control level entities including 
guard scripted routines
"""

import os
import pygame
from pygame.locals import *
from gamedirector import *
from math import *
import random

# You can import this here to get global access to static game resources, including
# level data
import resources

class Level_Behaviours(object):
	def __init__(self,parent):
		self.parent = parent
		# only add things here that depend on static data
	
	# on_levelstart: gets called when level is first loaded
	def on_levelstart(self,level_id):
		pass
		# examples:
		# You can access static level data loaded in from json
		# resources.levels[level_id].data['tilemap']['layer_b'] etc.
		# don't edit static data in resources, what you want for the actual game running is in tilemap:
		#
		# you can access the tilemap via:
		# t = self.parent.tiledlayers
		#
		# for example occupancy map is: self.parent.tiledlayers.occlayer
		#
		# I will provide a bit more documentation for stuff in the tilemap you can do when implemented
		# For now:
		# t.UpdateTileLayer(tile, layer, tileval) # layer: 1: mid, 2: fore: change value in displayed tiles
		#
	
	def on_update(self):
		pass
		# this method gets called every game frame (don't make it do super slow stuff :) )
		# you can access the tilemap in the same way as in "on_startlevel"

