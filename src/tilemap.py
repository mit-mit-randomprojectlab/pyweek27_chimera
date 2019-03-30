#!/usr/bin/python

"""
tilemap.py: classes for tilemap and environment
"""

from builtins import range

import os
import pygame
from pygame.locals import *
from gamedirector import *
from math import *
import random

import heapq

import resources
import guards

# Passage: a class for both doors and breakable walls, which share similar behaviours
class Passage(object):
	def __init__(self,parent,type,tile,state='closed'):
		self.parent = parent
		self.type = type # door1, door2, ... , breakable
		self.tile = tile
		self.state = state
	
	def Open(self):
		self.ChangeState('open')
	
	def Close(self):
		self.ChangeState('closed')
	
	def ChangeState(self, newstate):
		if not self.state == newstate:
			if 'door' in self.type:
				resources.soundfx['door'].play()
			else:
				resources.soundfx['break'].play()
		self.state = newstate
		if newstate == 'open':
			if 'door' in self.type:
				newtile1 = 41
				newtile2 = 31
			else:
				newtile1 = -1
				newtile2 = -1
			newocc = 0
		else: # closed
			if 'door' in self.type:
				if len(self.type) == 4: # just 'door'
					newtile1 = 40
					newtile2 = 30
				else:
					num = int(self.type[4])
					newtile1 = 60+num-1
					newtile2 = 50+num-1
			newocc = 1
		t = self.tile-self.parent.tiledlayers.map_size[0]
		self.parent.tiledlayers.UpdateTileLayer(self.tile, 1, newtile1)
		self.parent.tiledlayers.UpdateTileLayer(self.tile-self.parent.tiledlayers.map_size[0], 2, newtile2)
		self.parent.tiledlayers.occlayer[self.tile] = newocc

class Button(object):
	def __init__(self,parent,type,tile):
		self.parent = parent
		self.type = type
		self.tile = tile
		self.state = False
		self.statechange_callback = None
	
	def Update(self):
		paststate = self.state
		cellids = [d.id for d in self.parent.tiledlayers.objectlayer[self.tile]]
		if any([(i in cellids) for i in [6,7,8,9,10,11,13]]): # players or guards
			self.state = True
		else:
			self.state = False
		if not paststate == self.state: # update tile image data
			if self.type == 'yellow':
				newtile = 8
			if self.type == 'red':
				newtile = 18
			if self.type == 'blue':
				newtile = 28
			if self.state == True:
				newtile += 1
			self.parent.tiledlayers.UpdateTileLayer(self.tile, 1, newtile)
			if not self.statechange_callback == None:
				self.statechange_callback(self)
			resources.soundfx['button'].play()

class Item(object):
	def __init__(self,parent,id,tile):
		self.parent = parent
		self.id = id
		self.tile = tile
		ts = self.parent.tiledlayers.tilesize
		msx = self.parent.tiledlayers.map_size[0]
		self.x = ts*(tile%msx)+int(ts/2)
		self.y = ts*int(tile/msx)+int(ts/2)
		self.parent.tiledlayers.InsertObj(tile,self)
		self.active = True
		self.flying = False
	
	def Pickup(self):
		self.active = False
		self.parent.tiledlayers.RemoveObj(self.tile,self)
	
	def Throw(self,x,y,vx,vy):
		self.flying = True
		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy
		self.to = 10
	
	def Update(self):
		if not self.flying:
			return
		self.x += self.vx
		self.y += self.vy
		(self.x,self.y) = self.parent.tiledlayers.HandleObjectWallCollision((self.x,self.y),(24,24),(self.vx,self.vy),occtype='fly')
		self.to -= 1
		if self.to == 0:
			self.flying = False
			self.active = True
			ts = self.parent.tiledlayers.tilesize
			self.tile = self.parent.tiledlayers.map_size[0]*int(self.y/ts)+int(self.x/ts)
			self.parent.tiledlayers.InsertObj(self.tile,self)
	
	def Draw(self,screen):
		if self.active or self.flying:
			tilecoords = resources.itemsprites_coords[self.id]
			screen.blit(resources.itemsprites, (self.x-16-self.parent.camera.x+int(self.parent.camera.w_view/2),self.y-16-self.parent.camera.y+int(self.parent.camera.h_view/2)), area=tilecoords)

class Planner(object):
    def __init__(self,parent):
        self.maxsteps = 600
        (self.w, self.h) = parent.map_size
        self.tilesize = parent.tilesize
        self.h_occlayer = parent.occlayer
        self.pn = 0
        self.touched = [0 for i in range(self.w*self.h)]
        self.cost_so_far = [0 for i in range(self.w*self.h)]
        self.came_from = [0 for i in range(self.w*self.h)]
    
    def getneighbours(self, i):
        neighbours = []
        x = i%self.w
        y = i/self.w
        cost = 1
        costd = sqrt(2)
        if x > 0 and not self.h_occlayer[i-1]:
            neighbours.append((i-1,cost))
            if y > 0 and not self.h_occlayer[i-self.w] and not self.h_occlayer[i-self.w-1]:
                neighbours.append((i-self.w-1,costd))
            if y < (self.h-1) and not self.h_occlayer[i+self.w] and not self.h_occlayer[i+self.w-1]:
                neighbours.append((i+self.w-1,costd))
        if x < (self.w-1) and not self.h_occlayer[i+1]:
            neighbours.append((i+1,cost))
            if y > 0 and not self.h_occlayer[i-self.w] and not self.h_occlayer[i-self.w+1]:
                neighbours.append((i-self.w+1,costd))
            if y < (self.h-1) and not self.h_occlayer[i+self.w] and not self.h_occlayer[i+self.w+1]:
                neighbours.append((i+self.w+1,costd))
        if y > 0 and not self.h_occlayer[i-self.w]:
            neighbours.append((i-self.w,cost))
        if y < (self.h-1) and not self.h_occlayer[i+self.w]:
            neighbours.append((i+self.w,cost))
        return neighbours
    
    def heuristic(self,i,j):
        xi = i%self.w
        yi = i/self.w
        xj = j%self.w
        yj = j/self.w
        return abs(xi - xj) + abs(yi - yj)
    
    def astar_path(self, start, goal):
        if self.h_occlayer[goal]: # goal is an obstacle
            return []
        self.pn += 1
        frontier = []
        heapq.heappush(frontier, (0, start))
        self.touched[start] = self.pn
        self.cost_so_far[start] = 0
        self.came_from[start] = None
        
        nsteps = 0
        
        while True:
            nsteps += 1
            if len(frontier) == 0: # ran out of options, no path
                #return None
                return []
            current = heapq.heappop(frontier)[1]
            
            if nsteps == self.maxsteps: # tried too hard
                return []
            
            if current == goal:  # got it
                path = [current]
                while not self.came_from[current] == None: # step backwards through came froms to get path
                    current = self.came_from[current]
                    path.insert(0,current)
                return path
            
            for next in self.getneighbours(current):
                new_cost = self.cost_so_far[current] + next[1]
                if self.touched[next[0]] < self.pn or new_cost < self.cost_so_far[next[0]]:
                    self.touched[next[0]] = self.pn
                    self.cost_so_far[next[0]] = new_cost
                    priority = new_cost + self.heuristic(goal, next[0])
                    heapq.heappush(frontier, (priority, next[0]))
                    self.came_from[next[0]] = current

class TiledLayers(object):
    def __init__(self,parent):
        self.parent = parent
    
    def init_level(self, level_id):
        
        self.level_id = level_id
        self.map_size = resources.levels[level_id].data['tilemap']['size'][:]
        self.tilesize = 32
        self.tilelayer_bg = resources.levels[level_id].data['tilemap']['layer_b'][:]
        self.tilelayer_mg = resources.levels[level_id].data['tilemap']['layer_m'][:]
        self.tilelayer_fg = resources.levels[level_id].data['tilemap']['layer_f'][:]
        self.occlayer = resources.levels[level_id].data['tilemap']['layerocc'][:]
        self.spawnlayer = resources.levels[level_id].data['tilemap']['layerspawn'][:]
        
        self.objectlayer = [[] for i in range(self.map_size[0]*self.map_size[1])]
        self.exiting = False
        self.players_safe = []
        
        # send initial data to camera
        if self.map_size[0] <= 25:
        	self.parent.camera.xlim = 25*self.tilesize
        else:
        	self.parent.camera.xlim = self.map_size[0]*self.tilesize
        if self.map_size[0] <= 19:
        	self.parent.camera.ylim = 19*self.tilesize
        else:
        	self.parent.camera.ylim = self.map_size[1]*self.tilesize
        
        # Spawnlayer data:
        # 0-5 = key, 6-11 = player, 13 = guard, 14 = sword, 15 = hammer, 16 = duck, 17 = cake
        
        # set player start tiles from spawn layer
        self.player_start_tiles = []
        self.player_ids = []
        for i in range(6):
        	try:
        		tile = self.spawnlayer.index(i+6) # 6-11 are players
        		self.player_ids.append(i+6)
        		self.player_start_tiles.append(tile)
        	except:
        		pass
        
        # check for items in spawn layer
        item_tiles = [i for i, x in enumerate(self.spawnlayer) if x in [0,1,2,3,4,5,14,15,16,17]]
        self.items = []
        for tile in item_tiles:
        	self.items.append(Item(self.parent,self.spawnlayer[tile],tile))
        
        # get goal tiles from occlayer
        self.finish_tiles = [i for i, x in enumerate(self.occlayer) if x == 2]
        
        # fix up occlayer to have zeros, now player end data extracted
        inds = [i for i, x in enumerate(self.occlayer) if x < 0]
        for i in inds:
        	self.occlayer[i] = 0
        
        # create occlayer for flying items, discounts fences as occupied
        self.occlayerfly = self.occlayer[:]
        fixtiles = [i for i, x in enumerate(self.tilelayer_mg) if x in [16,17]]
        for tile in fixtiles:
        	self.occlayerfly[tile] = 0
        
        # Initialise player data and load into object layer
        for i in range(len(self.player_ids)):
        	tile = self.player_start_tiles[i]
        	playerx = self.tilesize*(tile%self.map_size[0])+int(self.tilesize/2)
        	playery = self.tilesize*int(tile/self.map_size[0])+int(self.tilesize/2)
        	self.parent.inmates[i].x = playerx
        	self.parent.inmates[i].y = playery
        	self.parent.inmates[i].id = self.player_ids[i]
        	self.InsertObj(tile,self.parent.inmates[i])
        
        # Initialise passages (doors and breakable walls)
        self.passages = []
        passage_tiles = [22,40,41,60,61,62,63,64,65]
        passage_names = ['break','door','dooropen','door1','door2','door3','door4','door5','door6']
        for tile in range(len(self.spawnlayer)):
        	if self.tilelayer_mg[tile] in passage_tiles:
        		ind = passage_tiles.index(self.tilelayer_mg[tile])
        		type = passage_names[ind]
        		if type == 'dooropen':
        			type = 'door'
        			state = 'open'
        		else:
        			state = 'closed'
        		#print('new door: ',type,tile,state)
        		self.passages.append(Passage(self.parent,type,tile,state=state))
        
        # Initialise buttons
        self.buttons = []
        button_tiles = [8,18,28]
        button_names = ['yellow','red','blue']
        for tile in range(len(self.spawnlayer)):
        	if self.tilelayer_mg[tile] in button_tiles:
        		ind = button_tiles.index(self.tilelayer_mg[tile])
        		type = button_names[ind]
        		#print('new button: ',type,tile)
        		self.buttons.append(Button(self.parent,type,tile))
        
        # Create planning service
        self.planner = Planner(self)
        
        # Load guards
        guard_tiles = [i for i, x in enumerate(self.spawnlayer) if x in [13]]
        self.guards = []
        for tile in guard_tiles:
        	self.guards.append(guards.Guard(self.parent,tile))
        
        self.gui_tick = 0
        self.watertile_ind = 0
        
        # retrieve list of tiles for static animations (water)
        self.water_tiles = []
        self.water_tiles.append([i for i, x in enumerate(self.tilelayer_bg) if x in resources.water_animation_tiles[0]])
        self.water_tiles.append([i for i, x in enumerate(self.tilelayer_bg) if x in resources.water_animation_tiles[1]])
        self.water_tiles.append([i for i, x in enumerate(self.tilelayer_bg) if x in resources.water_animation_tiles[2]])
        
        # render tiled layers
        self.bglayer = pygame.Surface((self.tilesize*self.map_size[0],self.tilesize*self.map_size[1]))
        self.bglayer.fill((255,0,255))
        self.bglayer.convert()
        self.bglayer.set_colorkey((255,0,255))
        self.fglayer = pygame.Surface((self.tilesize*self.map_size[0],self.tilesize*self.map_size[1]))
        self.fglayer.fill((255,0,255))
        self.fglayer.convert()
        self.fglayer.set_colorkey((255,0,255))
        for i in range(self.map_size[0]):
            for j in range(self.map_size[1]):
                coords = [i*self.tilesize, j*self.tilesize]
                tilevalbg = self.tilelayer_bg[self.map_size[0]*j+i]
                tilevalmg = self.tilelayer_mg[self.map_size[0]*j+i]
                tilevalfg = self.tilelayer_fg[self.map_size[0]*j+i]
                if tilevalbg >= 0:
                    tilecoords = resources.tiles_coords[tilevalbg]
                    self.bglayer.blit(resources.tiles, (coords[0],coords[1]), area=tilecoords)
                if tilevalmg >= 0: # mid-ground layer gets rendered on top of background layer
                    tilecoords = resources.tiles_coords[tilevalmg]
                    self.bglayer.blit(resources.tiles, (coords[0],coords[1]), area=tilecoords)
                if tilevalfg >= 0:
                    tilecoords = resources.tiles_coords[tilevalfg]
                    self.fglayer.blit(resources.tiles, (coords[0],coords[1]), area=tilecoords)
    
    def UpdateTileMapEntities(self): # update routine called by main game loop
    	for button in self.buttons:
    		button.Update()
    	for item in self.items:
    		item.Update()
    	for guard in self.guards:
    		guard.UpdateMotion()
    	self.gui_tick += 1
    	if self.gui_tick % 10 == 0:
    		self.watertile_ind = (self.watertile_ind+1) % 4
    		for tile in self.water_tiles[0]:
    			self.tilelayer_bg[tile] = resources.water_animation_tiles[0][self.watertile_ind]
    			self.UpdateTileBGAni(tile)
    		for tile in self.water_tiles[1]:
    			self.tilelayer_bg[tile] = resources.water_animation_tiles[1][self.watertile_ind]
    			self.UpdateTileBGAni(tile)
    		for tile in self.water_tiles[2]:
    			self.tilelayer_bg[tile] = resources.water_animation_tiles[2][self.watertile_ind]
    			self.UpdateTileBGAni(tile)
    			
    def UpdateTileBGAni(self, tile): # layer: 1: mid, 2: fore
    	coords = [(tile%self.map_size[0])*self.tilesize, int(tile/self.map_size[0])*self.tilesize]
    	tilecoords = resources.tiles_coords[self.tilelayer_bg[tile]]
    	self.bglayer.blit(resources.tiles, (coords[0],coords[1]), area=tilecoords)
    	if self.tilelayer_mg[tile] > 0: # also re-render mid-ground into this layer
    		tilecoords = resources.tiles_coords[self.tilelayer_mg[tile]]
    		self.bglayer.blit(resources.tiles, (coords[0],coords[1]), area=tilecoords)
    
    def UpdateTileLayer(self, tile, layer, tileval): # layer: 1: mid, 2: fore
    	coords = [(tile%self.map_size[0])*self.tilesize, int(tile/self.map_size[0])*self.tilesize]
    	if layer == 2:
    		self.fglayer.blit(resources.purpletile, (coords[0],coords[1])) # blit with transparency
    		if tileval >= 0:
    			tilecoords = resources.tiles_coords[tileval]
    			self.fglayer.blit(resources.tiles, (coords[0],coords[1]), area=tilecoords)
    	if layer == 1:
    		tilevalbg = self.tilelayer_bg[tile]
    		tilecoordsbg = resources.tiles_coords[tilevalbg]
    		self.bglayer.blit(resources.tiles, (coords[0],coords[1]), area=tilecoordsbg) # re-blit background first
    		if tileval >= 0:
    			tilecoords = resources.tiles_coords[tileval]
    			self.bglayer.blit(resources.tiles, (coords[0],coords[1]), area=tilecoords)
    
    def RenderBGLayer(self, screen):
        screen.blit(self.bglayer, (0,0), area=(self.parent.camera.x-self.parent.camera.w_view/2, self.parent.camera.y-self.parent.camera.h_view/2, self.parent.camera.w_view, self.parent.camera.h_view))
    
    def RenderFGLayer(self, screen):
        screen.blit(self.fglayer, (0,0), area=(self.parent.camera.x-self.parent.camera.w_view/2, self.parent.camera.y-self.parent.camera.h_view/2, self.parent.camera.w_view, self.parent.camera.h_view))
    
    def RenderGoalTiles(self, screen):
        for tile in self.finish_tiles:
            x = self.tilesize*(tile%self.map_size[0])
            y = self.tilesize*int(tile/self.map_size[0]) - 16 - 4*int((self.gui_tick % 30)/15)
            screen.blit(resources.guisprites, (x-self.parent.camera.x+int(self.parent.camera.w_view/2),y-self.parent.camera.y+int(self.parent.camera.h_view/2)), area=resources.guisprites_coords[2])
    
    def InsertObj(self,tileind,obj):
        self.objectlayer[tileind].append(obj)
        if obj.id in [6,7,8,9,10,11] and tileind in self.finish_tiles:
            self.players_safe.append(obj.id)
            if len(self.players_safe) == len(self.player_ids):
            	self.exiting = True
    
    def RemoveObj(self,tileind,obj):
        if obj in self.objectlayer[tileind]:
            self.objectlayer[tileind].pop(self.objectlayer[tileind].index(obj))
            if obj.id in [6,7,8,9,10,11] and tileind in self.finish_tiles: # TODO: fix up for recording all inmates get to end?
            	self.players_safe.remove(obj.id)
    
    def UpdateObj(self,tileind_old,tileind_new,obj):
        self.RemoveObj(tileind_old,obj)
        self.InsertObj(tileind_new,obj)
    
    def HandleObjectWallCollision(self,objpos,objsize,objmovevec,occtype='normal'):
        
        if occtype == 'normal':
        	occlayer = self.occlayer
        elif occtype == 'fly':
        	occlayer = self.occlayerfly
        
        x = objpos[0]
        y = objpos[1]
        vx = objmovevec[0]
        vy = objmovevec[1]
        sx = objsize[0]
        sy = objsize[1]
        ts = self.tilesize
        
        tileocc_ul = self.map_size[0]*int((y-int(sy/2))/ts)+int((x-int(sx/2))/ts)
        tileocc_ur = self.map_size[0]*int((y-int(sy/2))/ts)+int((x+int(sx/2))/ts)
        tileocc_ll = self.map_size[0]*int((y+int(sy/2))/ts)+int((x-int(sx/2))/ts)
        tileocc_lr = self.map_size[0]*int((y+int(sy/2))/ts)+int((x+int(sx/2))/ts)
        
        tileocc_u = self.map_size[0]*int((y-int(sy/2))/ts)+int(x/ts)
        tileocc_d = self.map_size[0]*int((y+int(sy/2))/ts)+int(x/ts)
        tileocc_l = self.map_size[0]*int(y/ts)+int((x-(sx/2))/ts)
        tileocc_r = self.map_size[0]*int(y/ts)+int((x+(sx/2))/ts)
        
        if vx > 0 and vy == 0: # handle lateral/longitudinal collisions
            if occlayer[tileocc_ur] or occlayer[tileocc_lr] or occlayer[tileocc_r]:
                x = ts*(tileocc_ur % self.map_size[0]) - 1 - int(sx/2)
        elif vx < 0 and vy == 0:
            if occlayer[tileocc_ul] or occlayer[tileocc_ll] or occlayer[tileocc_l]:
                x = ts*(tileocc_ul % self.map_size[0]) + 1 + int(sx/2) + ts
        elif vx == 0 and vy > 0:
            if occlayer[tileocc_lr] or occlayer[tileocc_ll] or occlayer[tileocc_d]:
                y = ts*int(tileocc_ll/self.map_size[0]) - 1 - int(sy/2)
        elif vx == 0 and vy < 0:
            if occlayer[tileocc_ul] or occlayer[tileocc_ur] or occlayer[tileocc_u]:
                y = ts*int(tileocc_ul/self.map_size[0]) + 1 + int(sy/2) + ts
        elif vx > 0 and vy < 0: # handle corner cases
            xref = ts*(tileocc_ur % self.map_size[0]) - 1 - int(sx/2)
            yref = ts*int(tileocc_ur/self.map_size[0]) + 1 + int(sy/2) + ts
            if occlayer[tileocc_ul] and occlayer[tileocc_lr]:
                x = xref
                y = yref
            elif occlayer[tileocc_ul]:
                y = yref
            elif occlayer[tileocc_lr]:
                x = xref
            elif occlayer[tileocc_ur]:
                if fabs(x-xref) < fabs(y-yref) or occlayer[tileocc_ur+self.map_size[0]]:
                    x = xref
                else:
                    y = yref
        elif vx > 0 and vy > 0:
            xref = ts*(tileocc_lr % self.map_size[0]) - 1 - int(sx/2)
            yref = ts*int(tileocc_lr/self.map_size[0]) - 1 - int(sy/2)
            if occlayer[tileocc_ll] and occlayer[tileocc_ur]:
                x = xref
                y = yref
            elif occlayer[tileocc_ll]:
                y = yref
            elif occlayer[tileocc_ur]:
                x = xref
            elif occlayer[tileocc_lr]:
                if fabs(x-xref) < fabs(y-yref) or occlayer[tileocc_lr-self.map_size[0]]:
                    x = xref
                else:
                    y = yref
        elif vx < 0 and vy > 0:
            xref = ts*(tileocc_ll % self.map_size[0]) + 1 + int(sx/2) + ts
            yref = ts*int(tileocc_ll/self.map_size[0]) - 1 - int(sy/2)
            if occlayer[tileocc_ul] and occlayer[tileocc_lr]:
                x = xref
                y = yref
            elif occlayer[tileocc_lr]:
                y = yref
            elif occlayer[tileocc_ul]:
                x = xref
            elif occlayer[tileocc_ll]:
                if fabs(x-xref) < fabs(y-yref) or occlayer[tileocc_ll-self.map_size[0]]:
                    x = xref
                else:
                    y = yref
        elif vx < 0 and vy < 0:
            xref = ts*(tileocc_ul % self.map_size[0]) + 1 + int(sx/2) + ts
            yref = ts*int(tileocc_ul/self.map_size[0]) + 1 + int(sy/2) + ts
            if occlayer[tileocc_ur] and occlayer[tileocc_ll]:
                x = xref
                y = yref
            elif occlayer[tileocc_ur]:
                y = yref
            elif occlayer[tileocc_ll]:
                x = xref
            elif occlayer[tileocc_ul]:
                if fabs(x-xref) < fabs(y-yref) or occlayer[tileocc_ul+self.map_size[0]]:
                    x = xref
                else:
                    y = yref
        
        return (x,y)
    