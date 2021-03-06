#!/usr/bin/python

"""
level_editor.py: GUI for creating/editing level data
"""

from builtins import range

import os, sys
import pygame
from pygame.locals import *
from gamedirector import *

# start - up hidden Tkinter for using file open/save dialog
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

item_list = [None, 'key', 'ducky']

# Load in resources
resources = {}
def init_resources(mainpath):
	load_spritesheet('tiles', mainpath, 'tileset_1x.png', (255, 0, 255), 10, 14)
	load_spritesheet('items', mainpath, 'items_1x.png', (255, 0, 255), 6, 3)

	# Text data for draw modes
	resources['font'] = pygame.font.SysFont("arial", 12)
	resources['text_occ'] = resources['font'].render('Occupancy Mode', True, (255, 255, 255))
	resources['text_bg'] = resources['font'].render('Background Tile Mode', True, (255, 255, 255))
	resources['text_mg'] = resources['font'].render('Midground Tile Mode', True, (255, 255, 255))
	resources['text_fg'] = resources['font'].render('Foreground Tile Mode', True, (255, 255, 255))
	resources['text_item'] = resources['font'].render('Item Mode (q to quit back to tiles)', True, (255, 255, 255))

def load_spritesheet(name, mainpath, filename, color, w, h):
	resources[name] = pygame.image.load(os.path.join(mainpath, 'data', 'gfx', filename)).convert()
	resources[name].set_colorkey(color)
	resources[name + '_coords'] = []
	for j in range(h):
		for i in range(w):
			resources[name + '_coords'].append((i * 16, j * 16, 16, 16))
	resources[name + '_w'] = w
	resources[name + '_h'] = h


# Class for dialog to get map size for new map
default_map_size = [32, 32]
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
	screen_res = (1200, 700)

	window_title = "Level Editor: n/l/s (new/load/save), o (occupancy layer), b (background), m (midground), f (foreground), g (toggle guide lines), a (auto - tiler), i (spawn)"
	dir = GameDirector(window_title, screen_res, framerate)

	# Load resources
	init_resources(mainpath)

	# Load edior
	level_edit = LevelEditor(dir, screen_res)
	dir.addscene('level_edit', level_edit)

	# start up director
	dir.change_scene('level_edit', [])
	dir.loop()

class LevelEditor(GameScene):
	def __init__(self, director, window_size):
		super(LevelEditor, self).__init__(director)

		self.window_size = window_size
		self.background = pygame.Surface(window_size)
		self.background.fill((0, 0, 0))
		self.background.convert()

		self.mouse_pos = (0, 0)
		self.mouse_down = False
		self.draw_type =  - 1
		self.draw_type_item = 'null'
		self.tilemode = 0 # 0: occupancy, 1: bg, 2: mg, 3: fg
		self.objectdrawtype = 'none'
		self.tilesize = 16
		self.zoom = 0
		self.guides = False

		self.level = None

		self.palette = {}
		self.setPalette('tiles')
		self.setPalette('items')
		self.npal_x = self.palette['tiles_w']
		self.npal_y = self.palette['tiles_h']

		self.layer_key = ['layerocc', 'layer_b', 'layer_m', 'layer_f', 'layerspawn']
		self.draw_offset = (16, 32) # fix up
		self.tileNum = 0
		self.draw_offset_palette = (self.window_size[0] - self.tilesize - self.npal_x * self.tilesize, 2 * self.tilesize)
		self.draw_offset_palette = (2 * 16  +  800, 2 * 16)
		self.reset_userdata()
		self.SetAutoTileRules()

	def setPalette(self, name):
		self.palette[name + '_w'] = resources[name + '_w']
		self.palette[name + '_h'] = resources[name + '_h']
		self.palette[name] = pygame.Surface((self.palette[name + '_w'] * self.tilesize, self.palette[name + '_h'] * self.tilesize))
		self.palette[name].fill((0, 0, 0))
		self.palette[name].convert()
		for j in range(self.palette[name + '_h']):
			for i in range(self.palette[name + '_w']):
				self.palette[name].blit(resources[name], (i * self.tilesize, j * self.tilesize), area=resources[name + '_coords'][i + self.palette[name + '_w'] * j])

	def reset_mainwindowsurf(self):
		self.mainwindowsurf = pygame.Surface((self.level.data['tilemap']['size'][0] * self.tilesize, self.level.data['tilemap']['size'][1] * self.tilesize))
		self.mainwindowsurf.fill((0, 0, 0))
		self.mainwindowsurf.convert()

		sx = self.level.data['tilemap']['size'][0] * self.tilesize
		sy = self.level.data['tilemap']['size'][1] * self.tilesize
		offx = self.draw_offset[0] + 400 - sx/2
		offy = self.draw_offset[1] + 300 - sy/2

		self.mainwindowparams = [sx, sy, offx, offy]

	def reset_userdata(self):
		self.userdata = []

	def AssignTile(self, layer, x, y, value):
		if not isinstance(layer, str):
			layer = self.layer_key[layer]
		msx = self.level.data['tilemap']['size'][0]
		msy = self.level.data['tilemap']['size'][1]
		if x < 0 or x >= msx or y < 0 or y >= msy:
			return
		self.level.data['tilemap'][layer][msx * y + x] = value

	def GetTile(self, layer, x, y):
		if not isinstance(layer, str):
			layer = self.layer_key[layer]
		msx = self.level.data['tilemap']['size'][0]
		msy = self.level.data['tilemap']['size'][1]
		if x < 0 or x >= msx or y < 0 or y >= msy:
			return False
		return self.level.data['tilemap'][layer][msx * y + x]

	def ToggleOcc(self, i, j):
		msx = self.level.data['tilemap']['size'][0]
		msy = self.level.data['tilemap']['size'][1]
		if i < 0 or i >= msx or j < 0 or j >= msy:
			return
		self.level.data['tilemap']['layerocc'][msx * j + i] = self.level.data['tilemap']['layerocc'][int(msx * j + i)]  +  1
		if self.level.data['tilemap']['layerocc'][msx * j + i] > 3:
			self.level.data['tilemap']['layerocc'][msx * j + i] = 0

	def SetOcc(self, x, y, value):
		msx = self.level.data['tilemap']['size'][0]
		msy = self.level.data['tilemap']['size'][1]
		if x < 0 or x >= msx or y < 0 or y >= msy:
			return
		self.level.data['tilemap']['layerocc'][msx * y + x] = self.level.data['tilemap']['layerocc'][int(msx * y + x)] = value

	# def AutoUpdateTileLayers(self):
	#     if self.level == None:
	#         return
	#     ts = self.tilesize
	#     msx = self.level.data['tilemap']['size'][0]
	#     msy = self.level.data['tilemap']['size'][1]
	#     layerocc = self.level.data['tilemap']['layerocc']
	#     layer_b = self.level.data['tilemap']['layer_b']
	#     layer_m = self.level.data['tilemap']['layer_m']
	#     layer_f = self.level.data['tilemap']['layer_f']
	#     for i in range(msx):
	#         for j in range(msy):
	#             if layerocc[msx * j + i] == 0:
	#                 self.AssignTile('layer_b', i, j, 26)
	#                 if j >= 1:
	#                     if layerocc[msx * (j - 1) + i] == 1:
	#                         self.AssignTile('layer_b', i, j, 36)
	#                     elif layerocc[msx * (j - 1) + i] == 2:
	#                         self.AssignTile('layer_b', i, j, 66)
	#             elif layerocc[msx * j + i] == 1:
	#                 self.AssignTile('layer_b', i, j, 10)
	#                 if j >= 1:
	#                     self.AssignTile('layer_f', i, j - 1, 1) # TODO: set based on connectivity to surrounds
	#             elif layerocc[msx * j + i] == 2:
	#                 self.AssignTile('layer_b', i, j, 26)
	#                 self.AssignTile('layer_m', i, j, 16)
	#                 if j >= 1:
	#                     self.AssignTile('layer_f', i, j - 1, 6) # TODO: set based on connectivity to surrounds

	def AutoUpdateTileLayers(self):
		if self.level == None:
			return
		msx = self.level.data['tilemap']['size'][0]
		msy = self.level.data['tilemap']['size'][1]
		for x in range(msx):
			for y in range(msy):
				for layer in range(1, 4):
					tile = self.GetTile(layer, x, y)
					if tile in self.AutoTileRules[layer]:
						for rule in self.AutoTileRules[layer][tile]:
							rule(x, y, tile)

	def SetAutoTileRules(self):
		door_tiles = list(range(40, 44)) + list(range(60, 67))
		wall_tiles = [10, 11, 12, 13, 20, 21, 22]
		wall_tiles += door_tiles
		unshaded_floor = [26, 27]

		self.AutoTileRules = {}
		for layer in range(1, 4):
			self.AutoTileRules[layer] = {}

		def is_wall(x, y):
			return (self.GetTile(2, x, y) in wall_tiles)

		def add_rule(tiles, layer, rule):
			for t in tiles:
				if not t in self.AutoTileRules[layer]:
					 self.AutoTileRules[layer][t] = [rule]
				else:
					 self.AutoTileRules[layer][t].append(rule)

		# WALLS (just draw a standard wall)
		def wall_rule(x, y, tile):
			# Isn't covered by roof...
			if not is_wall(x, y + 1):
				wall_tile = tile
				if not is_wall(x - 1, y):
					wall_tile += 1
				if not is_wall(x + 1, y):
					wall_tile += 2
				self.AssignTile(2, x, y, wall_tile)
				# roof above
				floor = self.GetTile(1, x, y + 1)
				if floor in unshaded_floor:
					self.AssignTile(1, x, y + 1, floor + self.npal_x)
			# Add roof now!
			if self.GetTile(3, x, y - 1) == -1: # Don't overwrite anything

				roof_keys = {
					# Top/Bottom 0 = none, 1 = bottom, 2 = top, 3 = both
					0: {
						# Left/Right 0 = none, 1 = left, 2 = right, 3 = both
						0: 74,
						1: 34,
						2: 35,
						3: 0
					},
					1: {
						# Left/Right 0 = none, 1 = left, 2 = right, 3 = both
						0: 45,
						1: 24,
						2: 25,
						3: 4
					},
					2: {
						0: 44,
						1: 14,
						2: 15,
						3: 5
					},
					3: {
						0: 1,
						1: 2,
						2: 3,
						3: 23
					}
				}

				topbottom = 0
				if not is_wall(x, y + 1):
					topbottom += 1
				if not is_wall(x, y - 1):
					topbottom += 2
				leftright = 0
				if not is_wall(x - 1, y):
					leftright += 1
				if not is_wall(x + 1, y):
					leftright += 2
				roof_tile = roof_keys[topbottom][leftright]
				self.AssignTile(3, x, y - 1, roof_tile)

		add_rule([10], 2, wall_rule)

		# DOOR RULE (draw the bottom half of the door)
		def door_rule(x, y, tile):
			self.AssignTile(3, x, y - 1, tile - self.npal_x)
			floor = self.GetTile(1, x, y + 1)
			if floor in unshaded_floor:
				self.AssignTile(1, x, y + 1, floor + self.npal_x)
			floor = self.GetTile(1, x, y)
			if floor in unshaded_floor:
				self.AssignTile(1, x, y, floor + self.npal_x*2)
		add_rule(door_tiles, 2, door_rule)

		# FENCES (just draw the bottom half of the fence)
		def fence_rule(x, y, tile):
			if tile == 16:
				self.AssignTile(3, x, y - 1, tile - self.npal_x)
				floor = self.GetTile(1, x, y + 1)
				if floor in unshaded_floor:
					self.AssignTile(1, x, y + 1, floor + self.npal_x*4)
				floor = self.GetTile(1, x, y)
				if floor in unshaded_floor:
					self.AssignTile(1, x, y, floor + self.npal_x*2)
			elif tile == 17:
				if self.GetTile(2, x, y - 1) != 17:
					self.AssignTile(3, x, y - 1, tile - self.npal_x)
				floor = self.GetTile(1, x, y)
				if floor in unshaded_floor:
					self.AssignTile(1, x, y, floor + self.npal_x*5)
		add_rule([16, 17], 2, fence_rule)

		# BEDS (just draw the bottom left corner)
		def bed_rule(x, y, tile):
			self.AssignTile(2, x + 1, y, tile + 1)
			self.AssignTile(3, x, y - 1, tile - self.npal_x)
			self.AssignTile(3, x + 1, y - 1, tile - self.npal_x + 1)
		add_rule([48, 68, 88], 2, bed_rule)

		# CLOSETS AND STATUES
		def prop_rule(x, y, tile):
			self.AssignTile(3, x, y - 1, tile - self.npal_x)
		add_rule([96, 97, 118, 119], 2, prop_rule)

		# OCC RULE
		def occ_rule(x, y, tile):
			if tile == -1 or tile in [8, 18, 28]:
				self.SetOcc(x, y, 0)
			else:
				self.SetOcc(x, y, 1)
		all = list(range(-1, self.npal_x * self.npal_y))
		add_rule(all, 2, occ_rule)

	def on_switchto(self, switchtoargs):
		pass

	def on_update(self):
		self.mouse_pos = pygame.mouse.get_pos()
		if self.mouse_down:
			self.on_mousePress(fresh = False)
		#print self.mouse_pos

	def on_event(self, events):

		for event in events:
			if event.type == KEYDOWN:
				self.on_keyDown(event.key)
			elif event.type == MOUSEBUTTONDOWN:
				self.mouse_down = event.button
				self.on_mousePress(fresh = True)
			elif event.type == MOUSEBUTTONUP:
				self.mouse_down = False

	def on_keyDown(self, key):
		if key == K_n: # starting a new file
			d = MyDialog(root)
			root.wait_window(d.top)
			if d.newlvl_result == 1:
				self.level = level_data.LevelData(path=None, size=default_map_size)
				print('Created new level: %d by %d tiles'%(default_map_size[0], default_map_size[1]))
				self.reset_mainwindowsurf()
				self.reset_userdata()
		if key == K_s: # saving level to file
			if (sys.version_info > (3, 0)):  # Python 3 code in this block
				file_path = filedialog.asksaveasfilename(title='Save level file (.json):', defaultextension = '.json', filetypes = [('level files', '.json')])
			else: # Python 2
				file_path = tkFileDialog.asksaveasfilename(title='Save level file (.json):', defaultextension = '.json', filetypes = [('level files', '.json')])
			if len(file_path) > 0:
				self.level.SaveLevel(file_path)
				print('Saved level to %s'%(file_path))
		if key == K_l: # loading a level from file
			if (sys.version_info > (3, 0)):  # Python 3 code in this block
				file_path = filedialog.askopenfilename(title='Select level file (.json):', defaultextension = '.json', filetypes = [('level files', '.json')])
			else: # Python 2
				file_path = tkFileDialog.askopenfilename(title='Select level file (.json):', defaultextension = '.json', filetypes = [('level files', '.json')])
			if len(file_path) > 0:
				self.level = level_data.LevelData(path=file_path)
				print('Loaded level: %d by %d tiles'%(default_map_size[0], default_map_size[1]))
				self.reset_mainwindowsurf()
				self.reset_userdata()
		if key == K_DOWN:
			self.draw_type = self.draw_type  +  1
			if self.draw_type == self.npal_x * self.npal_y:
				self.draw_type =  - 1
		if key == K_UP:
			self.draw_type = self.draw_type  -  1
			if self.draw_type ==  - 2:
				self.draw_type = self.npal_x * self.npal_y - 1
		if key == K_o: # occupancy mode
			self.tilemode = 0
		if key == K_b: # bg tile mode
			self.tilemode = 1
		if key == K_m: # mg tile mode
			self.tilemode = 2
		if key == K_f: # tile foreground mode
			self.tilemode = 3
		if key == K_g: # toggle guides on/off
			if self.guides == True:
				self.guides = False
			else:
				self.guides = True
		if key == K_a: # toggle guides on/off
			self.AutoUpdateTileLayers()
		if key == K_i:
			self.tilemode = 4
			self.draw_type = 0
		if key == K_q:
			self.objectdrawtype = 'none'

	def on_mousePress(self, fresh = False):
		if not self.level == None:
			sx = self.mainwindowparams[0]
			sy = self.mainwindowparams[1]
			offx = self.mainwindowparams[2]
			offy = self.mainwindowparams[3]
			msx = self.level.data['tilemap']['size'][0]
			msy = self.level.data['tilemap']['size'][1]
			if (self.mouse_pos[0] > offx and self.mouse_pos[1] > offy and self.mouse_pos[0] < (offx + sx) and self.mouse_pos[1] < (offy + sy)):
				coords = (int((self.mouse_pos[0] - offx)/self.tilesize), int((self.mouse_pos[1] - offy)/self.tilesize))
				tile = msx * coords[1] + coords[0]
				self.tileNum = tile
				if coords[0] >= 0 and coords[0] < msx and coords[1] >= 0 and coords[1] < msy:
					if self.objectdrawtype == 'none':
						if self.tilemode == 0 and fresh:
							self.ToggleOcc(coords[0], coords[1])
						elif self.tilemode > 0:
							if self.mouse_down == 1:
								self.AssignTile(self.tilemode, coords[0], coords[1], self.draw_type)
							else:
								self.AssignTile(self.tilemode, coords[0], coords[1], -1)
					elif self.objectdrawtype == 'item':
						pass # TODO: add item support


		palette = 'tiles'
		if self.tilemode == 4:
			palette = 'items'
		pal_w = self.palette[palette + "_w"]
		pal_h = self.palette[palette + "_h"]
		if (self.mouse_pos[0] > self.draw_offset_palette[0] and self.mouse_pos[1] < (self.draw_offset_palette[1] + pal_h * self.tilesize)):
			coords = (int((self.mouse_pos[0] - self.draw_offset_palette[0])/self.tilesize), int((self.mouse_pos[1] - self.draw_offset_palette[1])/self.tilesize))
			if coords[0] >= 0 and coords[0] < pal_w and coords[1] >= 0 and coords[1] < pal_h:
				self.draw_type = coords[0] + pal_w * coords[1]

	def on_draw(self, screen):

		# Init background to black
		screen.blit(self.background, (0, 0))

		# Draw tilemap window data
		pygame.draw.rect(screen, (255, 255, 255), \
			pygame.Rect((self.draw_offset[0] - 1, self.draw_offset[1] - 1), (800 + 2, 600 + 2)), 1)
		pygame.draw.rect(screen, (0, 0, 0), \
			pygame.Rect((self.draw_offset[0], self.draw_offset[1]), (800, 600)))

		# Draw palette
		palette = 'tiles'
		if self.tilemode == 4:
			palette = 'items'
		pal_w = self.palette[palette + "_w"]
		pal_h = self.palette[palette + "_h"]

		screen.blit(self.palette[palette], self.draw_offset_palette)
		if self.draw_type >= 0:
			pygame.draw.rect(screen, (255, 0, 0), \
				pygame.Rect((self.draw_offset_palette[0] + self.tilesize * (self.draw_type%pal_w), self.draw_offset_palette[1] + self.tilesize * int(self.draw_type/pal_w)), (self.tilesize, self.tilesize)), 1)

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
					coords = [i * self.tilesize, j * self.tilesize]
					occval = self.level.data['tilemap']['layerocc'][msx * j + i]
					colors = {
						-1: (100, 100, 100),
						0: (0, 0, 0),
						1: (255, 255, 255),
						2: (0, 0, 255),
				    	3: (255, 0, 0),
					    4: (255, 255, 0),
					}
					pygame.draw.rect(self.mainwindowsurf, colors[occval], pygame.Rect((coords[0], coords[1]), (self.tilesize, self.tilesize)))

		else: # draw tiles on or below current layer
			for layer in range(1, 5):
				for i in range(msx):
					for j in range(msy):
						if layer <= self.tilemode:
							coords = [i * self.tilesize, j * self.tilesize]
							tileval = self.level.data['tilemap'][self.layer_key[layer]][msx * j + i]
							if tileval >= 0:
								sheet = 'tiles'
								if layer == 4:
									sheet = 'items'
								area = resources[sheet+'_coords'][tileval]
								self.mainwindowsurf.blit(resources[sheet], (coords[0], coords[1]), area=area)

		# render window surf to main window
		sx = self.mainwindowparams[0]
		sy = self.mainwindowparams[1]
		offx = self.mainwindowparams[2]
		offy = self.mainwindowparams[3]
		pygame.draw.rect(screen, (50, 50, 50), pygame.Rect((offx - 1, offy - 1), (sx + 2, sy + 2)), 1)
		screen.blit(self.mainwindowsurf, (offx, offy))

		if self.objectdrawtype == 'none':
			if self.tilemode == 0:
				screen.blit(resources['text_occ'], (sx/2, 10))
			elif self.tilemode == 1:
				screen.blit(resources['text_bg'], (sx/2, 10))
			elif self.tilemode == 2:
				screen.blit(resources['text_mg'], (sx/2, 10))
			elif self.tilemode == 3:
				screen.blit(resources['text_fg'], (sx/2, 10))
		else:
			if self.objectdrawtype == 'item':
				screen.blit(resources['text_item'], (sx/2, 10))

		pos = resources['font'].render(str(self.tileNum), True, (255, 255, 255))
		screen.blit(pos, (10, 10))

		# draw tile guides
		if self.guides == True:
			for i in range(1, msx):
				start_pos = (offx + i * ts, offy)
				end_pos = (offx + i * ts, offy + msy * ts)
				pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos)
			for i in range(1, msy):
				start_pos = (offx, offy + i * ts)
				end_pos = (offx + msx * ts, offy + i * ts)
				pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos)
