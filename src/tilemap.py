#!/usr/bin/python

"""
tilemap.py: classes for tilemap and environment
"""

import os
import pygame
from pygame.locals import *
from gamedirector import *
from math import *
import random

import resources

class TiledLayers(object):
    def __init__(self,parent):
        self.parent = parent
    
    def init_level(self, level_id):
        
        self.level_id = level_id
        self.map_size = resources.levels[level_id].data['tilemap']['size'][:]
        self.tilesize = 32
        self.player_start_tile = 33 # for now until in level data
        self.finish_tile = 32*32 # for now until in level data
        self.tilelayer_bg = resources.levels[level_id].data['tilemap']['layer_b'][:]
        self.tilelayer_mg = resources.levels[level_id].data['tilemap']['layer_m'][:]
        self.tilelayer_fg = resources.levels[level_id].data['tilemap']['layer_f'][:]
        self.occlayer = resources.levels[level_id].data['tilemap']['layerocc'][:]
        
        self.objectlayer = [[] for i in range(self.map_size[0]*self.map_size[1])]
        self.exiting = False
        
        # send initial data to camera
        if self.map_size[0] <= 25:
        	self.parent.camera.xlim = 25*self.tilesize
        else:
        	self.parent.camera.xlim = self.map_size[0]*self.tilesize
        if self.map_size[0] <= 19:
        	self.parent.camera.ylim = 19*self.tilesize
        else:
        	self.parent.camera.ylim = self.map_size[1]*self.tilesize
        
        # Initialise player data and load into object layer
        playerx = self.tilesize*(self.player_start_tile%self.map_size[0])+self.tilesize/2
        playery = self.tilesize*int(self.player_start_tile/self.map_size[0])+self.tilesize/2
        self.parent.player.x = playerx
        self.parent.player.y = playery
        self.InsertObj(self.player_start_tile,0)
        
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
        
    def UpdateTileLayer(self, tile, tileval):
        coords = [(tile%self.map_size[0])*self.tilesize, int(tile/self.map_size[0])*self.tilesize]
        if tileval >= 0:
            tilecoords = resources.tiles_coords[tileval]
            self.bglayer.blit(resources.tiles, (coords[0],coords[1]), area=tilecoords)
    
    def RenderBGLayer(self, screen):
        screen.blit(self.bglayer, (0,0), area=(self.parent.camera.x-self.parent.camera.w_view/2, self.parent.camera.y-self.parent.camera.h_view/2, self.parent.camera.w_view, self.parent.camera.h_view))
    
    def RenderFGLayer(self, screen):
        screen.blit(self.fglayer, (0,0), area=(self.parent.camera.x-self.parent.camera.w_view/2, self.parent.camera.y-self.parent.camera.h_view/2, self.parent.camera.w_view, self.parent.camera.h_view))
    
    def InsertObj(self,tileind,objid):
        self.objectlayer[tileind].append(objid)
        if objid == 0 and tileind == self.finish_tile:
            self.exiting = True
    
    def RemoveObj(self,tileind,objid):
        if objid in self.objectlayer[tileind]:
            self.objectlayer[tileind].pop(self.objectlayer[tileind].index(objid))
    
    def UpdateObj(self,tileind_old,tileind_new,objid):
        self.RemoveObj(tileind_old,objid)
        self.InsertObj(tileind_new,objid)
    
    def HandleObjectWallCollision(self,objpos,objsize,objmovevec):
        
        x = objpos[0]
        y = objpos[1]
        vx = objmovevec[0]
        vy = objmovevec[1]
        sx = objsize[0]
        sy = objsize[1]
        ts = self.tilesize
        
        tileocc_ul = int(self.map_size[0]*((y-(sy/2))/ts)+((x-(sx/2))/ts))
        tileocc_ur = int(self.map_size[0]*((y-(sy/2))/ts)+((x+(sx/2))/ts))
        tileocc_ll = int(self.map_size[0]*((y+(sy/2))/ts)+((x-(sx/2))/ts))
        tileocc_lr = int(self.map_size[0]*((y+(sy/2))/ts)+((x+(sx/2))/ts))
        
        tileocc_u = int(self.map_size[0]*((y-(sy/2))/ts)+(x/ts))
        tileocc_d = int(self.map_size[0]*((y+(sy/2))/ts)+(x/ts))
        tileocc_l = int(self.map_size[0]*(y/ts)+((x-(sx/2))/ts))
        tileocc_r = int(self.map_size[0]*(y/ts)+((x+(sx/2))/ts))
        
        if vx > 0 and vy == 0: # handle lateral/longitudinal collisions
            if self.occlayer[tileocc_ur] or self.occlayer[tileocc_lr] or self.occlayer[tileocc_r]:
                x = ts*(tileocc_ur % self.map_size[0]) - 1 - sx/2
        elif vx < 0 and vy == 0:
            if self.occlayer[tileocc_ul] or self.occlayer[tileocc_ll] or self.occlayer[tileocc_l]:
                x = ts*(tileocc_ul % self.map_size[0]) + 1 + sx/2 + ts
        elif vx == 0 and vy > 0:
            if self.occlayer[tileocc_lr] or self.occlayer[tileocc_ll] or self.occlayer[tileocc_d]:
                y = ts*(tileocc_ll/self.map_size[0]) - 1 - sy/2
        elif vx == 0 and vy < 0:
            if self.occlayer[tileocc_ul] or self.occlayer[tileocc_ur] or self.occlayer[tileocc_u]:
                y = ts*(tileocc_ul/self.map_size[0]) + 1 + sy/2 + ts
        elif vx > 0 and vy < 0: # handle corner cases
            xref = ts*(tileocc_ur % self.map_size[0]) - 1 - sx/2
            yref = ts*(tileocc_ur/self.map_size[0]) + 1 + sy/2 + ts
            if self.occlayer[tileocc_ul] and self.occlayer[tileocc_lr]:
                x = xref
                y = yref
            elif self.occlayer[tileocc_ul]:
                y = yref
            elif self.occlayer[tileocc_lr]:
                x = xref
            elif self.occlayer[tileocc_ur]:
                if fabs(x-xref) < fabs(y-yref) or self.occlayer[tileocc_ur+self.map_size[0]]:
                    x = xref
                else:
                    y = yref
        elif vx > 0 and vy > 0:
            xref = ts*(tileocc_lr % self.map_size[0]) - 1 - sx/2
            yref = ts*(tileocc_lr/self.map_size[0]) - 1 - sy/2
            if self.occlayer[tileocc_ll] and self.occlayer[tileocc_ur]:
                x = xref
                y = yref
            elif self.occlayer[tileocc_ll]:
                y = yref
            elif self.occlayer[tileocc_ur]:
                x = xref
            elif self.occlayer[tileocc_lr]:
                if fabs(x-xref) < fabs(y-yref) or self.occlayer[tileocc_lr-self.map_size[0]]:
                    x = xref
                else:
                    y = yref
        elif vx < 0 and vy > 0:
            xref = ts*(tileocc_ll % self.map_size[0]) + 1 + sx/2 + ts
            yref = ts*(tileocc_ll/self.map_size[0]) - 1 - sy/2
            if self.occlayer[tileocc_ul] and self.occlayer[tileocc_lr]:
                x = xref
                y = yref
            elif self.occlayer[tileocc_lr]:
                y = yref
            elif self.occlayer[tileocc_ul]:
                x = xref
            elif self.occlayer[tileocc_ll]:
                if fabs(x-xref) < fabs(y-yref) or self.occlayer[tileocc_ll-self.map_size[0]]:
                    x = xref
                else:
                    y = yref
        elif vx < 0 and vy < 0:
            xref = ts*(tileocc_ul % self.map_size[0]) + 1 + sx/2 + ts
            yref = ts*(tileocc_ul/self.map_size[0]) + 1 + sy/2 + ts
            if self.occlayer[tileocc_ur] and self.occlayer[tileocc_ll]:
                x = xref
                y = yref
            elif self.occlayer[tileocc_ur]:
                y = yref
            elif self.occlayer[tileocc_ll]:
                x = xref
            elif self.occlayer[tileocc_ul]:
                if fabs(x-xref) < fabs(y-yref) or self.occlayer[tileocc_ul+self.map_size[0]]:
                    x = xref
                else:
                    y = yref
        
        return (x,y)
    