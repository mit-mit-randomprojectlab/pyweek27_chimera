#!/usr/bin/python

"""
game.py: main in-game scene classes
"""

from builtins import range

import os
import pygame
from pygame.locals import *
from gamedirector import *

import resources

import random
from math import *

class MainGame(GameScene):
    def __init__(self, director, window_size):
        super(MainGame, self).__init__(director)
        self.window_size = window_size
        
        # frame rate recording
        self.avgframerate = -1
        self.frsamples = 0
    
    def on_switchto(self, switchtoargs):
        self.data = 1
    
    def on_update(self):
        
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
    			    
    def draw(self, screen):
        screen.fill((255,255,255))
    
    def on_draw(self, screen):
        self.draw(screen)
