#!/usr/bin/python

"""
level_data.py: Classes for loading/saving tilemap level data
"""

from builtins import range

import os
import json

class LevelData(object):
	def __init__(self, path=None, size=[32,32]):
		if path == None: # Creating new, empty level object
			self.data = {}
			self.data['tilemap'] = {}
			
			self.data['tilemap']['size'] = size[:]
			self.data['tilemap']['ts'] = 16
			self.data['tilemap']['layerocc'] = [0]*size[0]*size[1]
			self.data['tilemap']['layer_b'] = [-1]*size[0]*size[1]
			self.data['tilemap']['layer_f'] = [-1]*size[0]*size[1]
			
			self.data['items'] = []
			
		else: # else load level from file
			self.LoadLevel(path)
	
	def LoadLevel(self, path):
		with open(path) as json_file:
			self.data = json.load(json_file)
	
	def SaveLevel(self, path):
		with open(path, 'w') as outfile:
			json.dump(self.data, outfile, indent=4, separators=(',', ': '))
			
