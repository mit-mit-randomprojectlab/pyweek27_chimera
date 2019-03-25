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

class KeyControl(object):
	def __init__(self,controlmap):
		self.CM = controlmap
		self.l = 0
		self.r = 0
		self.u = 0
		self.d = 0
		self.action = 0
	
	def ProcessKeyEvent(self,event):
		if event.type == KEYDOWN:
			if event.key == self.CM["L"]:
				self.l = 1
			elif event.key == self.CM["R"]:
				self.r = 1
			elif event.key == self.CM["U"]:
				self.u = 1
			elif event.key == self.CM["D"]:
				self.d = 1
			elif event.key == self.CM["action"]:
				self.action = 1
		elif event.type == KEYUP:
			if event.key == self.CM["L"]:
				self.l = 0
			elif event.key == self.CM["R"]:
				self.r = 0
			elif event.key == self.CM["U"]:
				self.u = 0
			elif event.key == self.CM["D"]:
				self.d = 0
			elif event.key == self.CM["action"]:
				self.action = 0



class Inmate(object):
    def __init__(self,parent):
        self.parent = parent
        self.alive = True
        self.x = -1
        self.y = -1
        self.heading = 0
        self.moving = False
        self.speed = 4
        self.speed_d = 3
        self.control = KeyControl(resources.controlmap)
    
    def UpdateMotion(self):
        
        # dead?
        if not self.alive:
        	return
        
        tsize = self.parent.tiledlayers.tilesize
        init_tile = self.parent.tiledlayers.map_size[0]*int(self.y/tsize)+int(self.x/tsize)
        
        # Check for player input (motion)
        vx = self.control.r-self.control.l
        vy = self.control.d-self.control.u
        
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
        
        # Set heading info
        if vx > 0:
            self.heading = 2
        elif vx < 0:
            self.heading = 3
        elif vy > 0:
        	self.heading = 1
        elif vy < 0:
        	self.heading = 0
        
        # Handle world boundaries
        if self.x < (tsize/2):
        	self.x = (tsize/2)
        elif self.x > self.parent.tiledlayers.map_size[0]*tsize-(tsize/2):
        	self.x = self.parent.tiledlayers.map_size[0]*tsize-(tsize/2)
        if self.y < (tsize/2):
        	self.y = (tsize/2)
        elif self.y > self.parent.tiledlayers.map_size[1]*tsize-(tsize/2):
        	self.y = self.parent.tiledlayers.map_size[1]*tsize-(tsize/2)
        
        # Handle all collisions off solid objects
        playersize_x = 24
        playersize_y = 24
        (self.x,self.y) = self.parent.tiledlayers.HandleObjectWallCollision((self.x,self.y),(playersize_x,playersize_y),(vx,vy))
        
        # Check if need to inform tilemap object layer of updates
        final_tile = self.parent.tiledlayers.map_size[0]*int(self.y/tsize)+int(self.x/tsize)
        if not init_tile == final_tile:
            self.parent.tiledlayers.UpdateObj(init_tile,final_tile,0)
    
    def Draw(self,screen):
    	ts = self.parent.tiledlayers.tilesize
        tilecoords = resources.charsprites_coords[0]
        imw = 32
        imh = 48
        boxw = 24
        boxh = 24
        pygame.draw.rect(screen, (255,0,0), pygame.Rect((self.x-(boxw/2)-self.parent.camera.x+self.parent.camera.w_view/2,self.y-(boxh/2)-self.parent.camera.y+self.parent.camera.h_view/2),(boxw,boxh)))
        screen.blit(resources.charsprites, (self.x-(imw/2)-self.parent.camera.x+self.parent.camera.w_view/2,self.y-(imh/2)-self.parent.camera.y+self.parent.camera.h_view/2-20), area=tilecoords)
