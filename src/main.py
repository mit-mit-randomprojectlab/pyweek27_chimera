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
    screen_res = (800,600)
    window_title = "Pyweek27: Team Chimera"
    dir = GameDirector(window_title, screen_res, framerate)
    
    # Load resources
    resources.init(mainpath,screen_res)
    
    # Load game scenes
    maingame = game.MainGame(dir, screen_res)
    maingame.savepath = os.path.join(mainpath,'data','saved_progress.txt')
    dir.addscene('maingame', maingame)
    
    pausescene = game.PauseScreen(dir, screen_res)
    dir.addscene('pausescene', pausescene)
    maingame.h_pausescene = pausescene
    pausescene.h_maingame = maingame
    
    titlescene = game.TitleScreen(dir, screen_res)
    titlescene.savepath = os.path.join(mainpath,'data','saved_progress.txt')
    titlescene.h_maingame = maingame
    dir.addscene('titlescene', titlescene)
    
    # start up director
    #dir.change_scene('maingame', [True, 'testbig003'])
    #dir.change_scene('maingame', [True, 'level1'])
    dir.change_scene('titlescene', [])
    dir.loop()
    
