#!/usr/bin/python

"""
resources.py: Load all resource data once 
"""

from builtins import range

import os, sys
import pygame
from pygame.locals import *

import level_data

class GameFont(object):
    def __init__(self,mainpath,path,size):
        self.fontim = pygame.image.load(os.path.join(mainpath,'data','gfx',path)).convert()
        self.fontim.set_colorkey((255,0,255))
        
        #keys = list('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ? = abcdefghijklmnopqrstuvwxyz+,-.!"#$%&`():')
        keys = list('1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ.,_-+d/p!"`#&()o?$:;<>{}=v^[]p    ')
        self.rects = {}
        for i in range(7):
            for j in range(10):
                k = keys[i*10+j]
                self.rects[k] = [j*size[0],i*size[1],size[0],size[1]]
    
    def RenderSentence(self, sentence, maxx, maxy, align='left'):
        sentsurf = pygame.Surface((maxx,maxy))
        sentsurf.fill((255,0,255))
        sentsurf.convert()
        sentsurf.set_colorkey((255,0,255))
        textheight = self.rects['A'][3]
        maxlines = maxy/textheight
        linedist = 0
        line = 0
        offsets = []
        if align in ['centre','vcentre']:
            for word in sentence.split(' '):
                letters = word.split()[0]+' '
                wordsize = sum([self.rects[let][2] for let in letters])
                if wordsize > maxx:
                    return False
                if (linedist+wordsize) >= maxx:
                    line += 1
                    offsets.append((maxx-linedist)/2)
                    linedist = 0
                    if line == maxlines:
                        return False
                for let in letters:
                    linedist += self.rects[let][2]
                if word[-1] == '\n':
                    line += 1
                    offsets.append((maxx-linedist)/2)
                    linedist = 0
            offsets.append((maxx-linedist)/2)
            voffset = maxy/2 - ((line+1)*textheight)/2
            linedist = 0
            line = 0
        for word in sentence.split(' '):
            letters = word.split()[0]+' '
            wordsize = sum([self.rects[let][2] for let in letters])
            if wordsize > maxx:
                return False
            if (linedist+wordsize) >= maxx:
                line += 1
                linedist = 0
                if line == maxlines:
                    return False
            for let in letters:
                if align == 'centre':
                    sentsurf.blit(self.fontim,(linedist+offsets[line],textheight*line),area=self.rects[let])
                elif align == 'vcentre':
                    sentsurf.blit(self.fontim,(linedist+offsets[line],textheight*line+voffset),area=self.rects[let])
                else:
                    sentsurf.blit(self.fontim,(linedist,textheight*line),area=self.rects[let])
                linedist += self.rects[let][2]
            if word[-1] == '\n':
                line += 1
                linedist = 0
        return sentsurf

def init(mainpath,screen_res):
	
	global debug_graphics
	debug_graphics = True
	
	# Fonts and text
	gamefont = GameFont(mainpath,'font_2x.png',(18,26))
	gamefontsmall = GameFont(mainpath,'font_1x.png',(9,13))
	gamefontgrey = GameFont(mainpath,'fontgrey_2x.png',(18,26))
	gamefontgreysmall = GameFont(mainpath,'fontgrey_1x.png',(9,13))
	
	# In game text surfaces (pre-rendered)
	global text_surfs
	
	text_surfs = {}
	text_surfs['newgame_on'] = gamefont.RenderSentence('NEW GAME', 800, 26, align='vcentre')
	text_surfs['newgame_off'] = gamefontgrey.RenderSentence('NEW GAME', 800, 26, align='vcentre')
	text_surfs['continue_on'] = gamefont.RenderSentence('CONTINUE GAME', 800, 26, align='vcentre')
	text_surfs['continue_off'] = gamefontgrey.RenderSentence('CONTINUE GAME', 800, 26, align='vcentre')
	
	text_surfs['resume_on'] = gamefont.RenderSentence('RESUME GAME', 800, 26, align='vcentre')
	text_surfs['resume_off'] = gamefontgrey.RenderSentence('RESUME GAME', 800, 26, align='vcentre')
	text_surfs['reset_on'] = gamefont.RenderSentence('RESET GAME (R)', 800, 26, align='vcentre')
	text_surfs['reset_off'] = gamefontgrey.RenderSentence('RESET GAME (R)', 800, 26, align='vcentre')
	text_surfs['help_on'] = gamefont.RenderSentence('HELP/TIPS', 800, 26, align='vcentre')
	text_surfs['help_off'] = gamefontgrey.RenderSentence('HELP/TIPS', 800, 26, align='vcentre')
	text_surfs['quit_on'] = gamefont.RenderSentence('QUIT GAME', 800, 26, align='vcentre')
	text_surfs['quit_off'] = gamefontgrey.RenderSentence('QUIT GAME', 800, 26, align='vcentre')
	
	text_surfs['stage_clear'] = gamefont.RenderSentence('STAGE CLEAR!', 800, 26, align='vcentre')
	
	text_surfs['controls001'] = gamefontgreysmall.RenderSentence('CONTROLS:', 800, 13, align='vcentre')
	text_surfs['controls002'] = gamefontgreysmall.RenderSentence('ARROW KEYS: MOVE PLAYER', 800, 13, align='vcentre')
	text_surfs['controls003'] = gamefontgreysmall.RenderSentence('TAB: SWITCH BETWEEN PLAYERS', 800, 13, align='vcentre')
	text_surfs['controls004'] = gamefontgreysmall.RenderSentence('SPACE: PICKUP/USE/DROP/THROW ITEM', 800, 13, align='vcentre')
	
	text_surfs['help001'] = gamefontsmall.RenderSentence('GUIDE YOUR CREW, INMATE BY INMATE, TO ESCAPE THE PRISON. GET ALL PLAYERS TO THESE EXIT TILES. LEAVE NO MAN BEHIND!', 400, 39)
	text_surfs['help002'] = gamefontsmall.RenderSentence('GUARDS: THESE GUYS ARE EVERYWHERE. IF THEY CATCH ONE OF YOUR TEAM, IT`S BACK TO THE SLAMMER', 500, 26)
	text_surfs['help003'] = gamefontsmall.RenderSentence('DOORS: YOU`LL NEED COLOUR-CODED KEYS FOR THESE DOORS', 400, 26)
	text_surfs['help004'] = gamefontsmall.RenderSentence('BUTTONS: THESE CAN ACTIVATE DOORS', 400, 26)
	text_surfs['help005'] = gamefontsmall.RenderSentence('WEAK WALLS: IF YOU HAD A HAMMER, YOU COULD PROBABLY BREAK THESE DOWN', 400, 26)
	text_surfs['help006'] = gamefontsmall.RenderSentence('FENCE: GUARDS CAN`T SEE YOU BEHIND THIS (PROBABLY). YOU COULD THROW AN ITEM OVER IT (LIKE A KEY)', 500, 26)
	text_surfs['help007'] = gamefontsmall.RenderSentence('KEY: YOU`LL NEED THIS TO GET THROUGH SOME DOORS (PRESS SPACE): MAKE SURE TO MATCH THE COLOUR', 500, 26)
	text_surfs['help008'] = gamefontsmall.RenderSentence('RUBBER DUCKY: YOU COULD USE THIS TO DISTRACT A GUARD BY THROWING IT (SPACE WHILE MOVING)', 500, 26)
	text_surfs['help009'] = gamefontsmall.RenderSentence('SWORD: GUARDS CARRY THESE AROUND. IF YOU COULD GET YOUR HANDS ON ONE, THEY MIGHT BE SCARED OF YOU', 500, 26)
	text_surfs['help010'] = gamefontsmall.RenderSentence('HAMMER: COULD BREAK SOMETHING THAT WAS WEAK (USE SPACE)', 400, 26)
	text_surfs['help011'] = gamefontsmall.RenderSentence('PIECE OF CAKE: VERY DISTRACTING FOR GUARDS: A VERY YUMMY CAKE', 400, 26)
	
	text_surfs['level1tips'] = []
	text_surfs['level1tips'].append(gamefont.RenderSentence('WELCOME TO BLUELAND STATE PENITENTIARY, SCUM BAGS!', 800, 104, align='vcentre'))
	text_surfs['level1tips'].append(gamefont.RenderSentence('HOPE YOU BROUGHT SOME READING MATERIAL, BECAUSE YOU FELLAS ARE GOING TO BE HERE A LOOONG TIME!', 800, 104, align='vcentre'))
	text_surfs['level1tips'].append(gamefont.RenderSentence('GO AHEAD, STRETCH YOUR LEGS, HAVE A WALK AROUND (ARROW KEYS)', 800, 104, align='vcentre'))
	text_surfs['level1tips'].append(gamefont.RenderSentence('NOT MUCH ROOM TO PACE AROUND IN THERE! HA HA HA!', 800, 104, align='vcentre'))
	text_surfs['level1tips'].append(gamefont.RenderSentence('YOU WANNA OPEN THE DOOR? JUST WALK UP TO IT (AND PRESS SPACE)', 800, 104, align='vcentre'))
	text_surfs['level1tips'].append(gamefont.RenderSentence('OH YEAH, THATS RIGHT ... I FORGOT ITS LOCKED AND I HAVE THE ONLY KEY! HA HA HA!', 800, 104, align='vcentre'))
	text_surfs['level1tips'].append(gamefont.RenderSentence('ANYTIME YOU WANNA SWAP WITH YOUR GANG MEMBERS, SURE GO AHEAD (PRESS TAB)', 800, 104, align='vcentre'))
	text_surfs['level1tips'].append(gamefont.RenderSentence('ACTUALLY, YOU CAN`T DO THAT EITHER CAUSE THEYRE ON THE OTHER SIDE OF THE PRISON!', 800, 104, align='vcentre'))
	text_surfs['level1tips'].append(gamefont.RenderSentence('YOU BOYS AINT EVER GETTIN OUT! HA HA HA!', 800, 104, align='vcentre'))
	text_surfs['level1tips'].append(gamefont.RenderSentence('(PRESS ESC AND SEE HELP/TIPS IF DESIRED)', 800, 104, align='vcentre'))
	
	# Load tileset image, set tile coords
	global tiles
	global tiles_coords
	
	tiles = pygame.image.load(os.path.join(mainpath,'data','gfx','tileset_2x.png')).convert()
	tiles.set_colorkey((255,0,255))
	tiles_coords = []
	for j in range(14):
		for i in range(10):
			tiles_coords.append((i*32, j*32, 32, 32))
	
	global water_animation_tiles
	water_animation_tiles = [[70,71,72,71],[80,81,82,81],[90,91,92,91]]
	#water_animation_tiles = [70,71,72]
	
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
	
	global titlegfx
	titlegfx = []
	titlegfx.append(pygame.image.load(os.path.join(mainpath,'data','gfx','title001.png')).convert())
	titlegfx[-1].set_colorkey((255,0,255))
	titlegfx.append(pygame.image.load(os.path.join(mainpath,'data','gfx','title002.png')).convert())
	titlegfx[-1].set_colorkey((255,0,255))
	titlegfx.append(pygame.image.load(os.path.join(mainpath,'data','gfx','title003.png')).convert())
	titlegfx[-1].set_colorkey((255,0,255))
	
	# Cutscene Surfaces
	global cutscenesurfs
	cutscenesurfs = {}
	
	# Logo
	cutscenesurfs['team_chimera'] = pygame.image.load(os.path.join(mainpath,'data','gfx','team_chimera_6x.png')).convert()
	cutscenesurfs['team_chimera'].set_colorkey((255,0,255))
	
	# News at start
	cutscenesurfs['news001'] = pygame.image.load(os.path.join(mainpath,'data','gfx','news_2x.png')).convert()
	cutscenesurfs['news001'].set_colorkey((255,0,255))
	
	# News at end
	cutscenesurfs['news002'] = pygame.image.load(os.path.join(mainpath,'data','gfx','news2_2x.png')).convert()
	cutscenesurfs['news002'].set_colorkey((255,0,255))
	
	# Load level data
	global levels
	levels = {}
	file_paths = [i for i in os.listdir(os.path.join(mainpath,'data','level')) if "json" in i]
	for f in file_paths:
		level_name = f[:-5]
		levels[level_name] = level_data.LevelData(path=os.path.join(mainpath,'data','level',f))
	
	global level_list
	#level_list = ['level1','level2','level3','testbig003','test001']
	level_list = ['testbig003']
	
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
	soundfx['policesiren'] = pygame.mixer.Sound(os.path.join(mainpath,'data','snd','policesiren.ogg'))
	
	# Music Data
	global musicpaths
	musicpaths = {}
	musicpaths['tense_chase'] = os.path.join(mainpath,'data','music','tense_chase.ogg')
	musicpaths['sneaky'] = os.path.join(mainpath,'data','music','sneaky.ogg')
	
	global level_music
	level_music = ['sneaky','sneaky','sneaky','sneaky','sneaky','sneaky','sneaky','sneaky','sneaky','sneaky']
	
	# pre-sets and controls
	global controlmap
	controlmap = {}
	controlmap['R'] = K_RIGHT
	controlmap['L'] = K_LEFT
	controlmap['D'] = K_DOWN
	controlmap['U'] = K_UP
	controlmap['switch'] = K_TAB
	controlmap['action'] = K_SPACE

