#!/usr/bin/python

"""
guards.py: classes for controlling guards
"""

from builtins import range

import os
import pygame
from pygame.locals import *
from gamedirector import *

from math import *

import resources
    
class Guard(object):
	def __init__(self,parent,tile):
		self.parent = parent
		self.id = 13
		ts = self.parent.tiledlayers.tilesize
		msx = self.parent.tiledlayers.map_size[0]
		self.x = ts*(tile%msx)+int(ts/2)
		self.y = ts*int(tile/msx)+int(ts/2)
		self.parent.tiledlayers.InsertObj(tile,self)
		self.item = None
		
		self.speed = 4
		self.speed_d = 3
		self.speeda = 2
		self.speed_da = 2
		
		self.moving = False
		self.anispeed1 = 15
		self.anispeed2 = 5
		self.anispeed2a = 5
		self.gait = 0
		self.gait_to = self.anispeed1
		self.ani_to = -1
		
		self.path = []
		self.mode = 'patrol'
		self.waypoints = [141,341,528,391,-1]
		self.current_wp = 0
		#self.mode = 'none'
		#self.waypoints = []
		#self.current_wp = -1
	
	def UpdateMotion(self):
		
		tsize = self.parent.tiledlayers.tilesize
		msx = self.parent.tiledlayers.map_size[0]
		init_tile = self.parent.tiledlayers.map_size[0]*int(self.y/tsize)+int(self.x/tsize)
		
		# Run through behaviours
		if self.mode == 'none':
			vx = 0
			vy = 0
		if self.mode == 'patrol':
			
			speed = self.speeda
			speed_d = self.speed_da
			anispeed2 = self.anispeed2a
			
			# check for achieved path point
			if len(self.path) == 0: # plan to next waypoint, if available
				if self.current_wp >= 0:
					self.current_wp += 1
					if self.current_wp == len(self.waypoints):
						self.waypoints = []
						self.current_wp = -1
					if self.waypoints[self.current_wp] == -1: # cue to go back and repeat waypoints
						self.current_wp = 0
					self.path = self.parent.tiledlayers.planner.astar_path(init_tile, self.waypoints[self.current_wp])
			if len(self.path) > 0: # have a path, control player to next point
				xdest = tsize*(self.path[0]%msx) + int(tsize/2)
				ydest = tsize*int(self.path[0]/msx) + int(tsize/2)
				if abs(xdest-self.x) <= speed and abs(ydest-self.y) <= speed:
					tile_achieved = self.path.pop(0)
					if len(self.path) > 0: # still moving
						if self.parent.tiledlayers.occlayer[self.path[0]]: # check can still traverse
							self.path = []
						else:
							xdest = tsize*(self.path[0]%msx) + int(tsize/2)
							ydest = tsize*int(self.path[0]/msx) + int(tsize/2)
				if abs(xdest-self.x) > speed:
					vx = int((xdest-self.x)/abs(xdest-self.x))
				else:
					vx = 0
				if abs(ydest-self.y) > speed:
					vy = int((ydest-self.y)/abs(ydest-self.y))
				else:
					vy = 0
			else: # no path available
				vx = 0
				vy = 0
		
		else:
			
			speed = self.speed
			speed_d = self.speed_d
			anispeed2 = self.anispeed2
			
		lastmoving = self.moving
		if abs(vx) > 0 or abs(vy) > 0:
			self.moving = True
		else:
			self.moving = False
		
		if abs(vx) > 0 and abs(vy) > 0:
			self.x = self.x + speed_d*vx
			self.y = self.y + speed_d*vy
		else:
			self.x = self.x + speed*vx
			self.y = self.y + speed*vy
		
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
				self.gait_to = anispeed2
			else:
				self.gait_to -= 1
				if self.gait_to == 0:
					self.gait_to = anispeed2
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
			self.parent.tiledlayers.UpdateObj(init_tile,final_tile,self)
	
	def Draw(self,screen):
		ts = self.parent.tiledlayers.tilesize
		tile = 6*12 + self.gait
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
			pygame.draw.rect(screen, (255,255,0), pygame.Rect((self.x-(boxw/2)-self.parent.camera.x+int(self.parent.camera.w_view/2),self.y-int(boxh/2)-self.parent.camera.y+int(self.parent.camera.h_view/2)),(boxw,boxh)))
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
