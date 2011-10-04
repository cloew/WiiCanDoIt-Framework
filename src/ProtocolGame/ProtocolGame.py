#!/usr/bin/env python

"""The Protocol Game --- highlight the differences between centralized
and decentralized protocols.
"""

import math
import sys
import os
import getopt
import time
import bisect
import random
import re 
import select
import threading
import subprocess

import pygame
from pygame.locals import *
from pygame.color import Color
from pygame.rect import Rect
import pygame.image

def centered_rect( rcenter, wh ) :
	"""Returns a Rect with size wh, centered on coords rcenter.
	"""
	return pygame.rect.Rect( rcenter[0]-wh[0]//2, rcenter[1]-wh[1]//2, wh[0], wh[1] )

def sub_rect_centered( rect, newwidth, newheight ) :
	"""Returns a new Rect of size (newwidth,newheight) centered on rect.

	Note that it is centered on only, it may not end up being a "sub"
	rectangle, in that 

	  rect.contains( sub_rect_centered( rect, x, y ) )

	may not return True.
	"""
	left = (rect.left+rect.width//2 - newwidth//2)
	top = (rect.top+rect.height//2 - newheight//2)

	return Rect( left, top, newwidth, newheight )

def sub_rect_offset( rect, x=0, y=0, u=0, v=0 ) :
	"""Returns a new Rect based on rect and offsets from borders.  

	x, y represents offsets from the upper left corner,
	u, v > 0 represent width of new sub rect,
	u, v < 0 represent offsets from the rect's lower right corner,

	If any parameter is a float, it is treated as a percentage of the original
	rect's size (the significance of the sign remains).

	So:
	  sub_rect( r, 10, 10, -10, -10 )
	and
	  sub_rect( r, 0.1, 0.1, -0.1, -0,1 )
	yield the same sub rectangle of r, if r is a 100x100 square.

	And
	  sub_rect( r )
	is a simple copy.
	"""
	# the defaults
	l, t, m, n = rect.left, rect.top, rect.left+rect.width, rect.top+rect.height

	# account for percents
	def convert_percents( orig_begin, orig_end, param ) :
		if isinstance(param,float) :
			orig_length = orig_end - orig_begin
			param = int(math.floor(orig_length*abs(param)))	
			if param < 0 :
				param = -param
		return param

	# is it a width or an offset?
	def width_or_offset( new_begin, orig_end, param ) :
		if param <= 0 :
			# an offset
			param = orig_end+param - new_begin
		return param

	a = l + abs( convert_percents(l,m,x) )
	b = t + abs( convert_percents(t,n,y) )

	c = width_or_offset( a, m, convert_percents(l,m,u) )
	d = width_or_offset( b, n, convert_percents(t,n,v) )

	return Rect( (a,b), (c,d) )

def dice_rect( rect, cols_rows_tuple, margin ) :
	"""Returns a tuple of Rects that divide rect into cols and rows
	with margin pixels in between (and around edge).
	"""
	gridcr = cols_rows_tuple
	gridmargin = (4,4)
	gridoffset = (rect.left,rect.top)
	# scaled size of one element
	def scaled_grid_size( length, count, margin ) :
		l = length - (count+1)*margin
		l -= l%count
		return l//count

	gridsize = map( lambda x : scaled_grid_size(*x),
			zip( (rect.w,rect.h), gridcr, gridmargin ) )
	offsets = map( sum, zip(gridoffset,gridmargin))
	size = map( sum, zip(gridsize,gridmargin))
	#print gridsize, offsets, size
	return tuple([ pygame.rect.Rect( 
		map( sum, 
			zip(offsets, ((g%gridcr[0])*(size[0]),(g//gridcr[0])*(size[1])) )), gridsize )
			for g in xrange(gridcr[0]*gridcr[1]) ])

def stretch_imagelist_to_rect( imagelist, rect ) :
	return [ pygame.transform.scale(i,rect.size) for i in imagelist ]

def blit_image_in_rect( scr, img, rect ) :
	scr.blit( img, rect.topleft )

def	blit_text_in_rect_centered( scr, rect, fnt, text, clr ) : 
	sz = fnt.size( text )
	x = rect.left+rect.width//2-sz[0]//2
	y = rect.top+rect.height//2-sz[1]//2
	scr.blit( fnt.render( text, 1, clr ), (x,y) ) 

# exceptions
class GameException( Exception ) :
	def __init__( self, runninggame ) :
		super(GameException,self).__init__()
		self.gametime = time.time() - runninggame.starttime
	def __str__( self ) :
		return " ".join( ["%s,"%self.message, "running time", str(self.gametime) ] )
class GameEventsEOF( GameException ) :
	message = "End of game events"
class GameOver( GameException ) :
	message = "Game over"
class GameOverDisplayError(GameException) :
	message="Game over --- display error"

# game config
def _arg_splitter( s ) :
	# need +-. for floating point values
	return re.split( r'[^-a-zA-Z0-9+._]+', s ) 

class Config( object ) :
	# global config (compile time)
	CONFIG = {
		'COLORS':['red','green','blue','purple'],
		'EVENT_QUEUE_RESOLUTION':0.030, # 30 milli seconds
	}
	USAGE = (
		( 'colors', int, "Number of colors in the game", lambda v : v>1),
		( 'playerIDs', _arg_splitter, "Player IDs in game", lambda v : len(v) and len(v[0])>0 ),
		( 'noise', lambda s : map( float, _arg_splitter(s) ), 
			"mu and std. dev. of response noise (s)", lambda v : len(v)==2 )
	)
	def __init__( self, args ) :
			
		self.config = dict( self.CONFIG )  # copy

		for u in range(len(self.USAGE)) :
			name, parser, descr, validator = self.USAGE[u]
			#print name, parser, descr, args[u]
			v = parser( args[u] )
			try :
				if validator( v ) :
					print descr+":", v
					self.config[name] = v
			except :
				pass

	def gameOn( self, gameStyle=None ) :
		"""Returns a running game instance.
		"""
		ctor = globals()[gameStyle or 'RunningGame']
		return ctor( prng=random.Random(), **self.config )	

class wiiPipeline(object) :
	"""Class for controlling the wii pipeline of data.
	"""
	RUMBLETIME=0.2
	def __init__( self, insevent ) :
		self.sp = subprocess.Popen( ["./wiis/pipeline"], bufsize=1, shell=False,
				stdin=subprocess.PIPE, stdout=subprocess.PIPE )
		self.__outf, self.inf = (self.sp.stdin,self.sp.stdout)
		self.__insevent = insevent
		self.rumble = self.norumble
	def write( self, cmd ) :
		self.__outf.write(cmd+'\n')
	def norumble( self, plid ) : pass
	def justrumble( self, plid, secs_to_begin=0 ) :
		t = time.time()+secs_to_begin
		self.__insevent( (t,
					(lambda f=self.write, m="rumble-on %s"%plid : f(m), tuple() )) )
		# post an event to turn rumble off
		self.__insevent( (t+self.RUMBLETIME, 
					(lambda f=self.write, m="rumble-off %s"%plid : f(m), tuple() )) )
	def rumble_then_discover( self, plid ) :
		self.justrumble( plid )
		self.__insevent( (time.time()+self.RUMBLETIME*3/2, (self.discoverone, tuple()) ) )
	def discoverone( self ) :
		self.write( "discover-one" )
		pass
	def __del__( self ) :
		self.__outf.write("quit\n")
		self.sp.wait()

class RunningGame(object) :
	"""A running game that uses the console.
	"""
	def __init__( self, **config ) :
		super(RunningGame,self).__init__()
		self.__dict__.update( config )
		# we should now have:
		#   colors = number of transition colors
		# 	prng = the prng to use (duh)
		# 	noise = (mu,stddev) distribution of response noise (secs)

		# --> colors is now the list of color names
		self.colors = self.COLORS[:self.colors]

		# init the wii pipeline
		self.wiipl = wiiPipeline(self.insertEvent)

		# continue with the init for the 'restartable' phase
		self.__reinit()
		
	def __reinit( self ) :	
		# create an empty event queue
		self.equeue = []

		# mark the start time
		self.starttime = time.time()

		###
		# Primary interface functions for game modes
		# (these are setup with __installGameModeMappings as game transitions
		# occurr).
		# _checkGameOver(s)
		# _modeString(s)
		# _changeColor(s,plid,amount)
		# _nextMode(s)
		###
		self._checkGameOver = lambda s : None
		self._modeString = lambda s : ''
		self._changeColor = lambda s,p,a : None #\
#			raise RuntimeError( "%s: default _changeColor called" % s.__class__ )
		self._nextMode = lambda s : None #\
#		raise RuntimeError( "%s: default _nextMode called" % s.__class__ )

		# DO NOT just call .goto functions, instead post an event to 
		# call one of these --- we have to let subclasses finish setting up
		# their internal states.
		f = self.gotoWiiDiscover
		if getattr(self,'playerIDs',[]) :
			f = self.preWiiDiscover()

		self.insertEvent( (0, ( f, tuple() ) ))

	def __str__( self ) :
		# display usrmsg if there is one
		um = getattr(self,'usrmsg','')
		if um :
			um = '\n' + um
		return self._modeString(self) + um

	def _installGameModeMappings( self, mappings ) :
		"""Installs the dictionary mappings:

		  { 'function_name': function_object }

		into the running instance.
		"""
		for name, func in mappings.iteritems() :
			setattr( self, name, func )

	###
	# A basic mode transition message interface for users
	###
	class transitionMessage(object) :
		def __init__( self, rg, secs ) :
			"""rg is a RunningGame instance."""
			self.secs = secs + 1
			self( rg )
		def __call__( self, rg ) :
			self.secs -= 1
			if self.secs > 0 :
				rg.insertEvent( (time.time()+1, (self, (rg,)) ) )
			else :
				# this seems to be the DRY way to clear the user message
				# --- why would we want a usermessage preserved across game
				#     state transitions?
				try :
					del rg.usrmsg
				except :
					pass
				# goto next mode
				rg._nextMode()

	###
	# Game Modes:  wiiDiscover, playGame, gameOver
	###
	def preWiiDiscover ( self ) :
		"""Don't go through discovery for no reason.
		"""
		if hasattr(self,'goal') :
			del self.goal
			del self.grid
		rumbles = 6
		if hasattr( self, 'playerIDs' ) and len(self.playerIDs) :
			# rumble all nodes
			rumbletime = (rumbles*2+1)*self.wiipl.RUMBLETIME
			for r in range(rumbles) :
				for k in self.playerIDs :
					self.wiipl.justrumble( k, secs_to_begin=r*2*self.wiipl.RUMBLETIME )

			self.usrmsg = "Rumbling wiis do not need re-discovery!"
			self.transitionMessage( rg=self, secs=rumbletime)
			self._installGameModeMappings( {
				'_nextMode': self.gotoWiiDiscover,
				} )
		else :
			# need discovery
			self.gotoWiiDiscover()

	DISCOVERSECS=12
	def gotoWiiDiscover( self ) :
		"""Goto discovery mode for wiis.
		"""
		# init --- don't re-init
		if not hasattr( self, 'playerIDs' ) :
			self.playerIDs = []

		# turn rumble to rumble and re-discover
		self.wiipl.rumble = self.wiipl.rumble_then_discover
		#self.wiipl.rumble = self.wiipl.justrumble

		# turn on discovery
		self.wiipl.discoverone()

		# show status message to users and transition to next mode
		# in 5 seconds
		tm = self.transitionMessage( rg=self, secs=self.DISCOVERSECS )

		# function mappings
		def modeString( s, tm=tm ) :
			return 'wii Discovery: %d so far; TAB to continue; %d secs remaining...' % \
					( len(s.playerIDs), tm.secs ) 
		def changeColor( s, plid, amount, tm=tm ) :
			if plid not in s.playerIDs :
				s.playerIDs.append( plid )
				tm.secs = self.DISCOVERSECS
		self._installGameModeMappings( {
			'_modeString': modeString,
			'_changeColor': changeColor,
			'_nextMode': self.gotoReadyPlayGame,
			} )
	
		return True

	WIIMOTES=4
	def gotoReadyPlayGame( self ) :
		"""Goto play game mode
		"""
		# we should now have a self.playerIDs list 
		# 	[ playerID1, playerID2, ... ]
		# from wiiDiscoveryMode
		if len(self.playerIDs) < self.WIIMOTES :
			# transition message, and return to discovery
			self._installGameModeMappings( {
				'_modeString': lambda s : "Not enough wiis found! Restarting discovery...",
				'_nextMode': self.gotoWiiDiscover
				} )
			self.transitionMessage( rg=self, secs=2 )
			return False

		# pick a goal at random
		self.goal = self.prng.randrange(0,len(self.colors))

		# if they all wind up being on the goal, then there is no game to play
		# ... make sure this doesn't happen
		self.grid = [self.goal]  # force entry
		while (max(self.grid) == min(self.grid)) and (self.grid[0] == self.goal) :
			# a list of current square color (indices), one for each player
			self.grid = [ self.prng.randrange(0,len(self.colors)) 
								for i in range(len(self.playerIDs)) ]
		#print self.grid

		# playercells is the randomized mapping from player id to grid cell
		ptocell = range(len(self.playerIDs))
		self.prng.shuffle(ptocell)
		self.playercells = {}
		for i in xrange(len(self.playerIDs)) : 
			self.playercells[self.playerIDs[i]] = ptocell[i]

		tm = self.transitionMessage( rg=self, secs=5 )

		# turn rumble feedback off
		self.wiipl.rumble = self.wiipl.norumble

		###
		# new function mappings for play game mode
		###
		def modeString( s, tm=tm ) :
			return 'Ready to Play! %d' % tm.secs 
		def changeColor( s, plid, amount ) :
			# do nothing till game begins
			pass
		self._installGameModeMappings( {
			'_modeString': modeString,
			'_changeColor': changeColor,
			'_nextMode': self.gotoPlayGame,
			} )

		self.usrmsg = modeString(self)

		return True

	def gotoPlayGame( self ) :
		# turn simple rumble back on
		self.wiipl.rumble = self.wiipl.justrumble

		###
		# just setup new mappings for state changes
		def modeString( s ) :
			return '%s goal %d' % (s.grid, s.goal)
		def changeColor( s, plid, amount ) :
			"""Increment gridelement's color by amount.
			"""
			ge = self.playercells[plid]
			if ge >= 0 :
				s.grid[ge] = (s.grid[ge] + amount) % len(s.colors)

		def checkGameOver( self ) :
			"""Returns False or raises GameOver
			"""
			# we cannot be done with the game when there are remaining events in
			# the event queue
			if len(self.equeue) :
				return False 

			for i in xrange( 1, len(self.grid) ) :
				if self.grid[i] != self.grid[i-1] : 
					return False

			raise GameOver( self )

		self._installGameModeMappings( {
			'_modeString': modeString,
			'_changeColor': changeColor,
			'_checkGameOver': checkGameOver,
			'_nextMode': self.preWiiDiscover,
			} )

		return True
		
	POSTGAMESHOWSECS=5
	def gotoPostGameShow( self ) :
		"""Goto game over screen
		"""
		self.usrmsg = "Success! Game Over!" 
		tm = self.transitionMessage( rg=self, secs=self.POSTGAMESHOWSECS )

	def nextColor( self, playerID ) :
		"""Next color for a player."""
		self._changeColor( self, playerID, 1 )

	def prevColor( self, playerID ) :
		"""Previous color for a player."""
		self._changeColor( self, playerID, len(self.colors)-1 )

	def randomColor( self, playerID ) :
		"""A randomly choosen color for a player (but guaranteed to be 
		different than the current.
		"""
		self._changeColor( self, playerID, self.prng.randrange(1,len(self.colors) ))

	def refreshDisplay( self ) :
		print str(self)

	def insertEvent( self, event ) :
		"""Inserts an event (as described in processEventQueue) 
		into the queue.
		"""
		# place this event into the queue
		insat = bisect.bisect( [a[0] for a in self.equeue], event[0] )
		self.equeue.insert(insat, event)

	def processEventQueue( self, now, newevents=[], count=None ) :
		"""The meat of the action.  now represents the current time.
		The event queue consists of tuples:

		  ( time_to_eval_at, (RunningGame_member_function, args) )

		The event argument should be one of these such tuples.  count is 
		the maximum number of events to process (or None).

		processEventQueue returns the number of events processed from the 
		queue (0 -> no events processed)
		"""
		# place events into the queue
		map( self.insertEvent, newevents )

		# process all events with resolution seconds
		upto = bisect.bisect( [a[0] for a in self.equeue], 
				now+self.EVENT_QUEUE_RESOLUTION )

		upto = min( [upto, count or len(self.equeue)] )

		# split now, so that member functions can place new events 
		# on the queue (think *timers*)
		events_to_eval = self.equeue[:upto]
		self.equeue = self.equeue[upto:]

		for i in xrange(upto) :
			apply( *events_to_eval[i][1] )
		
		return upto

	def __gameEventHandler( self, now, rg, r, readers, xcept, rpipes ) :
		"""The standard handler, see RunningGame.play() for argument and 
		and return value documentation.
		"""
		l = r.readline()
		if not l :
			# EOF signal in python
			#sys.stderr.write( "End of file on %s\n" % r )
			xcept.append(r)  # will be remove from readers in play()
			return None
		plid, op = l.split()
		ev = ( {
			'next':rg.nextColor,
			'previous':rg.prevColor,
			'random':rg.randomColor,
			'found':rg.nextColor,
			'ripple':lambda plid : None
			}[op], (plid,) )	
		self.wiipl.rumble( plid )
		# random response noise
		ns = rg.prng.gauss( *self.noise )
		#print "next event noise", ns, self.noise
		ev = ( now+abs(ns), ev )
		# return as list
		return [ev]

	def play( self, pipes, handlers={} ) :
		"""Read events from input pipes till the game concludes 
		or raises GameEventsEOF when data on pipes exhausted.

		handlers is a dictionary with keys from the pipes list:
		  { pipes_element : handler_function }
		Any keys found therein will have
		  handler_function( now, running_game, pipes_element, 
				readers, xcept, rpipes )
		called when pipes_element is in the readers set of select.select().

		The handler function should:
		 1. return a list of game events, or None
		 2. remove pipes_element from rpipes if there is no more 
			data coming across the pipe.
		 3. *place* pipes_element *into* the xcept set if failure is detected.
		"""
		self.refreshDisplay()
		rpipes = list(pipes)

		while len(rpipes) :
		
			now = time.time()
			waitfor = max(0,( len(self.equeue) and (self.equeue[0][0]-now) ) or 100)
			readers, writers, xcept = select.select(rpipes,[],rpipes,waitfor)
			# update current time
			now = time.time()
			# insert new events into queue
			events = []
			for r in readers :
				h = handlers.get(r,self.__gameEventHandler)
				evlist = h( now, self, r, readers, xcept, rpipes )
				events.extend( evlist or [] )

			# insert into event queue, and process all pending events
			if self.processEventQueue( now, newevents=events ) > 0 :
				# refresh game state
				self.refreshDisplay()

			# is the game over yet?
#			try :
				self._checkGameOver(self)
#			except GameOver, go :
#				self.gotoPostGameShow()

			# handle xcept set
			for x in xcept :
				#sys.stderr.write( "I/O Exception on %s\n" % r )
				try :
					xindex = rpipes.index(x)  # it should be in there...
					if xindex >= 0 :
						del rpipes[xindex]
				except :
					pass

			# if the only readers left *don't* handle game events, whats the 
			# point of continuing?
			#print rpipes
			if not self.equeue :
				more_game_events = False
				for r in rpipes :
					# we assume that all gameEventHandlers *don't* have a
					# handlers entry
					if r not in handlers :
						more_game_events = True
						break
	
				if not more_game_events :
					break

		# if we get this far, we must raise the EOF event
		raise GameEventsEOF(self)

	def waitOnEventQueue( self ) :
		"""Waits until leading event is processed.
		
		Returns False if queue is empty.
		"""
		if not len( self.equeue ) :
			return False
		now = time.time()
		try :
			time.sleep(self.equeue[0][0]-now)
		except IOError, e:
			pass # invalid (0) arg to sleep
		# the time must now be the eval time of the first event
		self.processEventQueue( self.equeue[0][0], count=1 )
		# we must process at least one, so it is time to redisplay...
		self.refreshDisplay()
		return True

class PyGame( RunningGame ) :
	"""pygame implementation.
	"""
	class EventShuffler( object ) :
		"""All the threading logic is in here.  Here is the way things are
		handled --- the goal is to keep *all* game logic in the same thread
		as calls RunningGame.play, and there should be only one
		thread that does that.

		The upshot is that *all* this object does is moves events from a 
		dedicated pygame event queue monitoring thread to the thread running
		RunningGame.play.

		The notifier thread:
		  1. waits for self.ready_for_more_events to be set (true)
		  2. sets self.events to the result of pygame.event.get()
		  3. clears self.ready_for_more_events 
		  4. writes one byte to the self.w file descriptor
		  5. loops back --> 1

		The handler function is called when a byte is received
		on the r file descriptor, via the play() logic in RunningGame (super called
		from PyGame).  The handler:
		  0. deals with all the self.events,
		  1. reads one byte from self.r,
		  2. sets self.ready_for_more_events

		I don't think there are race conditions in the above logic:
		  a. notifier manipulates self.events only when ready_for_more_events is
		     set and there are no bytes in the pipe.  
		  b. handler manipulates self.events only when ready_for_more_events is
		     set and there is one byte in the pipe.
		  c. it *is possible* that between notifier 4 and 1, that all of
			 handler has run, in which case notifier 1 simply won't stall the
			 notifier thread.  but this isn't a race condition, now is it?
		"""
		def __init__( self ) :
			# either an empty list or a list or a list of events
			# returned by pygame.event.wait.
			self.events = []

			# signal event from handler to notifier
			self.ready_for_more_events = threading.Event()
			self.ready_for_more_events.set() # make it true
				
			# the notification pipe from notifier to handler
			self.r, self.w = os.pipe() 

		def notifier( self ) :
			# see class docstring
			while True :
				self.ready_for_more_events.wait()
				self.events = pygame.event.get()
				if not hasattr(self,'w') :
					break  # end of thread logic (see EventShuffler.shutdown)
				self.ready_for_more_events.clear()
				os.write(self.w,'0')

		def handler( self, now, rg, r, readers, xcept, rpipes ) :
			"""Specialized handler for PyGame events (pump and deal with
			the PyGame event queue).

			See RunningGame.play() for documentation on arguments and
			return value.

			See the EventShuffler docstring for threading documentation.
			"""
			# deal with self.events
			for event in self.events :
				# handle window resize
				if event.type==QUIT: 
					raise GameOverDisplayError(rg)
				# http://www.pygame.org/wiki/WindowResizing?parent=CookBook
				elif event.type==VIDEORESIZE:
					rg.setupScreen( event.dict['size'] )
					# screen will be redrawn after all events	
				elif event.type == KEYDOWN :
					if event.key in (K_ESCAPE,K_q) :
						raise GameOver(rg)
					elif event.key in (K_SPACE,K_TAB) :
						# goto the next mode
						try :
							del rg.usrmsg
						except :
							pass
						rg.insertEvent( (now, (rg._nextMode, tuple())) )

			# pump it up! (just in case)
			# pygame.event.pump() --- i don't think we need this.

			# read one byte from the notification pipe
			os.read(self.r, 1)

			# signal notifier
			self.ready_for_more_events.set()

			# trick --- return a no-op event for immediate evaluation so that
			# we force a redraw on sizing events
			return [ (now, (lambda x : None, (None,)) )]

		def shutdown( self, nthread ) :
			os.close(self.r)
			os.close(self.w)
			# force an exception in the notifier thread (not nice, but
			# experience shows this always works!
			del self.w
			pygame.event.post( pygame.event.Event(USEREVENT) )
			self.ready_for_more_events.set()
			nthread.join()

	# PyGame class
	BACKGROUND = Color('black')
	TEXTCOLOR = Color('gold1')
	USRMSGBACKGROUND = Color('blue4')
	DEVMODE = False #True
	def __init__( self, **config ) :
		super(PyGame,self).__init__(**config)

		pygame.init()
		self.display = pygame.display  # convenient alias
		self.display.set_caption("The Protocol Game")

		# read in grid images
		self.gridimages = [ pygame.image.load(
				os.path.sep.join(['images','grid_%s.png'%c]))
				for c in self.COLORS ]

		self.screensize = self.display.list_modes()[0]
		if self.DEVMODE : 
			self.screensize = map( lambda a : a/2, self.screensize )

		####
		# game interface functions
		# _setupScreen( s, wh )
		# _refreshDisplay( s )
		####
		self._setupScreen = lambda s, wh : None
		self._refreshDisplay = lambda s : setattr(s,'usrmsg',s._modeString(s))

		# make sure setup screen gets called
		self.setupScreen( self.screensize )

	FONTFRACTION = 0.05
	MARGINFRACTION = 0.02
	GRIDOFFSETFRACTION = 0.35
	def __setup_screen_basic_metrics(self, wh) :
		self.screensize = wh
		self.scrrect = Rect( (0,0), wh )
		self.screen = self.display.set_mode(
				self.screensize, HWSURFACE|DOUBLEBUF|RESIZABLE)
		# dynamic font height
		self.fheight = int(math.floor(wh[1]*self.FONTFRACTION))
		self.gamefont = pygame.font.SysFont("None", self.fheight )
		self.prettyfont = pygame.font.SysFont("None", self.fheight*2)
		self.prettyfont.set_bold( True )
		self.prettyfont.set_italic( True )

		self.margin = int(max(2,math.floor(wh[1]*self.MARGINFRACTION)))

	def __blit_usrmsg( self ) :
		m = getattr(self,'usrmsg',None) 
		if m :
			lines = re.split(r'[.;!?] +', m)
			rects = [ Rect((0,0), self.prettyfont.size(l)) for l in lines ] 
			# remember height
			height = rects[0].height
			# 'add' the rects together
			h = max( map( lambda r : r.height, rects ))*len(rects)
			w = max( map( lambda r : r.width, rects ))
			# add a margin between lines, the bottom and top
			h += (len(rects)-1)*self.margin + 2*self.margin
			# add a margin on sides
			w += 2*self.margin

			# center in display
			crect = sub_rect_centered( self.scrrect, w, h )
			# draw it
			pygame.draw.rect( self.screen, self.USRMSGBACKGROUND, crect )

			# bump back to max text size
			crect.top += self.margin
			crect.left += self.margin
			crect.width -= self.margin
			crect.height = height

			# draw lines
			for l in lines :
				blit_text_in_rect_centered( self.screen, crect, self.prettyfont,
						l, self.TEXTCOLOR)	  
				crect.top += height + self.margin

	def __del__( self ) :
		# do the obvious
		pygame.display.quit()
	
	def refreshDisplay( self ) :
		if not hasattr(self,'screen') :
			self.setupScreen( self.screensize )

		self.screen.fill( self.BACKGROUND )
		self._refreshDisplay(self)
		# if there is a user message
		self.__blit_usrmsg()
		pygame.display.flip()

	def setupScreen( self, wh ) :
		self.__setup_screen_basic_metrics(wh)
		self._setupScreen(self,wh)

	####
	# game modes
	####
	def gotoReadyPlayGame( self ) :

		# chain
		if not super(PyGame,self).gotoReadyPlayGame() :
			# not ready yet
			return False

		def setupScreen( s, wh ) :
			s.__setup_screen_basic_metrics( wh )
			# calculate rows and cols, prefer cols >= rows 
			x = math.sqrt(len(s.grid))
			f = math.floor(x)
			cr = [ int(f) ]*2
			x = 0 # incr cols first
			while cr[0]*cr[1] < len(s.grid) :
				cr[x] += 1
				x = (x+1)%2

			# the rects for the grid cols
			gridarea = sub_rect_offset( s.scrrect, s.GRIDOFFSETFRACTION, 0, 0, 0 )
			s.gridrects = dice_rect( gridarea, cr, s.margin )

			# scaled versions of images to show
			gridsize = s.gridrects[0].size
			s.showimages = stretch_imagelist_to_rect( s.gridimages, s.gridrects[0] )
			# goal location
			goalarea = sub_rect_offset( s.scrrect, 0, 0.3, gridarea.left, gridsize[1] )
			s.goalrect = sub_rect_centered( goalarea, *gridsize )
			s.goallabelrect = Rect( goalarea.left, s.goalrect.bottom, 
					goalarea.width, s.fheight*3 )

		# make sure new screen metrics are setup
		setupScreen( self, self.screensize )

		def refreshDisplay( s ) :
			for g in xrange( len(s.grid) ) :
				blit_image_in_rect(s.screen,s.showimages[s.grid[g]],s.gridrects[g])

			blit_image_in_rect( s.screen, s.showimages[s.goal], s.goalrect )
			s.screen.blit(s.showimages[s.goal],s.goalrect)
			t = s.COLORS[s.goal] + " goal"
			t = t.title()
			blit_text_in_rect_centered( s.screen, s.goallabelrect, s.prettyfont,
					t, Color(s.COLORS[s.goal]))	  

		# setup mappings for gameplay
		self._installGameModeMappings( {
			'_setupScreen': setupScreen,
			'_refreshDisplay': refreshDisplay,
			} )

	def play( self, pipes, handlers={} ) :
		"""PyGame version of play() provides a handler to manage
		the pygame event queue."""
		# setup event transfer
		shuffler = PyGame.EventShuffler()
		notifier_thread = threading.Thread( group=None,
				target=shuffler.notifier, name="pygame-notifier" )
		notifier_thread.start()

		# add on pygame specific handlers
		pipes.append( shuffler.r )
		handlers[shuffler.r] = shuffler.handler
		try :
			# chain to standard handling
			super(PyGame,self).play( pipes, handlers )
		finally :
			# return pipes and handlers to the way they were
			del handlers[pipes.pop()]
			# join up
			shuffler.shutdown( notifier_thread )

# a main startup routine
def main( gameStyle, argv ) :

	try :
		r = Config( argv ).gameOn( gameStyle )
		r.play([r.wiipl.inf,])
	except GameOver, e :
		print e
	except GameEventsEOF, e :
		print e
		while r.waitOnEventQueue() :
			pass
		print GameOver(r)
	except Exception, e :
		print str(e)
		# reraise for the call stack visualization 
		# (can't debug without it!)
		raise

if __name__ == '__main__' :
	# call with gameStyle as the first argument:
	#   $ python ProtocolGame.py RunningGame blah blah blah
	#   $ python ProtocolGame.py PyGame blah blah blah
	# or even
	#   $ python ProtocolGame.py '' blah blah blah
	main( sys.argv[1], sys.argv[2:] )

