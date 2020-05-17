#!/usr/bin/python
# -*- coding: utf-8 -*-

""" Raid Notify

	1.0.1
		Added support for raider's game

	1.0.0
		Initial public release

"""

#---------------------------------------
# Script Import Libraries
#---------------------------------------
import clr
clr.AddReference("IronPython.Modules.dll")

import os
import codecs
import json
import re

#---------------------------------------
# Script Information
#---------------------------------------
ScriptName = "Raid Notify"
Website = "https://www.twitch.tv/kruiser8"
Description = "Provide Twitch raid chat notifications and a most recent file."
Creator = "Kruiser8"
Version = "1.0.1"

#---------------------------------------
# Script Variables
#---------------------------------------

# Settings file location
SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")

# Raider file location
MostRecentRaiderFile = os.path.join(os.path.dirname(__file__), "files", "most_recent_raider.txt")

# Raider RawData
reUserNotice = re.compile(r"(?:^(?:@(?P<irctags>[^\ ]*)\ )?:tmi\.twitch\.tv\ USERNOTICE)")

#---------------------------------------
# Script Classes
#---------------------------------------
class Settings(object):
	""" Load in saved settings file if available else set default values. """
	def __init__(self, settingsfile=None):
		try:
			with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
				self.__dict__ = json.load(f, encoding="utf-8")
		except:
			self.RaidMessage = "{name} is raiding the stream with {count} viewers!"
			self.RaidMinRaiders = 1
			self.MostRecentRaidFormat = "{name} - {count}"

	def Reload(self, jsondata):
		""" Reload settings from Streamlabs user interface by given json data. """
		self.__dict__ = json.loads(jsondata, encoding="utf-8")

	def Save(self, settingsfile):
		""" Save settings contained within to .json and .js settings files. """
		try:
			with codecs.open(settingsfile, encoding="utf-8-sig", mode="w+") as f:
				json.dump(self.__dict__, f, encoding="utf-8", ensure_ascii=False)
			with codecs.open(settingsfile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
				f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8', ensure_ascii=False)))
		except:
			Parent.Log(ScriptName, "Failed to save settings to file.")

#---------------------------------------
# Script Functions
#---------------------------------------

def sendChatNotification(displayName, viewerCount, game):
	try:
		Parent.SendStreamMessage(ScriptSettings.RaidMessage.format(name=displayName,count=str(viewerCount),game=game))
	except Exception as e:
		Parent.SendStreamWhisper(Parent.GetChannelName(), "Unable to use input format. Check Script Logs (i)")
		Parent.Log(ScriptName, str(e.args))
		Parent.SendStreamMessage("{name} is raiding the stream with {count} viewers!".format(name=displayName,count=str(viewerCount)))

def saveRecentRaid(displayName, viewerCount):
	try:
		with open(MostRecentRaiderFile, 'w') as writeFile:
			writeFile.write(ScriptSettings.MostRecentRaidFormat.format(name=displayName,count=str(viewerCount)))
	except Exception as e:
		Parent.SendStreamWhisper(Parent.GetChannelName(), "Unable to write most recent raid file using format. Check Script Logs (i)")
		Parent.Log(ScriptName, str(e.args))
		with open(MostRecentRaiderFile, 'w') as writeFile:
			writeFile.write('{name} - {count}'.format(name=displayName,count=str(viewerCount)))

def getRaiderGame(channel):
	headers = {}
	url = 'https://decapi.me/twitch/game/{0}'.format(channel)
	result = Parent.GetRequest(url, headers)

	data = json.loads(result)

	if data['status'] == 200:
		game = data['response']
		return game
	else:
		errorMessage = 'Error getting game for {0}: [{1}] {2}'.format(channel, str(data['status']), str(data['error']))
		Parent.Log(ScriptName, errorMessage)
		return ''

#---------------------------------------
# Chatbot Initialize Function
#---------------------------------------
def Init():

	# Load settings from file and verify
	global ScriptSettings
	ScriptSettings = Settings(SettingsFile)

	# End of Init
	return

#---------------------------------------
# Chatbot Save Settings Function
#---------------------------------------
def ReloadSettings(jsondata):

	# Reload newly saved settings and verify
	ScriptSettings.Reload(jsondata)

	# End of ReloadSettings
	return

#---------------------------------------
# Chatbot Execute Function
#---------------------------------------
def Execute(data):

	# Raw IRC message from Twitch
	if data.IsRawData() and data.IsFromTwitch():

		# Apply regex on raw data to detect raid usernotice
		usernotice = reUserNotice.search(data.RawData)
		if usernotice:

			tags = dict(re.findall(r"([^=]+)=([^;]*)(?:;|$)", usernotice.group("irctags")))
			id = tags['msg-id']
			if (id == 'raid'):
				displayName = tags['msg-param-displayName']
				viewerCount = tags['msg-param-viewerCount']

				if int(viewerCount) >= ScriptSettings.RaidMinRaiders:

					game = ''
					if '{game}' in ScriptSettings.RaidMessage:
						game = getRaiderGame(displayName)

					# Send Raid Stream Message
					sendChatNotification(displayName, viewerCount, game)

				# Save Most Recent Raider
				saveRecentRaid(displayName, viewerCount)

		# No usernotice
		return

	# End of execute
	return

#---------------------------------------
# Chatbot Tick Function
#---------------------------------------
def Tick():

	# End of Tick
	return

#---------------------------------------
# Chatbot Button Function
#---------------------------------------
def TestRaid():
	displayName = Parent.GetChannelName()
	viewerCount = Parent.GetRandom(ScriptSettings.RaidMinRaiders, ScriptSettings.RaidMinRaiders + 100)
	game = 'Test Game'

	sendChatNotification(displayName, viewerCount, game)
	saveRecentRaid(displayName, viewerCount)

def OpenReadMe():
    """Open the README.txt in the scripts folder"""
    os.startfile(os.path.join(os.path.dirname(__file__), "README.txt"))

def OpenOutputFiles():
    """Open output folder"""
    os.startfile(os.path.join(os.path.dirname(__file__), "files"))
