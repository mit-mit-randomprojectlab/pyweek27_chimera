#!/usr/bin/python

"""
players.py: classes for player-controlled inmates
"""

import os
import pygame
from pygame.locals import *
from gamedirector import *

import random
from math import *

import resources

class MasterControl(object):
	def __init__(self,parent,controlmap):
		self.parent = parent
		self.CM = controlmap
		self.current_p = 0
	
	def ProcessKeyEvent(self,event):
		current_control = self.parent.inmates[self.current_p].control
		if self.parent.tiledlayers.exiting:
			current_control.Stop()
			return
		if event.type == KEYDOWN:
			if event.key == self.CM["L"]:
				current_control.l = 1
			elif event.key == self.CM["R"]:
				current_control.r = 1
			elif event.key == self.CM["U"]:
				current_control.u = 1
			elif event.key == self.CM["D"]:
				current_control.d = 1
			elif event.key == self.CM["action"]:
				current_control.action = 1
			elif event.key == self.CM["switch"]:
				current_control.Stop() # set control variable for current player to zero before switching
				self.current_p += 1
				if self.current_p == len(self.parent.inmates): # TODO: might need to fix up for in-active inmates
					self.current_p = 0
				current_inmate = self.parent.inmates[self.current_p]
				self.parent.camera.SetWaypoint([current_inmate.x,current_inmate.y])
		elif event.type == KEYUP:
			if event.key == self.CM["L"]:
				current_control.l = 0
			elif event.key == self.CM["R"]:
				current_control.r = 0
			elif event.key == self.CM["U"]:
				current_control.u = 0
			elif event.key == self.CM["D"]:
				current_control.d = 0
			elif event.key == self.CM["action"]:
				current_control.action = 0

class KeyControl(object):
	def __init__(self):
		self.l = 0
		self.r = 0
		self.u = 0
		self.d = 0
		self.action = 0
	def Stop(self):
		self.l = 0
		self.r = 0
		self.u = 0
		self.d = 0
		self.action = 0

class Inmate(object):
	def __init__(self,parent):
		self.parent = parent
		self.id = None
		self.alive = True
		self.x = -1
		self.y = -1
		
		self.speed = 4
		self.speed_d = 3
		
		self.moving = False
		self.anispeed1 = 15
		self.anispeed2 = 5
		self.gait = 0
		self.gait_to = self.anispeed1
		self.ani_to = -1
		
		self.item = None
		
		self.control = KeyControl()
	
	def UpdateMotion(self):
	
		# dead?
		if not self.alive:
			return
		
		tsize = self.parent.tiledlayers.tilesize
		init_tile = self.parent.tiledlayers.map_size[0]*int(self.y/tsize)+int(self.x/tsize)
		
		# Check for player input (motion)
		vx = self.control.r-self.control.l
		vy = self.control.d-self.control.u
		
		lastmoving = self.moving
		if abs(vx) > 0 or abs(vy) > 0:
			self.moving = True
		else:
			self.moving = False
		
		if abs(vx) > 0 and abs(vy) > 0:
			self.x = self.x + self.speed_d*vx
			self.y = self.y + self.speed_d*vy
		else:
			self.x = self.x + self.speed*vx
			self.y = self.y + self.speed*vy
		
		# Animation control
		if not self.moving: # stationary animation
			if lastmoving:
				self.gait = 0
				self.gait_to = self.anispeed1
			else:
				self.gait_to -= 1
				if self.gait_to == 0:
					self.gait_to = self.anispeed1
					self.gait = (self.gait+1) % 2
		else: # moving
			if not lastmoving:
				self.gait = 0
				self.gait_to = self.anispeed2
			else:
				self.gait_to -= 1
				if self.gait_to == 0:
					self.gait_to = self.anispeed2
					self.gait = (self.gait+1) % 4
		
		# Handle world boundaries
		if self.x < (tsize/2):
			self.x = int(tsize/2)
		elif self.x > self.parent.tiledlayers.map_size[0]*tsize-int(tsize/2):
			self.x = self.parent.tiledlayers.map_size[0]*tsize-int(tsize/2)
		if self.y < (tsize/2):
			self.y = int(tsize/2)
		elif self.y > self.parent.tiledlayers.map_size[1]*tsize-int(tsize/2):
			self.y = self.parent.tiledlayers.map_size[1]*tsize-int(tsize/2)
		
		# Handle all collisions off solid objects
		playersize_x = 24
		playersize_y = 24
		(self.x,self.y) = self.parent.tiledlayers.HandleObjectWallCollision((self.x,self.y),(playersize_x,playersize_y),(vx,vy))
		
		# Check if need to inform tilemap object layer of updates
		final_tile = self.parent.tiledlayers.map_size[0]*int(self.y/tsize)+int(self.x/tsize)
		if not init_tile == final_tile:
			self.parent.tiledlayers.UpdateObj(init_tile,final_tile,self.id)
	
	def Draw(self,screen):
		ts = self.parent.tiledlayers.tilesize
		tile = (self.id-6)*12 + self.gait
		if self.moving:
			tile += 4
			if not self.item == None:
				tile += 4
		elif not self.item == None:
			tile += 2
		tilecoords = resources.charsprites_coords[tile]
		imw = 32
		imh = 48
		boxw = 24
		boxh = 24
		if resources.debug_graphics:
			pygame.draw.rect(screen, (255,0,0), pygame.Rect((self.x-(boxw/2)-self.parent.camera.x+int(self.parent.camera.w_view/2),self.y-int(boxh/2)-self.parent.camera.y+int(self.parent.camera.h_view/2)),(boxw,boxh)))
		screen.blit(resources.charsprites, (self.x-int(imw/2)-self.parent.camera.x+int(self.parent.camera.w_view/2),self.y-int(imh/2)-self.parent.camera.y+int(self.parent.camera.h_view/2)-20), area=tilecoords)
