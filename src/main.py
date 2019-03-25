#!/usr/bin/python

"""
main.py: Main entry point for game
"""

from builtins import range

import os
import pygame
from pygame.locals import *
from gamedirector import *

import resources
import game

# Start
def main(mainpath):

    # Initialise pygame
    pygame.init()
    pygame.mixer.init()
    
    # start up director
    framerate = 30
    screen_res = (640,480)
    window_title = "Pyweek27: Team Chimera"
    dir = GameDirector(window_title, screen_res, framerate)
    
    # Load resources
    resources.init(mainpath,screen_res)
    
    # Load game scenes
    maingame = game.MainGame(dir, screen_res)
    dir.addscene('maingame', maingame)
    
    # start up director
    dir.change_scene('maingame', [True, 'test001'])
    dir.loop()
    
