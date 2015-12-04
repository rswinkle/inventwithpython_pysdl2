# Simulate (a Simon clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

#Ported to PySDL2 by Robert Winkler
#http://robertwinkler.com

import sdl2.ext
import sdl2
from sdl2 import sdlgfx, sdlmixer

import random, sys, ctypes
from utils import sysfont



FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FLASHSPEED = 500 # in milliseconds
FLASHDELAY = 200 # in milliseconds
BUTTONSIZE = 200
BUTTONGAPSIZE = 20
TIMEOUT = 4 # seconds before game over if no button is pushed.

#                              R    G    B
WHITE        = sdl2.ext.Color(255, 255, 255)
BLACK        = sdl2.ext.Color(  0,   0,   0)
BRIGHTRED    = sdl2.ext.Color(255,   0,   0)
RED          = sdl2.ext.Color(155,   0,   0)
BRIGHTGREEN  = sdl2.ext.Color(  0, 255,   0)
GREEN        = sdl2.ext.Color(  0, 155,   0)
BRIGHTBLUE   = sdl2.ext.Color(  0,   0, 255)
BLUE         = sdl2.ext.Color(  0,   0, 155)
BRIGHTYELLOW = sdl2.ext.Color(255, 255,   0)
YELLOW       = sdl2.ext.Color(155, 155,   0)
DARKGRAY     = sdl2.ext.Color( 40,  40,  40)
bgColor = BLACK

XMARGIN = int((WINDOWWIDTH - (2 * BUTTONSIZE) - BUTTONGAPSIZE) / 2)
YMARGIN = int((WINDOWHEIGHT - (2 * BUTTONSIZE) - BUTTONGAPSIZE) / 2)

# rectangles for each of the four buttons
YELLOWRECT = (XMARGIN, YMARGIN, BUTTONSIZE, BUTTONSIZE)
BLUERECT   = (XMARGIN + BUTTONSIZE + BUTTONGAPSIZE, YMARGIN, BUTTONSIZE, BUTTONSIZE)
REDRECT    = (XMARGIN, YMARGIN + BUTTONSIZE + BUTTONGAPSIZE, BUTTONSIZE, BUTTONSIZE)
GREENRECT  = (XMARGIN + BUTTONSIZE + BUTTONGAPSIZE, YMARGIN + BUTTONSIZE + BUTTONGAPSIZE, BUTTONSIZE, BUTTONSIZE)



def main():
	#cause I don't want to pass these around
	global ren, sprite_factory, sprite_renderer
	global reset_button, new_button, solve_button

	#this only initializes video subsystem
	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO|sdl2.SDL_INIT_AUDIO)

	window = sdl2.ext.Window("Slide Puzzle", size=(WINDOWWIDTH, WINDOWHEIGHT))
	ren = sdl2.ext.Renderer(window)
	window.show()

	font_file = sysfont.get_font("freesans", sysfont.STYLE_BOLD)
	font_manager = sdl2.ext.FontManager(font_file, size=16)

	#fontmanager=font_manager will be default_args passed to every sprite creation method
	sprite_factory = sdl2.ext.SpriteFactory(renderer=ren, fontmanager=font_manager, free=True)
	sprite_renderer = sprite_factory.create_sprite_render_system(window)



	#I should have to initialize sdl's audio subsystem before I do this
	#sdl2.SDL_Init(sdl2.SDL_INIT_AUDIO) # or
	#sdl2.SDL_InitSubSystem(sdl2.SDL_INIT_AUDIO)
	sdlmixer.Mix_Init(sdlmixer.MIX_INIT_OGG)
	sdlmixer.Mix_OpenAudio(44100, sdlmixer.MIX_DEFAULT_FORMAT, 2, 1024)
	BEEP1 = sdlmixer.Mix_LoadWAV(b"beep1.ogg")
	BEEP2 = sdlmixer.Mix_LoadWAV(b"beep2.ogg")
	BEEP3 = sdlmixer.Mix_LoadWAV(b"beep3.ogg")
	BEEP4 = sdlmixer.Mix_LoadWAV(b"beep4.ogg")

	#channel = sdlmixer.Mix_PlayChannel(-1, BEEP1, 0)

	# Initialize some variables for a new game
	pattern = [] # stores the pattern of colors
	currentStep = 0 # the color the player must push next
	lastClickTime = 0 # timestamp of the player's last button push
	score = 0
	# when False, the pattern is playing. when True, waiting for the player to click a colored button:
	waitingForInput = False


	running = True
	while running:
		clickedButton = None
		ren.clear(bgColor)
		drawButtons()


		ren.present()

		checkForQuit()
		for event in sdl2.ext.get_events():
			if event.type == sdl2.SDL_KEYDOWN:
				sym = event.key.keysym.sym
				if sym == sdl2.SDLK_q:
					clickedButton = YELLOW
				elif sym == sdl2.SDLK_w:
					clickedButton = BLUE
				elif sym == sdl2.SDLK_a:
					clickedButton = RED
				elif sym == sdl2.SDLK_s:
					clickedButton = GREEN
	
	
	shutdown()


#TODO expand for ESC
def checkForQuit():
	eventarray = (sdl2.SDL_Event * 50)()
	numevents = sdl2.SDL_PeepEvents(eventarray, 50, sdl2.SDL_PEEKEVENT, sdl2.SDL_FIRSTEVENT, sdl2.SDL_LASTEVENT)
	for i in range(numevents):
		if eventarray[i].type == sdl2.SDL_QUIT:
			shutdown()
		elif eventarray[i].type == sdl2.SDL_KEYDOWN:
			sym = eventarray[i].key.keysym.sym
			if sym == sdl2.SDLK_ESCAPE:
				shutdown()



def shutdown():
	sdlmixer.Mix_CloseAudio()
	sdl2.SDL_Quit()
	#sdl2.ext.quit()
	sys.exit()
	#do I need to do anything else here?


def drawButtons():
	ren.fill(YELLOWRECT, YELLOW)
	ren.fill(BLUERECT, BLUE)
	ren.fill(REDRECT, RED)
	ren.fill(GREENRECT, GREEN)





if __name__ == '__main__':
	main()
