#!/usr/bin/python

"""
resources.py: Load all resource data once 
"""

from builtins import range

import os, sys
import pygame
from pygame.locals import *

def init(mainpath,screen_res):
	
	# Load tileset image, set tile coords
	global tiles
	global tiles_coords
	
	tiles = pygame.image.load(os.path.join(mainpath,'data','gfx','tileset_2x.png')).convert()
	tiles.set_colorkey((255,0,255))
	tiles_coords = []
	for j in xrange(14):
		for i in xrange(10):
			tiles_coords.append((i*32, j*32, 32, 32))
	
	# Load sprites
	
	
    # pre-sets and controls
    global controlmap
    controlmap = {}
    controlmap['R'] = K_RIGHT
    controlmap['L'] = K_LEFT
    controlmap['D'] = K_DOWN
    controlmap['U'] = K_UP
    controlmap['throw'] = K_SPACE

