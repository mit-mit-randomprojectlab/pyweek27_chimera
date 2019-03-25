#!/usr/bin/python

"""
level_editor.py: GUI for creating/editing level data
"""

from builtins import range

import os, sys
import pygame
from pygame.locals import *
from gamedirector import *

# start-up hidden Tkinter for using file open/save dialog
if (sys.version_info > (3, 0)): # Python 3
	import tkinter as tk
	from tkinter import filedialog
	from tkinter import Toplevel, Label, Entry, Button, StringVar
	root = tk.Tk()
	root.withdraw()
else: # Python 2
	import Tkinter, tkFileDialog
	from Tkinter import Toplevel, Label, Entry, Button, StringVar
	root = Tkinter.Tk()
	root.withdraw()

import level_data

item_list = [None, 'key','ducky']

# Load in resources
resources = {}
def init_resources(mainpath):
	resources['tiles'] = pygame.image.load(os.path.join(mainpath,'data','gfx','tileset_1x.png')).convert()
	resources['tiles'].set_colorkey((255,0,255))
	resources['tiles_coords'] = []
	for j in range(14):
		for i in range(10):
			resources['tiles_coords'].append((i*16, j*16, 16, 16))
	
	# Text data for draw modes
	font_draw = pygame.font.SysFont("arial", 12)
	resources['text_occ'] = font_draw.render('Occupancy Mode', True, (255,255,255))
	resources['text_bg'] = font_draw.render('Background Tile Mode', True, (255,255,255))
	resources['text_fg'] = font_draw.render('Foreground Tile Mode', True, (255,255,255))
	resources['text_item'] = font_draw.render('Item Mode (q to quit back to tiles)', True, (255,255,255))

# Class for dialog to get map size for new map
default_map_size = [32,32]
class MyDialog(object):
	def __init__(self, parent):
		top = self.top = Toplevel(parent)
		top.title('New Level')
		Label(top, text="No. X tiles").pack()
		content1 = StringVar()
		content1.set(str(default_map_size[0]))
		self.e = Entry(top, textvariable=content1)
		self.e.pack(padx=5)
		Label(top, text="No. Y tiles").pack()
		content2 = StringVar()
		content2.set(str(default_map_size[1]))
		self.e2 = Entry(top, textvariable=content2)
		self.e2.pack(padx=5)
		b = Button(top, text="OK", command=self.ok)
		b.pack(pady=5)
		b2 = Button(top, text="Cancel", command=self.cancel)
		b2.pack(pady=5)
	
	def ok(self):
		newlvl_result = 1
		default_map_size[0] = int(self.e.get())
		default_map_size[1] = int(self.e2.get())
		self.newlvl_result = 1
		self.top.destroy()
	
	def cancel(self):
		self.newlvl_result = 0
		self.top.destroy()

# Start
def main(mainpath):

    # Initialise pygame
    pygame.init()
    
    # start up director
    framerate = 30
    screen_res = (1200,700)
    
    window_title = "Level Editor: n/l/s (new/load/save), o (occupancy layer), b (background tiles), f (foreground tiles), g (toggle guide lines), a (auto-tiler), i (items)"
    dir = GameDirector(window_title, screen_res, framerate)
    
    # Load resources
    init_resources(mainpath)
    
    # Load edior
    level_edit = LevelEditor(dir, screen_res)
    dir.addscene('level_edit', level_edit)
    
    # start up director
    dir.change_scene('level_edit', [])
    dir.loop()

"""
class LevelData(object):
    
    def __init__(self):
        pass
    
    def AssignMonstersLayer(self,i,j):
        if i < 0 or i >= self.map_size[0] or j < 0 or j >= self.map_size[1]:
            return
        ind = monster_list.index(self.monsterlayer[self.map_size[0]*j+i])
        ind_new = (ind+1) % len(monster_list)
        self.monsterlayer[self.map_size[0]*j+i] = monster_list[ind_new]
    
    def AssignItemLayer(self,i,j):
        if i < 0 or i >= self.map_size[0] or j < 0 or j >= self.map_size[1]:
            return
        ind = item_list.index(self.itemlayer[self.map_size[0]*j+i])
        ind_new = (ind+1) % len(item_list)
        self.itemlayer[self.map_size[0]*j+i] = item_list[ind_new]
    
    def AssignTriggerLayer(self,i,j):
        if i < 0 or i >= self.map_size[0] or j < 0 or j >= self.map_size[1]:
        	return
        ind = trigger_list.index(self.triggerlayer[self.map_size[0]*j+i])
        ind_new = (ind+1) % len(trigger_list)
        self.triggerlayer[self.map_size[0]*j+i] = trigger_list[ind_new]
"""

class LevelEditor(GameScene):
    def __init__(self, director, window_size):
        super(LevelEditor, self).__init__(director)
        
        self.window_size = window_size
        self.background = pygame.Surface(window_size)
        self.background.fill((0, 0, 0))
        self.background.convert()
        
        self.mouse_pos = (0,0)
        self.draw_type = -1
        self.draw_type_item = 'null'
        self.tilemode = 0
        self.objectdrawtype = 'none'
        self.tilesize = 16
        self.zoom = 0
        self.guides = False
        
        #self.level = level_data.LevelData()
        self.level = None
        
        self.npal_x = 10
        self.npal_y = 14
        self.palette = pygame.Surface((self.npal_x*self.tilesize, self.npal_y*self.tilesize))
        self.palette.fill((0, 0, 0))
        self.palette.convert()
        for j in range(self.npal_y):
            for i in range(self.npal_x):
                self.palette.blit(resources['tiles'], (i*self.tilesize,j*self.tilesize), area=resources['tiles_coords'][i+self.npal_x*j])
        
        self.draw_offset = (16, 32) # fix up
        self.draw_offset_palette = (self.window_size[0]-self.tilesize-self.npal_x*self.tilesize, 2*self.tilesize)
        self.draw_offset_palette = (2*16 + 800, 2*16)
        self.reset_userdata()
    
    def reset_mainwindowsurf(self):
    	self.mainwindowsurf = pygame.Surface((self.level.data['tilemap']['size'][0]*self.tilesize, self.level.data['tilemap']['size'][1]*self.tilesize))
    	self.mainwindowsurf.fill((0, 0, 0))
    	self.mainwindowsurf.convert()
    	
    	sx = self.level.data['tilemap']['size'][0]*self.tilesize
    	sy = self.level.data['tilemap']['size'][1]*self.tilesize
    	offx = self.draw_offset[0]+400-sx/2
    	offy = self.draw_offset[1]+300-sy/2
    	
    	self.mainwindowparams = [sx,sy,offx,offy]
    
    def reset_userdata(self):
        self.userdata = []
    
    def AssignBGTile(self,i,j,value):
    	msx = self.level.data['tilemap']['size'][0]
    	msy = self.level.data['tilemap']['size'][1]
    	if i < 0 or i >= msx or j < 0 or j >= msy:
    		return
    	self.level.data['tilemap']['layer_b'][msx*j+i] = value
    
    def AssignFGTile(self,i,j,value):
    	msx = self.level.data['tilemap']['size'][0]
    	msy = self.level.data['tilemap']['size'][1]
    	if i < 0 or i >= msx or j < 0 or j >= msy:
    		return
    	self.level.data['tilemap']['layer_f'][msx*j+i] = value
    
    def ToggleOcc(self,i,j):
    	msx = self.level.data['tilemap']['size'][0]
    	msy = self.level.data['tilemap']['size'][1]
    	if i < 0 or i >= msx or j < 0 or j >= msy:
    		return
    	self.level.data['tilemap']['layerocc'][msx*j+i] = self.level.data['tilemap']['layerocc'][int(msx*j+i)] + 1
    	if self.level.data['tilemap']['layerocc'][msx*j+i] > 2:
    		self.level.data['tilemap']['layerocc'][msx*j+i] = 0
    
    def AutoUpdateTileLayers(self):
    	if self.level == None:
    		return
    	ts = self.tilesize
    	msx = self.level.data['tilemap']['size'][0]
    	msy = self.level.data['tilemap']['size'][1]
    	layerocc = self.level.data['tilemap']['layerocc']
    	layer_b = self.level.data['tilemap']['layer_b']
    	layer_f = self.level.data['tilemap']['layer_f']
    	for i in range(msx):
    		for j in range(msy):
    			if layerocc[msx*j+i] == 0:
    				self.AssignBGTile(i,j,26)
    				if j >= 1:
    					if layerocc[msx*(j-1)+i] == 1:
    						self.AssignBGTile(i,j,36)
    					elif layerocc[msx*(j-1)+i] == 2:
    						self.AssignBGTile(i,j,66)
    			elif layerocc[msx*j+i] == 1:
    				self.AssignBGTile(i,j,10)
    				if j >= 1:
    					self.AssignFGTile(i,j-1,1) # TODO: set based on connectivity to surrounds
    			elif layerocc[msx*j+i] == 2:
    				self.AssignBGTile(i,j,16)
    				if j >= 1:
    					self.AssignFGTile(i,j-1,6) # TODO: set based on connectivity to surrounds
    
    def on_switchto(self, switchtoargs):
        pass
    
    def on_update(self):
        self.mouse_pos = pygame.mouse.get_pos()
        #print self.mouse_pos
        
    def on_event(self, events):
    	
        for event in events:
        	if event.type == KEYDOWN and event.key == K_n: # starting a new file
        		d = MyDialog(root)
        		root.wait_window(d.top)
        		if d.newlvl_result == 1:
        			self.level = level_data.LevelData(path=None, size=default_map_size)
        			print('Created new level: %d by %d tiles'%(default_map_size[0],default_map_size[1]))
        			self.reset_mainwindowsurf()
        			self.reset_userdata()
        	if event.type == KEYDOWN and event.key == K_s: # saving level to file
        		if self.level == None:
        			continue
        		if (sys.version_info > (3, 0)):  # Python 3 code in this block
        			file_path = filedialog.asksaveasfilename(title='Save level file (.json):', defaultextension = '.json', filetypes = [('level files', '.json')])
        		else: # Python 2
        			file_path = tkFileDialog.asksaveasfilename(title='Save level file (.json):', defaultextension = '.json', filetypes = [('level files', '.json')])
        		if len(file_path) > 0:
        			self.level.SaveLevel(file_path)
        			print('Saved level to %s'%(file_path))
        	if event.type == KEYDOWN and event.key == K_l: # loading a level from file
        		if (sys.version_info > (3, 0)):  # Python 3 code in this block
        			file_path = filedialog.askopenfilename(title='Select level file (.json):', defaultextension = '.json', filetypes = [('level files', '.json')])
        		else: # Python 2
        			file_path = tkFileDialog.askopenfilename(title='Select level file (.json):', defaultextension = '.json', filetypes = [('level files', '.json')])
        		if len(file_path) > 0:
        			self.level = level_data.LevelData(path=file_path)
        			print('Loaded level: %d by %d tiles'%(default_map_size[0],default_map_size[1]))
        			self.reset_mainwindowsurf()
        			self.reset_userdata()
        	if event.type == KEYDOWN and event.key == K_DOWN:
        		self.draw_type = self.draw_type + 1
        		if self.draw_type == self.npal_x*self.npal_y:
        			self.draw_type = -1
        	if event.type == KEYDOWN and event.key == K_UP:
        		self.draw_type = self.draw_type - 1
        		if self.draw_type == -2:
        			self.draw_type = self.npal_x*self.npal_y-1
        	if event.type == KEYDOWN and event.key == K_o: # occupancy mode
        		if self.level == None:
        			continue
        		self.tilemode = 0
        	if event.type == KEYDOWN and event.key == K_b: # tile mode
        		if self.level == None:
        			continue
        		self.tilemode = 1
        	if event.type == KEYDOWN and event.key == K_f: # tile foreground mode
        		if self.level == None:
        			continue
        		self.tilemode = 2
        	if event.type == KEYDOWN and event.key == K_g: # toggle guides on/off
        		if self.level == None:
        			continue
        		if self.guides == True:
        			self.guides = False
        		else:
        			self.guides = True
        			AutoUpdateTileLayers
        	if event.type == KEYDOWN and event.key == K_a: # toggle guides on/off
        		self.AutoUpdateTileLayers()
        	if event.type == KEYDOWN and event.key == K_m:
        		if self.level == None:
        			continue
        		self.objectdrawtype = 'monsters'
        	if event.type == KEYDOWN and event.key == K_i:
        		if self.level == None:
        			continue
        		self.objectdrawtype = 'item'
        	if event.type == KEYDOWN and event.key == K_q:
        		if self.level == None:
        			continue
        		self.objectdrawtype = 'none'
        	elif event.type == MOUSEBUTTONDOWN:
        		if not self.level == None:
        			sx = self.mainwindowparams[0]
        			sy = self.mainwindowparams[1]
        			offx = self.mainwindowparams[2]
        			offy = self.mainwindowparams[3]
        			msx = self.level.data['tilemap']['size'][0]
        			msy = self.level.data['tilemap']['size'][1]
        			if (self.mouse_pos[0] > offx and self.mouse_pos[1] > offy and self.mouse_pos[0] < (offx+sx) and self.mouse_pos[1] < (offy+sy)):
        				coords = (int((self.mouse_pos[0]-offx)/self.tilesize), int((self.mouse_pos[1]-offy)/self.tilesize))
        				tile = msx*coords[1]+coords[0]
        				if coords[0] >= 0 and coords[0] < msx and coords[1] >= 0 and coords[1] < msy:
        					if self.objectdrawtype == 'none':
        						if self.tilemode == 0:
        							self.ToggleOcc(coords[0],coords[1])
        						elif self.tilemode == 1:
        							self.AssignBGTile(coords[0],coords[1],self.draw_type)
        						elif self.tilemode == 2:
        							self.AssignFGTile(coords[0],coords[1],self.draw_type)
        					elif self.objectdrawtype == 'item':
        						pass
        						#self.level.AssignItemLayer(coords[0],coords[1])
        		if (self.mouse_pos[0] > self.draw_offset_palette[0] and self.mouse_pos[1] < (self.draw_offset_palette[1]+self.npal_y*self.tilesize)):
        			coords = (int((self.mouse_pos[0]-self.draw_offset_palette[0])/self.tilesize), int((self.mouse_pos[1]-self.draw_offset_palette[1])/self.tilesize))
        			if coords[0] >= 0 and coords[0] < self.npal_x and coords[1] >= 0 and coords[1] < self.npal_y:
        				self.draw_type = int(coords[0]+self.npal_x*coords[1])
    
    def on_draw(self, screen):
        
        # Init background to black
        screen.blit(self.background, (0, 0))
        
        # Draw tilemap window data
        pygame.draw.rect(screen,(255,255,255), \
            pygame.Rect((self.draw_offset[0]-1,self.draw_offset[1]-1),(800+2,600+2)),1)
        pygame.draw.rect(screen,(0,0,0), \
            pygame.Rect((self.draw_offset[0],self.draw_offset[1]),(800,600)))
        
        # Draw palette
        screen.blit(self.palette, self.draw_offset_palette)
        if self.draw_type >= 0:
            pygame.draw.rect(screen,(255,0,0), \
                pygame.Rect((self.draw_offset_palette[0]+self.tilesize*(self.draw_type%self.npal_x),self.draw_offset_palette[1]+self.tilesize*(self.draw_type/self.npal_x)),(self.tilesize,self.tilesize)),1)
        
        if self.level == None:  # skip rest if no level loaded yet
        	return
        
        ts = self.tilesize
        msx = self.level.data['tilemap']['size'][0]
        msy = self.level.data['tilemap']['size'][1]
        
        ############################
        # Draw Main working window
        
        self.mainwindowsurf.fill((50, 50, 50))
        
        if self.tilemode == 0: # draw occ layer info
        	for i in range(msx):
        		for j in range(msy):
        			coords = [i*self.tilesize, j*self.tilesize]
        			occval = self.level.data['tilemap']['layerocc'][msx*j+i]
        			if occval == 0:
        				pygame.draw.rect(self.mainwindowsurf, (0,0,0), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
        			elif occval == 1:
        				pygame.draw.rect(self.mainwindowsurf, (255,255,255), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
        			elif occval == 2:
        				pygame.draw.rect(self.mainwindowsurf, (0,0,255), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
        
        elif self.tilemode == 1: # draw background and foreground tiles
        	for i in range(msx):
        		for j in range(msy):
        			coords = [i*self.tilesize, j*self.tilesize]
        			tileval = self.level.data['tilemap']['layer_b'][msx*j+i]
        			if tileval >= 0:
        				tilecoords = resources['tiles_coords'][tileval]
        				self.mainwindowsurf.blit(resources['tiles'], (coords[0],coords[1]), area=tilecoords)
        	for i in range(msx):
        		for j in range(msy):
        			coords = [i*self.tilesize, j*self.tilesize]
        			tileval = self.level.data['tilemap']['layer_f'][msx*j+i]
        			if tileval >= 0:
        				tilecoords = resources['tiles_coords'][tileval]
        				self.mainwindowsurf.blit(resources['tiles'], (coords[0],coords[1]), area=tilecoords)
        
        elif self.tilemode == 2: # draw foreground tiles
        	for i in range(msx):
        		for j in range(msy):
        			coords = [i*self.tilesize, j*self.tilesize]
        			tileval = self.level.data['tilemap']['layer_f'][msx*j+i]
        			if tileval >= 0:
        				tilecoords = resources['tiles_coords'][tileval]
        				self.mainwindowsurf.blit(resources['tiles'], (coords[0],coords[1]), area=tilecoords)
        
        # render window surf to main window
        sx = self.mainwindowparams[0]
        sy = self.mainwindowparams[1]
        offx = self.mainwindowparams[2]
        offy = self.mainwindowparams[3]
        pygame.draw.rect(screen,(50,50,50), pygame.Rect((offx-1,offy-1),(sx+2,sy+2)),1)
        screen.blit(self.mainwindowsurf, (offx,offy))
        
        if self.objectdrawtype == 'none':
        	if self.tilemode == 0:
        		screen.blit(resources['text_occ'],(sx/2,10))
        	elif self.tilemode == 1:
        		screen.blit(resources['text_bg'],(sx/2,10))
        	elif self.tilemode == 2:
        		screen.blit(resources['text_fg'],(sx/2,10))
        else:
        	if self.objectdrawtype == 'item':
        		screen.blit(resources['text_item'],(sx/2,10))
        
        # draw tile guides
        if self.guides == True:
        	for i in range(1, msx):
        		start_pos = (offx+i*ts,offy)
        		end_pos = (offx+i*ts,offy+msy*ts)
        		pygame.draw.line(screen, (255,0,0), start_pos, end_pos)
        	for i in range(1,msy):
        		start_pos = (offx,offy+i*ts)
        		end_pos = (offx+msx*ts,offy+i*ts)
        		pygame.draw.line(screen, (255,0,0), start_pos, end_pos)
        
        """
        if self.objectdrawtype == 'monsters':
            for i in range(self.level.map_size[0]):
                for j in range(self.level.map_size[1]):
                    coords = [self.draw_offset[0]+i*self.tilesize, self.draw_offset[1]+j*self.tilesize]
                    monsterval = self.level.monsterlayer[self.level.map_size[0]*j+i]
                    ind = monster_list.index(monsterval)
                    if ind == 1:
                        pygame.draw.rect(screen, (255,255,0), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
                    elif ind == 2:
                        pygame.draw.rect(screen, (0,255,255), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
                    elif ind == 3:
                        pygame.draw.rect(screen, (255,0,0), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
                    elif ind == 4:
                        pygame.draw.rect(screen, (0,0,255), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
                    elif ind == 5:
                        pygame.draw.rect(screen, (255,255,255), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
        elif self.objectdrawtype == 'item':
            for i in range(self.level.map_size[0]):
                for j in range(self.level.map_size[1]):
                    coords = [self.draw_offset[0]+i*self.tilesize, self.draw_offset[1]+j*self.tilesize]
                    itemval = self.level.itemlayer[self.level.map_size[0]*j+i]
                    ind = item_list.index(itemval)
                    if ind == 1:
                        pygame.draw.rect(screen, (255,0,0), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
                    elif ind == 2:
                        pygame.draw.rect(screen, (0,255,0), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
                    elif ind == 3:
                        pygame.draw.rect(screen, (0,0,255), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
                    elif ind == 4:
                        pygame.draw.rect(screen, (0,255,255), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
        elif self.objectdrawtype == 'trigger':
            for i in range(self.level.map_size[0]):
                for j in range(self.level.map_size[1]):
                    coords = [self.draw_offset[0]+i*self.tilesize, self.draw_offset[1]+j*self.tilesize]
                    triggerval = self.level.triggerlayer[self.level.map_size[0]*j+i]
                    ind = trigger_list.index(triggerval)
                    if ind == 1:
                        pygame.draw.rect(screen, (255,0,0), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
                    elif ind == 2:
                        pygame.draw.rect(screen, (0,255,0), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
                    elif ind == 3:
                        pygame.draw.rect(screen, (0,0,255), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
                    elif ind == 4:
                        pygame.draw.rect(screen, (0,255,255), pygame.Rect((coords[0],coords[1]),(self.tilesize,self.tilesize)))
         """

