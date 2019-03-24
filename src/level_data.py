#!/usr/bin/python

"""
level_data.py: Classes for loading/saving tilemap level data
"""

import os
import json

class LevelData(object):
	def __init__(self, path=None):
		if path == None: # Creating new, empty level object
			self.data = {}
			self.data['tilemap'] = {}
			
			self.data['tilemap']['size'] = [24,24]
			self.data['tilemap']['ts'] = 8
			self.data['tilemap']['layer0'] = [0,0,0,2,3,1,78,0,\
				0,0,0,2,3,1,0,0,\
				1,0,0,2,3,1,5,0,\
				0,0,0,2,3,1,8,0,\
				0,0,0,2,3,1,0,0,\
				0,21,0,2,3,1,0,0,\
				0,0,0,2,3,1,0,0,\
				0,0,0,2,3,1,5,0]
			data['tilemap']['layerocc'] = []
			
			data['items'] = []
			data['items'].append({\
				'type': 'health',
				'value': 10
			})
			data['items''type': 'key',
				'value': 'green'
			})
		else: # else load level from file
			self.LoadLevel(path)
	
	def LoadLevel(self, path):
		with open('data.txt') as json_file:
			self.data = json.load(json_file)
	
	def SaveLevel(self, path):
		with open(path, 'w') as outfile:
			json.dump(self.data, outfile, indent=4, separators=(',', ': '))
			
