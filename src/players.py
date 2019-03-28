#!/usr/bin/python

"""
players.py: classes for player-controlled inmates
"""

from builtins import range

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
		self.exiting = False
	
	def ProcessKeyEvent(self,event):
		current_control = self.parent.inmates[self.current_p].control
		if self.parent.caught: # cut controls if caught
			return
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
				current_inmate.flash_to = 30
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
		self.flash_to = -1
		
		self.item = None
		
		self.control = KeyControl()
		
		self.seen = False # debugging
	
	def CheckforItems(self):
		ts = self.parent.tiledlayers.tilesize
		msx = self.parent.tiledlayers.map_size[0]
		msy = self.parent.tiledlayers.map_size[1]
		tile = msx*int(self.y/ts)+int(self.x/ts)
		tx = tile%msx
		ty = int(tile/msx)
		coords = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
		options = []
		for (tilex,tiley) in coords:
			if tx+tilex < 0 or tx+tilex >= msx or ty+tiley < 0 or ty+tiley >= msy:
				continue
			tnow = msx*(ty+tiley)+tx+tilex
			cx = ts*(tnow%msx)+int(ts/2)
			cy = ts*int(tnow/msx)+int(ts/2)
			for obj in self.parent.tiledlayers.objectlayer[tnow]:
				if obj.id in [0,1,2,3,4,5,14,15,16,17]:
					options.append([obj,tnow,cx,cy])
		if len(options) == 1:
			item = options[0][0]
			item.Pickup()
			self.item = item
		elif len(options) > 1:
			dists = [pow(i[2]-self.x,2)+pow(i[3]-self.y,2) for i in options]
			ind = dists.index(min(dists))
			item = options[ind][0]
			item.Pickup()
			self.item = item
	
	def CheckforDoors(self):
		ts = self.parent.tiledlayers.tilesize
		msx = self.parent.tiledlayers.map_size[0]
		for passage in self.parent.tiledlayers.passages:
			if passage.type in ['door1','door2','door3','door4','door5','door6']:
				if self.item.id == int(passage.type[4])-1:
					cx = ts*(passage.tile%msx)+int(ts/2)
					cy = ts*int(passage.tile/msx)+int(ts/2)
					dist = pow(cx-self.x,2)+pow(cy-self.y,2)
					if dist < (32*32):
						passage.Open()
						self.item = None
						return True
		return False
	
	def CheckBreakWalls(self):
		ts = self.parent.tiledlayers.tilesize
		msx = self.parent.tiledlayers.map_size[0]
		for passage in self.parent.tiledlayers.passages:
			if passage.type == 'break' and passage.state == 'closed':
				if self.item.id == 15: # hammer hammer hammer
					cx = ts*(passage.tile%msx)+int(ts/2)
					cy = ts*int(passage.tile/msx)+int(ts/2)
					dist = pow(cx-self.x,2)+pow(cy-self.y,2)
					if dist < (32*32):
						passage.Open()
	
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
		if self.flash_to >= 0:
			self.flash_to -= 1
		
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
			self.parent.tiledlayers.UpdateObj(init_tile,final_tile,self)
		
		# check for actions
		if self.control.action:
			self.control.action = False
			if self.item == None:
				self.CheckforItems()
			else:
				if self.item.id <= 5:
					unlocked = self.CheckforDoors()
					if unlocked:
						return
				elif self.item.id == 15: # hammer
					self.CheckBreakWalls()
				if abs(vx) > 0 and abs(vy) > 0:
					speed = 6
				else:
					speed = 8
				self.item.Throw(self.x,self.y,speed*vx,speed*vy)
				self.item = None
	
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
		if resources.debug_graphics and self.seen:
			pygame.draw.rect(screen, (255,0,0), pygame.Rect((self.x-(boxw/2)-self.parent.camera.x+int(self.parent.camera.w_view/2),self.y-int(boxh/2)-self.parent.camera.y+int(self.parent.camera.h_view/2)),(boxw,boxh)))
		if self.flash_to == -1 or (self.flash_to % 8) < 4:
			screen.blit(resources.charsprites, (self.x-int(imw/2)-self.parent.camera.x+int(self.parent.camera.w_view/2),self.y-int(imh/2)-self.parent.camera.y+int(self.parent.camera.h_view/2)-20), area=tilecoords)
		if not self.item == None:
			if self.item.id <= 5:
				tile = self.item.id+6
			elif self.item.id >= 16:
				tile = self.item.id
			elif self.item.id == 15:
				tile = 12
			elif self.item.id == 14:
				tile = 13
			tilecoords = resources.itemsprites_coords[tile]
			screen.blit(resources.itemsprites, (self.x-int(imw/2)-self.parent.camera.x+int(self.parent.camera.w_view/2)+8,self.y-int(imh/2)-self.parent.camera.y+int(self.parent.camera.h_view/2)-20+8), area=tilecoords)
