import impressive
import sys, os
import socket, select
from pygame.locals import *
import pygame
from threading import Thread
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))+ '/GameEventParser')
from GameEventListener import *

class SlideController:
	def __init__(self):
		print "Started the slide controller"

	def closeSlide(self, params):
		print "Called closeslide"
		#nextEvent = pygame.event.Event(KEYDOWN, {'unicode': None, 'key': K_ESCAPE})
		pygame.event.post(pygame.event.Event(QUIT))
		listener.end()
	
	def changeSlide(self, params):
		# see if we should go left or right
		flickx = params['flickx']
		if flickx > 0 :
			# next slide
			nextEvent = pygame.event.Event(KEYDOWN, {'unicode': None, 'key': K_RIGHT})
			pygame.event.post(nextEvent)
		elif flickx < 0:
			# previous slide
			prevEvent = pygame.event.Event(KEYDOWN, {'unicode': None, 'key': K_LEFT})
			pygame.event.post(prevEvent)
controller = SlideController()

listener = GameEventListener( controller, 'bindings.py', 'ImpressiveBindings', 1)
listener.start()
impressive.ParseOptions(sys.argv[1:])
impressive.run_main()
