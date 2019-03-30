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
				self.alpha = 255*(1.0-((1*int(self.ticks_elapsed/1))/float(self.ticks)))
		elif self.direction == 'out' and not self.finished_out:
			self.ticks_elapsed += 1
			if self.ticks_elapsed > self.ticks:
				self.finished_out = True
			else:
				#self.alpha = 255*(self.ticks_elapsed/float(self.ticks))
				self.alpha = 255*((1*int(self.ticks_elapsed/1))/float(self.ticks))
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

class ProgressData(object):
	def __init__(self,parent):
		self.parent = parent
		self.current_level = "level_"
	
	def LoadProgressData(self):
		f = open(self.parent.savepath, "r");
		self.current_level = f.readline().split()[0]
		f.close()
	
	def SaveProgressData(self):
		f = open(self.parent.savepath, "w");
		f.write('%s\n'%(self.current_level))
		f.close()
	
	def Reset(self):
		self.current_level = "level_"

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
		
		# Background
		self.background = pygame.Surface(window_size)
		self.background.fill((0,0,0))
		self.background.convert()
		
		self.background2 = pygame.Surface((800,200))
		self.background2.fill((0,0,0))
		self.background2.convert()
		self.background2.set_alpha(200)
		
		# Music
		self.current_music = 'none'
		
		# Initialise player data
		self.progress_data = ProgressData(self)
		
		# frame rate recording
		self.avgframerate = -1
		self.frsamples = 0
	
	def eb_on_levelstart(self):
		if self.tiledlayers.level_id == 'level2':
			self.tiledlayers.guards[0].waypoints = [444,892,885,469]
			self.tiledlayers.guards[0].current_wp = 0
			self.tiledlayers.guards[0].PickupItem(self.tiledlayers.items[0])
			self.tiledlayers.guards[1].waypoints = [496,484,869,880]
			self.tiledlayers.guards[1].current_wp = 0
			self.tiledlayers.guards[1].PickupItem(self.tiledlayers.items[1])
		elif self.tiledlayers.level_id == 'level4':
			self.tiledlayers.guards[0].waypoints = [247,250]
			self.tiledlayers.guards[0].current_wp = 0
			self.tiledlayers.guards[1].waypoints = [330,322]
			self.tiledlayers.guards[1].current_wp = 0
	
	def eb_on_update(self):
		if self.tiledlayers.level_id == 'level2':
			if self.tiledlayers.buttons[0].state == True:
				self.tiledlayers.passages[1].Open()
			else:
				self.tiledlayers.passages[1].Close()
		if self.tiledlayers.level_id == 'level4':
			if self.tiledlayers.buttons[0].state == True and self.tiledlayers.buttons[1].state == True and \
				self.tiledlayers.buttons[2].state == True and self.tiledlayers.buttons[3].state == True and \
				self.tiledlayers.buttons[4].state == True and self.tiledlayers.buttons[5].state == True:
				self.tiledlayers.passages[1].Open()
	
	def on_switchto(self, switchtoargs):
	
		# Check if un-pause or resetting level
		lvlreset = switchtoargs[0]
		if not lvlreset:
			return
		level_id = switchtoargs[1]
		
		# Save progress
		self.progress_data.current_level = level_id
		self.progress_data.SaveProgressData()
		
		self.paused = False
		self.exiting = False
		self.caught = False
		self.caught_to = 0
		
		# fade in/out
		self.fade = FadeInOut(30)
		
		# Initialise objects
		self.camera = Camera(self,self.window_size)
		self.tiledlayers = tilemap.TiledLayers(self)
		self.control = players.MasterControl(self,resources.controlmap)
		if level_id == 'level1':
			self.control.helptips_ind = 0
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
		self.eb_on_levelstart()
		
		# Check music
		if level_id in resources.level_list:
			level_music = resources.level_music[resources.level_list.index(level_id)]
		else:
			level_music = 'sneaky'
		if not self.current_music == level_music:
			self.current_music = level_music
			pygame.mixer.music.stop()
			if not self.current_music == 'none':
				pygame.mixer.music.load(resources.musicpaths[self.current_music])
				pygame.mixer.music.set_volume(0.5)
				pygame.mixer.music.play(-1)
		
		# Fade in game
		self.background.fill((0,0,0))
		self.fade.FadeIn()
	
	def on_update(self):
	
		# Update player motion and camera
		for inmate in self.inmates:
			inmate.UpdateMotion()
		self.camera.UpdateCamera([int(self.inmates[self.control.current_p].x),int(self.inmates[self.control.current_p].y)])
		
		# Update tilemap entities
		self.tiledlayers.UpdateTileMapEntities()
		
		# Update level behaviours
		self.behaviours.on_update()
		self.eb_on_update()
		
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
					self.current_music = 'none'
					self.director.change_scene('cutscene', ['news002','tense_chase','titlescene',[]])
				else:
					next_level = resources.level_list[ind_next]
					self.director.change_scene('maingame', [True, next_level])
			elif self.caught: # reset level
				self.director.change_scene('maingame', [True, self.tiledlayers.level_id])
		
	def on_event(self, events):
		for event in events:
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				self.draw(self.h_pausescene.background)
				self.director.change_scene('pausescene', [self.tiledlayers.level_id])
				#self.director.change_scene(None, [])
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
		for guard in self.tiledlayers.guards:
			guard.DrawGUI(screen)
		if resources.debug_graphics:
			self.tiledlayers.RenderGoalTiles(screen)
		if self.control.helptips_ind < 10: # drawing help surface messages on top
			screen.blit(self.background2, (0, 200))
			screen.blit(resources.text_surfs['level1tips'][self.control.helptips_ind], (0,250))
		if self.exiting:
			screen.blit(resources.text_surfs['stage_clear'], (0,250))
		#screen.blit(resources.text_surfs['test001'], (0,self.window_size[1]/2-resources.text_surfs['test001'].get_height()/2))
	
	def on_draw(self, screen):
		self.draw(screen)
		if self.paused:
			self.background.set_alpha(128)
		else:
			self.background.set_alpha(self.fade.alpha)
		screen.blit(self.background, (0, 0))

class MenuButton(object):
	def __init__(self,pos,surf_on,surf_off,go_func=None):
		self.pos = pos
		self.on = False
		self.surf_on = surf_on
		self.surf_off = surf_off
		self.go_func = go_func
	
	def Draw(self, screen):
		if self.on:
			screen.blit(self.surf_on, self.pos)
		else:
			screen.blit(self.surf_off, self.pos)

class MenuList(object):
	def __init__(self,buttons,select_ind,controlmap):
		self.buttons = buttons
		self.select_ind = select_ind
		self.buttons[self.select_ind].on = True
		self.CM = controlmap
	
	def ProcessKeyEvent(self,event):
		if event.type == KEYDOWN:
			if event.key == self.CM["U"]:
				self.buttons[self.select_ind].on = False
				self.select_ind = (self.select_ind-1) % len(self.buttons)
				self.buttons[self.select_ind].on = True
			elif event.key == self.CM["D"]:
				self.buttons[self.select_ind].on = False
				self.select_ind = (self.select_ind+1) % len(self.buttons)
				self.buttons[self.select_ind].on = True
			if event.key == self.CM["action"] or event.key == K_RETURN:
				self.buttons[self.select_ind].go_func()
	
	def Draw(self, screen):
		for b in self.buttons:
			b.Draw(screen)

class PauseScreen(GameScene):
	def __init__(self, director, window_size):
		super(PauseScreen, self).__init__(director)
		self.window_size = window_size
		
		# Background
		self.background = pygame.Surface(window_size)
		self.background.fill((0,0,0))
		self.background.convert()
		
		self.background2 = pygame.Surface((700,600-32))
		self.background2.fill((0,0,0))
		self.background2.convert()
		self.background2.set_alpha(200)
	
	def resume_game_now(self):
		self.director.change_scene('maingame', [False,-1])
	
	def reset_game_now(self):
		self.director.change_scene('maingame', [True,self.from_level])
	
	def help_game_now(self):
		self.help = True
	
	def DrawHelp(self,screen):
		screen.blit(self.background2, (50, 16))
		offsetx = 200
		offsety = 50
		screen.blit(resources.text_surfs['help001'], (offsetx,offsety-16))
		screen.blit(resources.text_surfs['help002'], (offsetx,offsety+48))
		screen.blit(resources.text_surfs['help003'], (offsetx,offsety+2*48))
		screen.blit(resources.text_surfs['help004'], (offsetx,offsety+3*48))
		screen.blit(resources.text_surfs['help005'], (offsetx,offsety+4*48))
		screen.blit(resources.text_surfs['help006'], (offsetx,offsety+5*48))
		screen.blit(resources.text_surfs['help007'], (offsetx,offsety+6*48))
		screen.blit(resources.text_surfs['help008'], (offsetx,offsety+7*48))
		screen.blit(resources.text_surfs['help009'], (offsetx,offsety+8*48))
		screen.blit(resources.text_surfs['help010'], (offsetx,offsety+9*48))
		screen.blit(resources.text_surfs['help011'], (offsetx,offsety+10*48))
		
		offsetx2 = 100
		screen.blit(resources.guisprites, (offsetx2,offsety-16), area=resources.guisprites_coords[2])
		screen.blit(resources.charsprites, (offsetx2,offsety+48-32), area=resources.charsprites_coords[12*6])
		screen.blit(resources.tiles, (offsetx2,offsety+2*48-24), area=(0,32*5,32,64))
		screen.blit(resources.tiles, (offsetx2,offsety+3*48), area=resources.tiles_coords[8])
		screen.blit(resources.tiles, (offsetx2,offsety+4*48), area=resources.tiles_coords[22])
		screen.blit(resources.tiles, (offsetx2,offsety+5*48-16), area=(6*32,0,32,64))
		screen.blit(resources.itemsprites, (offsetx2,offsety+6*48), area=resources.itemsprites_coords[0])
		screen.blit(resources.itemsprites, (offsetx2,offsety+7*48), area=resources.itemsprites_coords[16])
		screen.blit(resources.itemsprites, (offsetx2,offsety+8*48), area=resources.itemsprites_coords[13])
		screen.blit(resources.itemsprites, (offsetx2,offsety+9*48), area=resources.itemsprites_coords[12])
		screen.blit(resources.itemsprites, (offsetx2,offsety+10*48), area=resources.itemsprites_coords[17])

	
	def quit_game_now(self):
		self.h_maingame.current_music = 'none'
		pygame.mixer.music.stop()
		self.director.change_scene('titlescene', [])
	
	def on_switchto(self, switchtoargs):
		
		self.from_level = switchtoargs[0]
		self.help = False
		
		# Setup background
		backfade = pygame.Surface(self.background.get_size())
		backfade.fill((0,0,0))
		backfade.convert()
		backfade.set_alpha(128)
		self.background.blit(backfade, (0,0))
		
		# top-level menu buttons
		self.pos_v = 200
		self.button_resume = MenuButton((0,self.pos_v),resources.text_surfs['resume_on'],resources.text_surfs['resume_off'],self.resume_game_now)
		self.button_reset = MenuButton((0,self.pos_v+48),resources.text_surfs['reset_on'],resources.text_surfs['reset_off'],self.reset_game_now)
		self.button_help = MenuButton((0,self.pos_v+96),resources.text_surfs['help_on'],resources.text_surfs['help_off'],self.help_game_now)
		self.button_quit = MenuButton((0,self.pos_v+144),resources.text_surfs['quit_on'],resources.text_surfs['quit_off'],self.quit_game_now)
		self.buttonlist = [self.button_resume,self.button_reset,self.button_help,self.button_quit]
		self.topmenus = MenuList(self.buttonlist,0,resources.controlmap)
		
		# reset menu
		self.topmenus.select_ind = 0
		
	def on_update(self):
		pass
	
	def on_event(self, events):
		for event in events:
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				self.director.change_scene('maingame', [False,-1])
			if event.type == KEYDOWN and event.key == K_r: # bind "r" to reset level hotkey
				self.director.change_scene('maingame', [True,self.from_level])
			if event.type == KEYDOWN:
				if self.help:
					self.help = False
				else:
					self.topmenus.ProcessKeyEvent(event)
	
	def on_draw(self, screen):
		screen.blit(self.background, (0,0))
		if self.help:
			self.DrawHelp(screen)
		else:
			self.topmenus.Draw(screen)
			offset = 450
			screen.blit(resources.text_surfs['controls001'], (0,offset))
			screen.blit(resources.text_surfs['controls002'], (0,offset+16))
			screen.blit(resources.text_surfs['controls003'], (0,offset+32))
			screen.blit(resources.text_surfs['controls004'], (0,offset+48))

class TitleScreen(GameScene):
	def __init__(self, director, window_size):
		super(TitleScreen, self).__init__(director)
		self.window_size = window_size
		
		# Background
		self.background = pygame.Surface(window_size)
		self.background.fill((0,0,0))
		self.background.convert()
		
		self.fadebackground = pygame.Surface(window_size)
		self.fadebackground.fill((0,0,0))
		self.fadebackground.convert()
	
	def new_game_now(self):
		self.h_maingame.progress_data.Reset()
		#self.level_to = resources.level_list[0]
		self.level_to = 'cutscene'
		self.fade.FadeOut()
	
	def continue_game_now(self):
		self.h_maingame.progress_data.LoadProgressData()
		self.level_to = self.h_maingame.progress_data.current_level
		self.fade.FadeOut()
	
	def on_switchto(self, switchtoargs):
		
		# fade in/out
		self.fade = FadeInOut(30)
		
		# top-level menu buttons
		self.pos_v = 420
		if os.path.isfile(self.savepath):
			self.button_newgame = MenuButton((0,self.pos_v),resources.text_surfs['newgame_on'],resources.text_surfs['newgame_off'],self.new_game_now)
			self.button_continue = MenuButton((0,self.pos_v+48),resources.text_surfs['continue_on'],resources.text_surfs['continue_off'],self.continue_game_now)
			self.buttonlist = [self.button_newgame,self.button_continue]
		else:
			self.button_newgame = MenuButton((0,self.pos_v),resources.text_surfs['newgame_on'],resources.text_surfs['newgame_off'],self.new_game_now)
			self.buttonlist = [self.button_newgame]
		self.topmenus = MenuList(self.buttonlist,0,resources.controlmap)
		
		# reset menu
		self.topmenus.select_ind = 0
		
		self.tick = 0
		
		# Fade in game
		self.background.fill((0,0,0))
		self.fade.FadeIn()
		
	def on_update(self):
		self.tick = (self.tick+1) % 30
		self.fade.Update()
		if self.fade.finished_out:
			if self.level_to == 'cutscene':
				self.director.change_scene('cutscene', ['news001','none','maingame',[True,resources.level_list[0]]])
			else:
				self.director.change_scene('maingame', [True,self.level_to])
	
	def on_event(self, events):
		for event in events:
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				self.director.change_scene(None, [])
			if event.type == KEYDOWN:
				self.topmenus.ProcessKeyEvent(event)
	
	def on_draw(self, screen):
		screen.blit(self.background, (0,0))
		screen.blit(resources.titlegfx[0], (160,32))
		if int(self.tick/15) % 2 == 0:
			screen.blit(resources.titlegfx[1], (160,32))
			screen.blit(resources.titlegfx[2], (160,26))
		else:
			screen.blit(resources.titlegfx[1], (160,26))
			screen.blit(resources.titlegfx[2], (160,32))
		self.topmenus.Draw(screen)
		self.fadebackground.set_alpha(self.fade.alpha)
		screen.blit(self.fadebackground, (0, 0))

class CutScene(GameScene):
	def __init__(self, director, window_size):
		super(CutScene, self).__init__(director)
		self.window_size = window_size
		
		# Background
		self.background = pygame.Surface(window_size)
		self.background.fill((0,0,0))
		self.background.convert()
		
		self.fadebackground = pygame.Surface(window_size)
		self.fadebackground.fill((0,0,0))
		self.fadebackground.convert()
		
		self.fade = FadeInOut(30)
		self.exiting = False
	
	def on_switchto(self, switchtoargs):
		self.exiting = False
		self.scenesurf = switchtoargs[0]
		self.scenemusic = switchtoargs[1]
		self.nextscene = switchtoargs[2]
		self.nextscenedata = switchtoargs[3]
		
		# setup music
		if not self.scenemusic == 'none':
			pygame.mixer.music.stop()
			pygame.mixer.music.load(resources.musicpaths[self.scenemusic])
			pygame.mixer.music.set_volume(0.5)
			pygame.mixer.music.play(-1)
		else:
			pygame.mixer.music.stop()
		
		self.fade.FadeIn()
		
	def on_update(self):
		
		# Check for return to game
		self.fade.Update()
		if self.exiting and self.fade.direction == 'in':
			self.fade.FadeOut(True)
		if self.fade.finished_out:
			pygame.mixer.music.set_volume(0)
			self.director.change_scene(self.nextscene, self.nextscenedata)
	
	def on_event(self, events):
		for event in events:
			if event.type == KEYDOWN and event.key == K_ESCAPE:
				self.exiting = True
			if event.type == KEYDOWN:
				self.exiting = True
	
	def on_draw(self, screen):
		screen.blit(self.background, (0, 0))
		surf = resources.cutscenesurfs[self.scenesurf]
		screen.blit(surf, (400-surf.get_width()/2,300-surf.get_height()/2))
		self.fadebackground.set_alpha(self.fade.alpha)
		screen.blit(self.fadebackground, (0, 0))

