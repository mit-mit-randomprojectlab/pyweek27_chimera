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
		self.level_init = {}
		self.level_update = {}
		# Set Functions for Each Level ...
		self.level_init['testbig003'] = self.testbig003_init
		self.level_update['testbig003'] = self.DoorTest

		self.level_init['level1'] = self.level1_init
		self.level_update['level1'] = self.level1_update


		self.level_init['level3'] = self.level3_init
		self.level_update['level3'] = self.level3_update

	# on_levelstart: gets called when level is first loaded
	def on_levelstart(self,level_id):

		# examples:
		# You can access static level data loaded in from json
		# resources.levels[level_id].data['tilemap']['layer_b'] etc.

		# you can access the tilemap via:
		# t = self.parent.tiledlayers
		# t.UpdateTileLayer(tile, layer, tileval) # layer: 1: mid, 2: fore: change value in displayed tiles

		#item = self.parent.tiledlayers.items[0]
		#self.parent.tiledlayers.guards[0].PickupItem(item)

		if self.parent.tiledlayers.level_id in self.level_init:
			self.level_init[self.parent.tiledlayers.level_id]()

	def on_update(self):
		# this method gets called every game frame (don't make it do super slow stuff :) )
		if self.parent.tiledlayers.level_id in self.level_update:
			self.level_update[self.parent.tiledlayers.level_id]()

	# SPECIFIC LEVEL FUNCTIONS BELOW HERE

	def level1_init(self):
		self.parent.tiledlayers.guards[0].waypoints = [132, 623]
		self.parent.tiledlayers.guards[0].current_wp = 0
		self.parent.tiledlayers.passages[0].Open()
		self.parent.tiledlayers.passages[1].Open()

	def level1_update(self):
		if self.parent.tiledlayers.buttons[0].state == True and self.parent.tiledlayers.buttons[1].state == True:
			self.parent.tiledlayers.passages[3].Open()

	def level3_init(self):
		# self.parent.tiledlayers.guards[0].waypoints = [132, 623]
		# self.parent.tiledlayers.guards[0].current_wp = 0
		# DOORS
		self.parent.tiledlayers.passages[0].Open()
		self.parent.tiledlayers.passages[1].Open()
		# GUARD 0
		self.parent.tiledlayers.guards[0].waypoints = [271, 521, 688, 503]
		self.parent.tiledlayers.guards[0].current_wp = 0
		# GUARD 1
		sword = self.parent.tiledlayers.items[2]
		self.parent.tiledlayers.guards[1].PickupItem(sword)
		# GUARD 3
		self.parent.tiledlayers.guards[3].waypoints = [792, 797, 920, 925]
		# BUTTONS
		self.buttonProgress = 0
		self.lastPress = -1

	def level3_update(self):
		if self.parent.tiledlayers.buttons[0].state == True:
			self.parent.tiledlayers.passages[0].Open()
			self.parent.tiledlayers.passages[1].Open()
		else:
			self.parent.tiledlayers.passages[0].Close()
			self.parent.tiledlayers.passages[1].Close()
		for i in range(1, 5):
			if self.parent.tiledlayers.buttons[i].state == True:
				if self.buttonProgress == 0:
					self.buttonProgress = 1
					self.lastPress = i
				elif self.lastPress == i:
					continue
				elif self.lastPress == i - 1 or self.lastPress == 4 and i == 1:
					self.buttonProgress += 1
					self.lastPress = i
				elif self.buttonProgress != i:
					self.buttonProgress = 0
		if self.buttonProgress == 4:
			self.parent.tiledlayers.passages[3].Open()
		if self.parent.tiledlayers.buttons[5].state == True:
			self.parent.tiledlayers.passages[5].Open()


	def testbig003_init(self):
		self.parent.tiledlayers.guards[0].waypoints = [141,341,528,391]
		self.parent.tiledlayers.guards[0].current_wp = 0
		if self.parent.tiledlayers.level_id == 'testbig003':
			self.DoorTest()

	# Example method for opening a door if two buttons stood on
	def DoorTest(self):
		if self.parent.tiledlayers.buttons[0].state == True and self.parent.tiledlayers.buttons[1].state == True:
			self.parent.tiledlayers.passages[3].Open()
		else:
			self.parent.tiledlayers.passages[3].Close()
