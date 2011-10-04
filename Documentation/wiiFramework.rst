============================
The CSM Wii Gaming Framework
============================

Dependencies
------------

Requires the following Python packages from the debian repositories:
 
  #. python-cwiid
  #. python-pygame


Wiimote Manager
---------------
The purpose of the Wiimote Manager is to provide a simple interface with the cwiid.
This allows for all the Wiimote objects created by cwiid to be held in one place.

The Wiimote Manager performs the following tasks:
 * Interfaces with the Bluetooth Stack on Linux for all wiimote data
 * Holds all Wiimote objects created by cwiid
 * Contains the functionality to add Wiimotes as they are synced to the Bluetooth Stack
 * Sets the player number of Cwiid objects
 * Keeps track of what wiimote has what ID for passing events
 * Contains the callback function of each Wiimote that sends data over a Network Socket to the Wii Event Parser

To achieve this, the Wiimote Manager contains a list of objects called WiimoteControl. This object contains an individual
wiimote object and the ID assigned to it. This class also sets up the report modes of the Wiimote, as well as the callback
function. This function creates a rawdata event that contains both the ID of the wiimote and relevant data. That object
gets pickled and sent over the network socket.


Wii Event Parser
----------------
The Purpose of the Wii Event parser is to analyze the data provided by the wiimotes. It is designed to perform the following functions:
 * Read data in from a network socket_
 * Analyze the data from the socket in different ways depending on the information type
 * If an event is triggered, send the event over a second socket to the Game Event Parser

.. [socket] The purpose of this socket is for abstraction. The parser can read data, no matter the source,
            as long as it is passed over that socket in the correct format

To achieve this functionality, the Wii Event Parser contains several 
subclasses that keep track of necessary data to ensure the proper events get called. they are as follows:

*Accelerometer*
  Each Wiimote contains 3 accelerometer objects, one for each axis. The Accelerometer class tests these
  values against what is considered a normal acceleration value. If the acceleration value is above (or below)
  a threshold, it will get passed off to an AccMagTracker object to find the magnitude of the flick.

*AccMagTracker*
  This is a class used solely for keeping track of an acceleration magnitude. When an accelerometer value is
  above a certain threshold, it will get passed to this object. The AccMagTracker first checks to see when
  the most recent event occured, to see if the accelerometer is in a lockout state. If the accelerometer is not
  in a lockout state, it then checks to see if the value has reached a peak yet. The tracker looks for a peak
  flick by testing each flick value against the one right before it. once the flick is lower than the one before it,
  it assumes that the value before has reached its peak, and returns the acceleration value to pass an event.

*RollPitch*
  This object uses simple trig calculations to find the approximate roll and pitch of a wiimote. It also keeps track
  of an approximate current roll value, which changes every set amount of radians (as of writing this, .3 radians
  for roll and .2 radians for pitch). Because of this, an event is fired every time the wiimote is rolled that threshold
  relative to the last event called. This class also contains guards to test for if a flick might be occuring, and
  if it is, it does not send roll events.

*ButtonControl*
  This object is responsible for all events concerning buttons. Cwiid reports a button event as a binary string of what
  buttons are currently pressed. This object conpares that string to the prior state of the buttons, and calls a press
  or release of the proper button every time it finds a difference.

When events are triggered, each subclass creates a WiiEvent object. This object contains the ID of the wiimote, the action_ 
performed, and a modifier_

.. [action] This is a string that represents what the event was, such as *PressA* and  *FlickX*.
.. [modifier] This is a number that represents what exactly happened in the event. A button press is 1, button release is -1,
              and acceleration values are the magnitude of the flick.


WEPControl
----------
The initial intent of the WEPControl class was to contain botht the Wii Event Parser and Wiimote Manager in a single
location. However, since the Game Event listener (see below) now sets up the wii event parser, the WEPControl is now
primarily an interface for the Wiimote Manager. This class contains an Add Wiimotes function via command line, that
simply creates a cwiid.Wiimote object and adds it to the Wiimote manager, as well as a Gui function that performs
the same task.

Game Event Parser
-----------------
The Game Event Parser receives strings of WiiEvents from the Wii Event Parser and converts those strings into 
function calls in the game, which we have dubbed GameEvents_ The Game Event Parser can handle reasonably 
complicated sequences of events, but most game developers will likely only use simple bindings such as a 
single button press. The Game Event Parser is composed of the following parts:

**Game Event Core**
  The Game Event Core, located in the file called GameEventCore.py, is where parsing WiiEvents into GameEvents_ actually
  takes place. When it is initialized, the Game Event Core reads the bindings file and sets up several data structure to hold
  the binding's sequence of events for each player. The core then listens on a network socket for WiiEvents from the 
  Wii Event Parser. When it receives a Wii Event, it will look at the Wiimote ID, to see which player performed the action, 
  then examine each binding for that player to see if the received Wii Event matches the next event in the binding's sequence.
  If the event matches, either the binding's pointer will be advanced or a GameEvent will be sent to the Game Event Listener.
  For a finite state diagram of information flow within the Game Event Core, see the design report. 

**Bindings List**
  Each game must create a list of bindings that tells the Game Event Listener which game function to call after a
  given sequence of Wii Events. The bindings file is created by making a subclass of the Game Event Core class. 
  Within this subclass, no methods need to be defined; just variables that store a Wii Event list. Any variable defined
  in this subclass that begins with the prefix 'bind\_' will be treated as a binding. The Game Event Core will expect
  the 'bind\_' variable to be assigned to a Python list object. Within this list can be one or more of the following:
  * Atomic Wii Event strings
  * Tuples containing atomic Wii Event strings
  * Sets containing atomic Wii Event strings

  The atomic Wii Event strings currently supported are:
  * ButtonAPress / ButtonARelease
  * ButtonBPress / ButtonBRelease
  * Button1Press / Button1Release
  * Button2Press / Button2Release
  * ButtonUpPress / ButtonUpRelease
  * ButtonDownPress / ButtonDownRelease
  * ButtonLeftPress / ButtonLeftRelease
  * ButtonRightPress / ButtonRightRelease
  * ButtonHomePress / ButtonHomeRelease
  * ButtonPlusPress / ButtonPlusRelease
  * ButtonMinusPress / ButtonMinusRelease
  * FlickX
  * FlickY
  * FlickZ
  * Flick      (listens for flick in any direction)
  * Pitch
  * Roll

  If atomic Wii Event strings are joined together in a tuple, the events will be treated as optional. Only one 
  event from the tuple is required. In other words ('ButtonAPress', 'ButtonBPress') allows a user to press either
  'A' or 'B' but not both.

  If atomic Wii Event strings are joined in a set, the events will be treated as a combination. That is, all the events
  must happen almost simultaneously. So set(('ButtonAPress', 'ButtonBPress')) means that the user has to press
  both 'A' and 'B' at the same time. 

.. [Bindings] A sequence of Wii Events that is 
.. [GameEvents] A representation of something that should happen in the game. Consists simply of a game method name
                (prefixed with 'bind\_') and the parameters dictionary.

Game Event Listener
-------------------
The Game Event Listener is a small utility that receives Game Events from the Game Event Parser, looks up the corresponding
function in the game logic, and calls the function. As mentioned above, a Game Event is really just a function name with 
a corresponding parameter array. The function name should be one of the functions in the game class, with the additional
bindings prefix ('bind\_'). Since the Game Event Listener must have access to the game class's
member functions, it must be run as a thread started from inside the game.  

The second important task of the Game Event Listener is to start the processes for the Wii Event Parser and the Game Event
Parser. Since the Game Event Listener is essentially worthless unless the rest of the framework is running, calling the
start method will use Python's subprocess module to start the parsers. Both parsers have a small utility script, called 
startWEP.py and startGEP.py, that create a parser object, then starts the parser listening; the Game Event Listener 
runs these scripts to start the parsers. 

Besides the WEPControl, the Game Event Listener will likely be the only part of the framework a game has to directly
interact with. Luckily the Game Event Listener is easy to set up. The game needs to create a *GameEventListener* object
and pass the following arguments to the constructor: a reference to the game object, a string containing the name of the
bindings file,  a string for the name of the bindings class within the bindings file, and an integer representing the
number of players that will be playing the game. After creating the object, calling the *start* method will create the 
parser processes. Calling the *end* method will shut down the entire framework (including killing the parser processes).

For example, if we had a bindings class called TestGameBindings defined in a file called 'bindings.py' and we wanted 
to play a game with 5 players, we would start the framework with the following::
	
	import GameEventListener  # The import might need to be adjusted depending on your system path and game location

	game = TestGame()  # Do whatever is necessary to set up the game
	listener = GameEventListener.GameEventListener(game, 'bindings.py', 'TestGameBindings', 5)
	listener.start()
	...
		play the game 
	...
	listener.end()
	 

The Game
--------
**Network Game** 
  The Network Game is actually a port of a game from C# to Python. This game was originally completed by a team in the CSM User Interface Class.
  The structure of the new version is quite similar, but if you wish to view the original please view their code at http://wii-routing-game.googlecode.com/svn/trunk
  
  Note: All files referenced in this section are located in the src/NetworkGame directory within the wii2010-repo directory.

    The actual structure of the code is relatively simple and contains four classes.

    *The Player class* is used to represent human players in the game. This class holds a wiiID variable which is just an integer that 
    connects the Player to a Wiimote's data in the Wii Event Parser. Player objects also hold a color varaible which connects them to a 
    specific RouterNode when the Game is being played. 

    *The RouterNode class* represents a Network Node for use in the game. Objects of this class have a color variable that identifies what
    color Packet or, more appropriately, what string they accept, since in the Game logic Packets are merely strings of color names, “RED”,
    “BLUE”, :GREEN” etc. RouterNode objects also hold a queue that holds all the “Packets” at that node. The RouterNode also holds the
    coordinates as a percentage of the screen. These coordinates  represent where the node should appear on the screen.

    *The Game class* handles the actual integration with the Game Event Parsers. When the startGame function is called the Game object will
    start the Game Event Listener and tells it how many players to listen for. The Game class also holds all the functions that are bound to 
    Wiimote actions, and determines whether the Wiimote associated the action actually represents a player in the game.

    *The Map class* handles all the core game functionality. It handles creating, sending, and receiving of packets. Also, it checks if there
    is an edge in the direction a player flicks. It also handles all AI for computer players.

    *The Level file*, while not a class, is very important as it holds the functions that construct all the different Map layouts in the Game.
    Each layout is given their own function, that builds that specific Map. If you are interested in adding a level, please see the Test_Level()
    function in the Level.py file for a detailed walkthrough of how to build a level. As for accessing the Level throught the GUI, you would need
    to simply add a button that called a function you added that sets the Game's mapOn variable to the Map created by your custom level. This 
    addition should only take an extra 5 lines of code between creating the new button and writing the function, but you will also need to add the
    new button object to the MapSelection class's clickables variables, which lets the GUI know to check if the cursor clicks the Button. For exactly
    how to implement this please see the MapSelectionScreen.py file for how the current four levels are implemented. Specifically the addLevelButtons
    function which builds the buttons and adds them to the screen and the four startLevel functions that actually call the Levels functions to build maps
    and tell the Gui to start displaying them.

**Binary Tree Game**
  The Binary Tree Game is a brand new game created by CSM Lecturer Keith Hellman. The current version of the Game contains only one Game Mode, but is
  abstracted in the interest of allowing future Game Modes. The two main Game Logic abstractions are as follows:

  *The Player class* has been developed as the parent class to all player roles that will be used in future game modes. The Player class contains a current variable to determine what a player is messing with. For our game mode, the Sorter subclass used its current to designate the index in the opponent's queue it was looking at. The Player also has a selected variable that is supposed to act as boolean to tell whether a player has something selected and then provide different functionality. The Player class has functions called deselct and select, which set the selected variable to None and to the Player object's current respectively. However, setting selected to current and None is not necessary. Due to Python's dynamic typing, this selected variable can be easily overwritten within a subclass to best fit the needs of the author for their game mode. The Player class also holds the wiiID of each player's wiimotes allowing a way to connect a wiimote to a game logic player. The Player class also holds a team variable, which, while not as critical as the first three variables, is handy to include. Since this game is meant for a classroom setting, teamwork is likely encouraged and usually allows for a larger number of players to play simultaneously. The final and most important piece of the Player class is the ability to have dummy functions. When a binding is completed and the GameMode's bound function is called, the Player object that is found can simply call the appropriate function without error-checking to see if that kind of player can actually perform that action. In our game, the Rotator subclass was the only role that had an action performed when a Wiimote was rolled, and the use of these dummy functions allowed fro the Inserter and Sorter subclasses to roll their Wiimotes without any ill effects. Also, obviously, this abstraction allows different subclasses to perform different actions for the same function call (i.e. Sorters shove function moved its current only left or right one number while an Inserter's shove function tried to insert a number into the tree). The final piece of the Player class is the instantiation.

   *The GameMode class* is the second class new game modes will need to interact with. This is, as its name suggests, a class intended to be a super class to all other Game Modes. The intention of this is to maintain a standard way to interact with the GUI across Game modes. The GameMode comes with functions to get the GUI's screen(Why this is important will be explained in the following GUI section) and to return to the Main Menu of the game. The things the subclasses will need to do in order to interface with the rest of the system on an indiviual level are: Setting up the Bindings and Setting up the GUI Screen.

    - Setting up bindings
        All programmers need to build is the GameEventListener based on their bindings class. A line of code that should look like this: *self.listener = GameEventListener(self,'Bindings.py','PlayerSelectionBindings', 6)* Then, all that needs to be done to begin receiving wiimote events in the game is calling listener.start().

    - Setting up the GUI screen
        A Screen in the sense of the Binary Tree Game and Network Game is just a class with a Pygame Surface called *surface* as its only required variable. Essentially all a programmer needs to worry about is building their screen and blitting any non-Sprite objects to this surface. Then, if the programmer has Sprites that need to be updated, they need to add them to a SpriteGroup called *allsprites*. This way the overall GUI structure that actually builds the window that is displayed knows to draw the Screen's Sprite Objects as well. Also, a programmer needs to add any buttons or anything that can be clicked into a list called *clickables*, so that the overall GUI structure knows to check if the cursor clicks on them. Also, a programmer can choose to have a *running* variable that represents a boolean to tell the overall GUI whether the screen should continue to be run or not. Also, a programmer can add a function called *getInput* that takes a list of Pygame Events. This allows a programmer to incorporate keyboard or mouse input specific to their screen. As far as running this screen, all a programmer must do is create an object iof their Screen class, and call this function from within their GameMode subclass, *self.gui.runScreen(yourScreen)* where yourScreen is the object of the Game Mode subclass. This line tells the overall GUI to set the screen that is being displayed to yourScreen, grab the allsprites and clickables from yourScreen and add them to its corresponding variables, and then run a loop that constanly updates the screen and the sprites while allowing user input. With these steps a fully functioning screen should be displayed.

Interactions
------------
In its simplest form, two processes need to be run. The first starts the WEPControl and sets up wiimotes either via GUI or
by the command line. The other process is within the game, which is simply called by setting up a GameEventListener.
The game Event Listener sets up both the GameEventParser and the WiiEventParser for a particular game.  Apart
from that, the future developer can focus on game logic with the wiimote input taken care of.
