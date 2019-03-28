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
import level_behaviours

class FadeInOut(object):
	def __init__(self,ticks):
		self.ticks = ticks
		self.ticks_elapsed = 0
		self.direction = 'none'
		self.alpha = 255
		self.finished_in = False
		self.finished_out = False
		self.musicfade = False
	
	def Update(self):
		if self.direction == 'in' and not self.finished_in:
			self.ticks_elapsed += 1
			if self.ticks_elapsed > self.ticks:
				self.finished_in = True
			else:
				#self.alpha = 255*(1.0-(self.ticks_elapsed/float(self.ticks)))
				self.alpha = 255*(1.0-((5*int(self.ticks_elapsed/5))/float(self.ticks)))
		elif self.direction == 'out' and not self.finished_out:
			self.ticks_elapsed += 1
			if self.ticks_elapsed > self.ticks:
				self.finished_out = True
			else:
				#self.alpha = 255*(self.ticks_elapsed/float(self.ticks))
				self.alpha = 255*((5*int(self.ticks_elapsed/5))/float(self.ticks))
				if self.musicfade:
					pygame.mixer.music.set_volume(0.5*(1.0 - (self.ticks_elapsed/float(self.ticks))))
	
	def FadeIn(self):
		self.direction = 'in'
		self.ticks_elapsed = 0
		self.finished_in = False
		self.finished_out = False
	
	def FadeOut(self,musicfade=False):
		self.direction = 'out'
		self.ticks_elapsed = 0
		self.finished_out = False
		self.finished_in = False
		self.musicfade = musicfade

class Camera(object):
	def __init__(self,parent,screen_size,stickyness=0.33):
		self.parent = parent
		self.x = -1
		self.y = -1
		self.w_view = screen_size[0]
		self.h_view = screen_size[1]
		self.stickyness = stickyness
		
		self.waypoint1 = [0,0]
		self.waypoint2 = [0,0]
		self.waypoint_to = -1
		self.wp_t = 15.0
	
	def SetWaypoint(self,waypoint):
		self.waypoint1 = [self.x,self.y]
		self.x = waypoint[0]
		self.y = waypoint[1]
		self.UpdateCameraWalls()
		self.waypoint2 = [self.x,self.y]
		self.waypoint_to = self.wp_t
		self.x = self.waypoint1[0]
		self.y = self.waypoint1[1]
	
	def UpdateCamera(self,focus):
		if self.waypoint_to >= 0:
			self.x = self.waypoint2[0] + (self.waypoint_to/self.wp_t)*(self.waypoint1[0]-self.waypoint2[0])
			self.y = self.waypoint2[1] + (self.waypoint_to/self.wp_t)*(self.waypoint1[1]-self.waypoint2[1])
			self.waypoint_to -= 1
		else:
			self.UpdateCameraSticky(focus)
			self.UpdateCameraWalls()
	
	def UpdateCameraSticky(self,focus):
		if (focus[0] - self.x) > self.stickyness*self.w_view/2:
			self.x = focus[0] - self.stickyness*self.w_view/2
		elif (focus[0] - self.x) < -self.stickyness*self.w_view/2:
			self.x = focus[0] + self.stickyness*self.w_view/2
		if (focus[1] - self.y) > self.stickyness*self.h_view/2:
			self.y = focus[1] - self.stickyness*self.h_view/2
		elif (focus[1] - self.y) < -self.stickyness*self.h_view/2:
			self.y = focus[1] + self.stickyness*self.h_view/2
	
	def UpdateCameraWalls(self):
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
		
		# fade in/out
		self.fade = FadeInOut(30)
		
		# Background
		self.background = pygame.Surface(window_size)
		self.background.fill((0,0,0))
		self.background.convert()
		
		# frame rate recording
		self.avgframerate = -1
		self.frsamples = 0
	
	def on_switchto(self, switchtoargs):
	
		# Check if un-pause or resetting level
		lvlreset = switchtoargs[0]
		if not lvlreset:
			return
		level_id = switchtoargs[1]
		
		self.paused = False
		self.exiting = False
		self.caught = False
		self.caught_to = 0
		
		# Initialise objects
		self.camera = Camera(self,self.window_size)
		self.tiledlayers = tilemap.TiledLayers(self)
		self.control = players.MasterControl(self,resources.controlmap)
		n_inmates = len([i for i in resources.levels[level_id].data['tilemap']['layerspawn'] if i >= 6 and i <= 11])
		self.inmates = []
		for i in range(n_inmates):
			self.inmates.append(players.Inmate(self))
		self.behaviours = level_behaviours.Level_Behaviours(self)
		
		# load level data
		self.tiledlayers.init_level(level_id)
		
		# example callback?
		#self.tiledlayers.buttons[0].statechange_callback = self.DoorTest # test callback
		
		# Initialise level behaviours
		self.behaviours.on_levelstart(level_id)
		
		# Fade in game
		self.background.fill((0,0,0))
		self.fade.FadeIn()
	
	def DoorTest(self):
		if self.tiledlayers.buttons[0].state == True and self.tiledlayers.buttons[1].state == True:
			self.tiledlayers.passages[3].Open()
		else:
			self.tiledlayers.passages[3].Close()
	
	def on_update(self):
	
		# Update player motion and camera
		for inmate in self.inmates:
			inmate.UpdateMotion()
		self.camera.UpdateCamera([int(self.inmates[self.control.current_p].x),int(self.inmates[self.control.current_p].y)])
		
		# Update tilemap entities
		self.tiledlayers.UpdateTileMapEntities()
		
		# Update level behaviours
		self.behaviours.on_update()
		
		# testing functions
		self.DoorTest()
		
		# framerate tracking
		self.frsamples += 1
		if self.frsamples == 1:
			self.avgframerate = self.director.framerate
		else:
			self.avgframerate = self.avgframerate + (self.director.framerate - self.avgframerate)/(self.frsamples)
		
		# check for ending level
		if not self.exiting and self.tiledlayers.exiting:
			self.exiting = True
			self.fade.FadeOut()
		
		# check reset level because caught
		if self.caught and self.caught_to > 0:
			self.caught_to -= 1
			if self.caught_to == 0:
				self.fade.FadeOut()
		
		# Control fade in/out, look for end game cues
		self.fade.Update()
		if self.fade.finished_out:
			if self.tiledlayers.exiting: # finished level
				ind_next = resources.level_list.index(self.tiledlayers.level_id)+1
				if ind_next == len(resources.level_list):
					ind_next = 0
				next_level = resources.level_list[ind_next]
				self.director.change_scene('maingame', [True, next_level])
			elif self.caught: # reset level
				self.director.change_scene('maingame', [True, self.tiledlayers.level_id])
		
	def on_event(self, events):
		for event in events:
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				self.director.change_scene(None, [])
			elif event.type == KEYDOWN or event.type == KEYUP:
				self.control.ProcessKeyEvent(event)
	
	def draw(self, screen):
		screen.fill((0,0,0))
		self.tiledlayers.RenderBGLayer(screen)
		for item in self.tiledlayers.items:
			item.Draw(screen)
		for guard in self.tiledlayers.guards:
			guard.Draw(screen)
		for inmate in self.inmates:
			inmate.Draw(screen)
		self.tiledlayers.RenderFGLayer(screen)
		if resources.debug_graphics:
			self.tiledlayers.RenderGoalTiles(screen)
	
	def on_draw(self, screen):
		self.draw(screen)
		if self.paused:
			self.background.set_alpha(128)
		else:
			self.background.set_alpha(self.fade.alpha)
		screen.blit(self.background, (0, 0))
