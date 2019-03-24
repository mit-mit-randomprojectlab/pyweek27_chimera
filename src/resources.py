#!/usr/bin/python

"""
resources.py: Load all resource data once 
"""

import os, sys
import pygame
from pygame.locals import *

def init(mainpath,screen_res):
    
    # pre-sets and controls
    global controlmap
    controlmap = {}
    controlmap['R'] = K_RIGHT
    controlmap['L'] = K_LEFT
    controlmap['D'] = K_DOWN
    controlmap['U'] = K_UP
    controlmap['throw'] = K_SPACE

