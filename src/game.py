#!/usr/bin/python

"""
game.py: main in-game scene classes
"""

from builtins import range

import os
import pygame
from pygame.locals import *
from gamedirector import *

import random
from math import *

import resources
import tilemap
import players

class Camera(object):
	def __init__(self,parent,screen_size,stickyness=0.33):
		self.parent = parent
		self.x = -1
		self.y = -1
		self.w_view = screen_size[0]
		self.h_view = screen_size[1]
		self.stickyness = stickyness
	def UpdateCamera(self,focus):
		if (focus[0] - self.x) > self.stickyness*self.w_view/2:
			self.x = focus[0] - self.stickyness*self.w_view/2
		elif (focus[0] - self.x) < -self.stickyness*self.w_view/2:
			self.x = focus[0] + self.stickyness*self.w_view/2
		if (focus[1] - self.y) > self.stickyness*self.h_view/2:
			self.y = focus[1] - self.stickyness*self.h_view/2
		elif (focus[1] - self.y) < -self.stickyness*self.h_view/2:
			self.y = focus[1] + self.stickyness*self.h_view/2
		if self.x < self.w_view/2:
			self.x = self.w_view/2
		elif self.x > (self.xlim-self.w_view/2):
			self.x = self.xlim-self.w_view/2
		if self.y < self.h_view/2:
			self.y = self.h_view/2
		elif self.y > (self.ylim-self.h_view/2):
			self.y = self.ylim-self.h_view/2

class MainGame(GameScene):
	def __init__(self, director, window_size):
		super(MainGame, self).__init__(director)
		self.window_size = window_size
		
		# frame rate recording
		self.avgframerate = -1
		self.frsamples = 0
	
	def on_switchto(self, switchtoargs):
	
		# Check if un-pause or resetting level
		lvlreset = switchtoargs[0]
		if not lvlreset:
			return
		level_id = switchtoargs[1]
		
		# Initialise objects
		self.camera = Camera(self,self.window_size)
		self.tiledlayers = tilemap.TiledLayers(self)
		self.control = players.MasterControl(self,resources.controlmap)
		self.inmates = []
		for i in range(3):
			self.inmates.append(players.Inmate(self))
		
		# load level data
		self.tiledlayers.init_level(level_id)
	
	def on_update(self):
	
		# Update player motion and camera
		for inmate in self.inmates:
			inmate.UpdateMotion()
		self.camera.UpdateCamera([int(self.inmates[self.control.current_p].x),int(self.inmates[self.control.current_p].y)])
		
		# framerate tracking
		self.frsamples += 1
		if self.frsamples == 1:
			self.avgframerate = self.director.framerate
		else:
			self.avgframerate = self.avgframerate + (self.director.framerate - self.avgframerate)/(self.frsamples)
		
	def on_event(self, events):
		for event in events:
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				self.director.change_scene(None, [])
			elif event.type == KEYDOWN or event.type == KEYUP:
				self.control.ProcessKeyEvent(event)
	
	def draw(self, screen):
		screen.fill((0,0,0))
		self.tiledlayers.RenderBGLayer(screen)
		for inmate in self.inmates:
			inmate.Draw(screen)
		self.tiledlayers.RenderFGLayer(screen)
	
	def on_draw(self, screen):
		self.draw(screen)
