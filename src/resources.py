#!/usr/bin/python

"""
resources.py: Load all resource data once 
"""

from builtins import range

import os, sys
import pygame
from pygame.locals import *

import level_data

def init(mainpath,screen_res):
	
	global debug_graphics
	debug_graphics = True
	
	# Load tileset image, set tile coords
	global tiles
	global tiles_coords
	
	tiles = pygame.image.load(os.path.join(mainpath,'data','gfx','tileset_2x.png')).convert()
	tiles.set_colorkey((255,0,255))
	tiles_coords = []
	for j in range(14):
		for i in range(10):
			tiles_coords.append((i*32, j*32, 32, 32))
	
	global purpletile
	purpletile = pygame.Surface((32,32))
	purpletile.fill((255,0,255))
	purpletile.convert()
	
	# Load sprites
	global charsprites
	global charsprites_coords
	
	charsprites = pygame.image.load(os.path.join(mainpath,'data','gfx','chars_2x.png')).convert()
	charsprites.set_colorkey((255,0,255))
	charsprites_coords = []
	for j in range(7):
		for i in range(12):
			charsprites_coords.append((i*32, j*48, 32, 48))
	
	global itemsprites
	global itemsprites_coords
	
	itemsprites = pygame.image.load(os.path.join(mainpath,'data','gfx','items_2x.png')).convert()
	itemsprites.set_colorkey((255,0,255))
	itemsprites_coords = []
	for j in range(7):
		for i in range(6):
			itemsprites_coords.append((i*32, j*32, 32, 32))
	
	global guisprites
	global guisprites_coords
	
	guisprites = pygame.image.load(os.path.join(mainpath,'data','gfx','gui_2x.png')).convert()
	guisprites.set_colorkey((255,0,255))
	guisprites_coords = []
	for j in range(1):
		for i in range(3):
			guisprites_coords.append((i*32, j*32, 32, 32))
	
	# Load level data
	global levels
	levels = {}
	file_paths = [i for i in os.listdir(os.path.join(mainpath,'data','level')) if "json" in i]
	for f in file_paths:
		level_name = f[:-5]
		levels[level_name] = level_data.LevelData(path=os.path.join(mainpath,'data','level',f))
	
	global level_list
	level_list = ['testbig002','test001']
	
	# Sound Data
	global soundfx
	soundfx = {}
	soundfx['swish'] = pygame.mixer.Sound(os.path.join(mainpath,'data','snd','swish.ogg'))
	soundfx['drop'] = pygame.mixer.Sound(os.path.join(mainpath,'data','snd','drop.ogg')) # TODO: source
	soundfx['eating'] = pygame.mixer.Sound(os.path.join(mainpath,'data','snd','eating.ogg'))
	soundfx['button'] = pygame.mixer.Sound(os.path.join(mainpath,'data','snd','31589__freqman__buttons01.ogg'))
	soundfx['huh'] = pygame.mixer.Sound(os.path.join(mainpath,'data','snd','huh.ogg'))
	soundfx['siren'] = pygame.mixer.Sound(os.path.join(mainpath,'data','snd','siren.ogg'))
	soundfx['whistle'] = pygame.mixer.Sound(os.path.join(mainpath,'data','snd','whistle.ogg'))
	soundfx['door'] = pygame.mixer.Sound(os.path.join(mainpath,'data','snd','door.ogg'))
	soundfx['break'] = pygame.mixer.Sound(os.path.join(mainpath,'data','snd','boulders.ogg'))
	
	# pre-sets and controls
	global controlmap
	controlmap = {}
	controlmap['R'] = K_RIGHT
	controlmap['L'] = K_LEFT
	controlmap['D'] = K_DOWN
	controlmap['U'] = K_UP
	controlmap['switch'] = K_TAB
	controlmap['action'] = K_SPACE

