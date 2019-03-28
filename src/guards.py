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
		
		self.speed = 5
		self.speed_d = 4
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
		#self.mode = 'patrol'
		#self.waypoints = [141,341,528,391,-1]
		#self.current_wp = 0
		self.mode = 'none'
		self.waypoints = []
		self.current_wp = -1
		
		self.maxrpatrol = 32*10
		self.maxrinvestigate = 32*5
		self.maxrchase = 32*5
		
		self.wait_to = -1
		self.target = None
		self.last_seen = [-1,-1]
		self.tlastseen = 0
		
		self.was_stuck = False
		self.stuck_to = 0
	
	def CheckVisibility(self,xtarget,ytarget,maxr):
		msx = self.parent.tiledlayers.map_size[0]
		ts = self.parent.tiledlayers.tilesize
		dist = sqrt(pow(xtarget-self.x,2)+pow(ytarget-self.y,2))
		if dist > maxr:
			return False
		if dist < 32:
			return True
		step = 8
		dx = step*(xtarget-self.x)/dist
		dy = step*(ytarget-self.y)/dist
		x = self.x
		y = self.y
		n = dist/step
		for i in range(int(n)):
			x += dx
			y += dy
			tile = msx*int(y/ts)+int(x/ts)
			if self.parent.tiledlayers.occlayer[tile]:
				return False
		return True
	
	def CheckClearPath(self,xtarget,ytarget,maxr):
		msx = self.parent.tiledlayers.map_size[0]
		ts = self.parent.tiledlayers.tilesize
		dist = sqrt(pow(xtarget-self.x,2)+pow(ytarget-self.y,2))
		if dist > maxr:
			return False
		if dist < 32:
			return True
		step = 8
		dx = step*(xtarget-self.x)/dist
		dy = step*(ytarget-self.y)/dist
		x = self.x
		y = self.y
		x2 = self.x - dy
		y2 = self.y + dx
		x3 = self.x + dy
		y3 = self.y - dx
		n = dist/step
		for i in range(int(n)):
			x += dx
			y += dy
			tile = msx*int(y/ts)+int(x/ts)
			x2 += dx
			y2 += dy
			tile2 = msx*int(y2/ts)+int(x2/ts)
			x3 += dx
			y3 += dy
			tile3 = msx*int(y3/ts)+int(x3/ts)
			if self.parent.tiledlayers.occlayer[tile] or self.parent.tiledlayers.occlayer[tile2] or self.parent.tiledlayers.occlayer[tile3]:
				return False
		return True
	
	def IncrementPath(self,speed):
		if len(self.path) > 0: # have a path, control player to next point
			tsize = self.parent.tiledlayers.tilesize
			msx = self.parent.tiledlayers.map_size[0]
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
		else:
			vx = 0
			vy = 0
		return (vx,vy)
	
	def UpdateMotion(self):
		
		tsize = self.parent.tiledlayers.tilesize
		msx = self.parent.tiledlayers.map_size[0]
		init_tile = self.parent.tiledlayers.map_size[0]*int(self.y/tsize)+int(self.x/tsize)
		
		# Run through behaviours
		
		#speed = self.speeda
		#speed_d = self.speed_da
		speed = self.speed
		speed_d = self.speed_d
		anispeed2 = self.anispeed2
		
		direct_chase = False
		
		if self.mode == 'none':
			vx = 0
			vy = 0
		elif self.mode == 'patrol':
			
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
			
			# control along path
			(vx,vy) = self.IncrementPath(speed)
			
			# check if can see any players
			for inmate in self.parent.inmates:
				seen = self.CheckVisibility(inmate.x,inmate.y,self.maxrpatrol)
				if seen:
					self.mode = 'chase'
					self.target = inmate
					self.path = []
					self.last_seen = [self.target.x,self.target.y]
					self.tlastseen = 0
					break
		
		elif self.mode == 'chase':
			
			# update time since last seen
			self.tlastseen += 1
			
			dist = sqrt(pow(self.target.x-self.x,2)+pow(self.target.y-self.y,2))
			if dist < 48 and not self.parent.caught:
				self.parent.caught = True
				self.parent.caught_to = 60
				self.parent.caught_id = self.target
			if dist > self.maxrpatrol:
				self.mode = 'wait'
				self.wait_to = 60
				vx = 0
				vy = 0
			else:
				seen = self.CheckClearPath(self.target.x,self.target.y,self.maxrpatrol)
				if seen and not self.was_stuck and self.stuck_to == 0:
					
					direct_chase = True
					self.path = []
					self.last_seen = [self.target.x,self.target.y]
					self.tlastseen = 0
					if abs(self.target.x-self.x) > speed:
						vx = int((self.target.x-self.x)/abs(self.target.x-self.x))
					else:
						vx = 0
					if abs(self.target.y-self.y) > speed:
						vy = int((self.target.y-self.y)/abs(self.target.y-self.y))
					else:
						vy = 0
				else:
					# check if other players visible, better target
					for inmate in self.parent.inmates:
						seen_other = self.CheckClearPath(inmate.x,inmate.y,self.maxrchase)
						if seen_other:
							self.mode = 'chase'
							self.target = inmate
							self.path = []
							self.last_seen = [self.target.x,self.target.y]
							self.tlastseen = 0
							vx = 0
							vy = 0
							break
					if not seen_other:
						if self.tlastseen == 30:
							
							target_tile = msx*int(self.target.y/tsize)+int(self.target.x/tsize)
							self.path = self.parent.tiledlayers.planner.astar_path(init_tile, target_tile)
							#tile_skip = self.path.pop(0)
							self.last_seen = [self.target.x,self.target.y]
						if len(self.path) > 0:
							(vx,vy) = self.IncrementPath(speed)
						else:
							distlastseen = sqrt(pow(self.last_seen[0]-self.x,2)+pow(self.last_seen[1]-self.y,2))
							#if distlastseen < 2*speed:
							if distlastseen < 32:
								
								self.mode = 'wait'
								self.wait_to = 60
								self.path = []
								vx = 0
								vy = 0
							else:
								#print('planning')
								target_tile = msx*int(self.last_seen[1]/tsize)+int(self.last_seen[0]/tsize)
								self.path = self.parent.tiledlayers.planner.astar_path(init_tile, target_tile)
								#tile_skip = self.path.pop(0)
								if len(self.path) == 0:
									self.mode = 'wait'
									self.wait_to = 60
									self.path = []
								vx = 0
								vy = 0
		
		elif self.mode == 'wait':
			
			vx = 0
			vy = 0
			
			# check if can see any players
			for inmate in self.parent.inmates:
				seen = self.CheckVisibility(inmate.x,inmate.y,self.maxrpatrol)
				if seen:
					self.mode = 'chase'
					self.target = inmate
					self.path = []
					self.last_seen = [self.target.x,self.target.y]
					self.tlastseen = 0
					break
			
			self.wait_to -= 1
			if self.wait_to < 0:
				self.mode = 'patrol'
		
		# Update whether seen
		for inmate in self.parent.inmates:
			seen = self.CheckVisibility(inmate.x,inmate.y,self.maxrpatrol)
			if seen:
				inmate.seen = True
			else:
				inmate.seen = False
			
		lastmoving = self.moving
		if abs(vx) > 0 or abs(vy) > 0:
			self.moving = True
		else:
			self.moving = False
		
		prevx = self.x
		prevy = self.y
		
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
		playersize_x = 16
		playersize_y = 16
		(self.x,self.y) = self.parent.tiledlayers.HandleObjectWallCollision((self.x,self.y),(playersize_x,playersize_y),(vx,vy))
		
		# double check not getting stuck on wall
		self.was_stuck = False
		if self.stuck_to > 0:
			self.stuck_to -= 1
		if direct_chase and self.x == prevx and self.y == prevy:
			self.was_stuck = True
			self.stuck_to = 30
			#print('stuck!')
		
		# Check if need to inform tilemap object layer of updates
		final_tile = self.parent.tiledlayers.map_size[0]*int(self.y/tsize)+int(self.x/tsize)
		if not init_tile == final_tile:
			self.parent.tiledlayers.UpdateObj(init_tile,final_tile,self)
	
	def Draw(self,screen):
		ts = self.parent.tiledlayers.tilesize
		msx = self.parent.tiledlayers.map_size[0]
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
		if len(self.path) > 0 and resources.debug_graphics:
			for tile in self.path:
				x = ts*(tile%msx) + int(ts/2)
				y = ts*int(tile/msx) + int(ts/2)
				pygame.draw.rect(screen, (255,128,0), pygame.Rect((x-(8/2)-self.parent.camera.x+int(self.parent.camera.w_view/2),y-int(8/2)-self.parent.camera.y+int(self.parent.camera.h_view/2)),(8,8)))
	
		
			
