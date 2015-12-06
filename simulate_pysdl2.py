# Simulate (a Simon clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

#Ported to PySDL2 by Robert Winkler
#http://robertwinkler.com

import sdl2.ext
import sdl2
from sdl2 import sdlgfx, sdlmixer

import random, sys
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
	global clickedButton, BEEP1, BEEP2, BEEP3, BEEP4

	sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO|sdl2.SDL_INIT_AUDIO)

	window = sdl2.ext.Window("Simulate", size=(WINDOWWIDTH, WINDOWHEIGHT))
	ren = sdl2.ext.Renderer(window)
	ren.blendmode = sdl2.SDL_BLENDMODE_BLEND
	
	window.show()

	font_file = sysfont.get_font("freesans", sysfont.STYLE_BOLD)
	font_manager = sdl2.ext.FontManager(font_file, size=16)

	#fontmanager=font_manager will be default_args passed to every sprite creation method
	sprite_factory = sdl2.ext.SpriteFactory(renderer=ren, fontmanager=font_manager, free=True)
	sprite_renderer = sprite_factory.create_sprite_render_system(window)



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

	#directions text sprite
	info_text = make_text(sprite_factory, "Match the pattern by clicking on the button or using the Q, W, A, S keys.", 10, WINDOWHEIGHT-25)

	clickedButton = []
	while True:
		ren.fill((0, 0, WINDOWWIDTH, WINDOWHEIGHT), bgColor)
		drawButtons()


		score_text = make_text(sprite_factory, "Score: "+str(score), WINDOWWIDTH - 100, 10)
		sprite_renderer.render(score_text)
		sprite_renderer.render(info_text)

		handle_events()

		if not waitingForInput:
			# play the pattern
			ren.present()
			sdl2.SDL_Delay(1000)
			pattern.append(random.choice((YELLOW, BLUE, RED, GREEN)))
			for button in pattern:
				handle_events()
				flashButtonAnimation(button)
				sdl2.SDL_Delay(FLASHDELAY)
			waitingForInput = True
		else:
			# wait for the player to enter buttons
			if clickedButton and clickedButton[0] == pattern[currentStep]:
				# pushed the correct button
				flashButtonAnimation(clickedButton[0])
				currentStep += 1
				lastClickTime = sdl2.SDL_GetTicks()
				
				#could replace with collections.deque but premature optimizations and all that
				clickedButton.pop(0)

				if currentStep == len(pattern):
					# pushed the last button in the pattern
					changeBackgroundAnimation()
					score += 1
					waitingForInput = False
					currentStep = 0 # reset back to first step
					clickedButton.clear()

			elif (clickedButton and clickedButton[0] != pattern[currentStep]) or (currentStep != 0 and sdl2.SDL_GetTicks() - TIMEOUT*1000 > lastClickTime):
				# pushed the incorrect button, or has timed out
				gameOverAnimation()
				# reset the variables for a new game:
				pattern = []
				clickedButton.clear()
				currentStep = 0
				waitingForInput = False
				score = 0
				sdl2.SDL_Delay(1000)
				changeBackgroundAnimation()

		ren.present()
		sdl2.SDL_Delay(FPS)

	
	shutdown()


#will ignore clicks while busy doing animation etc.
#ie you can't click faster than it can flash them
def handle_events():
	global clickedButton
	for event in sdl2.ext.get_events():
		if event.type == sdl2.SDL_QUIT:
			shutdown()
		elif event.type == sdl2.SDL_MOUSEBUTTONUP:
			mousex, mousey = event.button.x, event.button.y
			button = getButtonClicked(mousex, mousey)
			if button:
			    clickedButton.append(button)
		elif event.type == sdl2.SDL_KEYDOWN:
			sym = event.key.keysym.sym
			if sym == sdl2.SDLK_ESCAPE:
				shutdown()
			elif sym == sdl2.SDLK_q:
				clickedButton.append(YELLOW)
			elif sym == sdl2.SDLK_w:
				clickedButton.append(BLUE)
			elif sym == sdl2.SDLK_a:
				clickedButton.append(RED)
			elif sym == sdl2.SDLK_s:
				clickedButton.append(GREEN)
	

def make_text(sprite_factory, text, top, left):
	button = sprite_factory.from_text(text)
	button.position = top, left
	return button


def shutdown():
	sdlmixer.Mix_CloseAudio()
	#sdl2.ext.quit()
	sdl2.SDL_Quit()
	sys.exit()
	#do I need to do anything else here?


def drawButtons():
	ren.fill(YELLOWRECT, YELLOW)
	ren.fill(BLUERECT, BLUE)
	ren.fill(REDRECT, RED)
	ren.fill(GREENRECT, GREEN)


def flashButtonAnimation(color, animationSpeed=50):
	if color == YELLOW:
		sound = BEEP1
		flashColor = BRIGHTYELLOW
		rectangle = YELLOWRECT
	elif color == BLUE:
		sound = BEEP2
		flashColor = BRIGHTBLUE
		rectangle = BLUERECT
	elif color == RED:
		sound = BEEP3
		flashColor = BRIGHTRED
		rectangle = REDRECT
	elif color == GREEN:
		sound = BEEP4
		flashColor = BRIGHTGREEN
		rectangle = GREENRECT

	r, g, b, a = flashColor

	channel = sdlmixer.Mix_PlayChannel(-1, sound, 0)
	for start, end, step in ((0, 255, 1), (255, 0, -1)): # animation loop
		for alpha in range(start, end, animationSpeed * step):
			handle_events()
			ren.fill(rectangle, color)
			ren.fill(rectangle, (r,g,b,alpha))
			ren.present()
			sdl2.SDL_Delay(FPS)

	ren.fill(rectangle, color)
	ren.present()

def hit_rect(rect, pt):
	"""returns True if pt is inside rect (rect is tuple (x, y, w, h))"""
	if pt[0] >= rect[0] and pt[0] <= rect[0] + rect[2] and pt[1] >= rect[1] and pt[1] <= rect[1]+rect[3]:
		return True
	return False

def hit_bbox(box, pt):
	"""returns True if pt is inside box (box is tuple (x1, y1, x2, y2))"""
	if pt[0] >= box[0] and pt[0] <= box[2] and pt[1] >= box[1] and pt[1] <= box[3]:
		return True
	return False

def getButtonClicked(x, y):
	if hit_rect(YELLOWRECT, (x, y)):
		return YELLOW
	elif hit_rect(BLUERECT, (x, y)):
		return BLUE
	elif hit_rect(REDRECT, (x, y)):
		return RED
	elif hit_rect(GREENRECT, (x, y)):
		return GREEN
	return None


def changeBackgroundAnimation(animationSpeed=40):
	global bgColor
	newBgColor = sdl2.ext.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

	r, g, b, a = newBgColor
	for alpha in range(0, 255, animationSpeed): # animation loop
		handle_events()
		ren.fill((0, 0, WINDOWWIDTH, WINDOWHEIGHT), (r,g,b,alpha))
		
		drawButtons() # redraw the buttons on top of the tint

		ren.present();
		sdl2.SDL_Delay(FPS)

	bgColor = newBgColor


def gameOverAnimation(color=WHITE, animationSpeed=50):
	# play all beeps at once, then flash the background
	
	# play all four beeps at the same time, roughly.
	channel = sdlmixer.Mix_PlayChannel(-1, BEEP1, 0)
	channel = sdlmixer.Mix_PlayChannel(-1, BEEP2, 0)
	channel = sdlmixer.Mix_PlayChannel(-1, BEEP3, 0)
	channel = sdlmixer.Mix_PlayChannel(-1, BEEP4, 0)

	r, g, b, a = color
	for i in range(3): # do the flash 3 times
		for start, end, step in ((0, 255, 1), (255, 0, -1)):
			# The first iteration in this loop sets the following for loop
			# to go from 0 to 255, the second from 255 to 0.
			for alpha in range(start, end, animationSpeed * step): # animation loop
				# alpha means transparency. 255 is opaque, 0 is invisible
				handle_events()

				ren.fill((0, 0, WINDOWWIDTH, WINDOWHEIGHT), (r,g,b,alpha))
				drawButtons()

				ren.present()
				sdl2.SDL_Delay(FPS)



if __name__ == '__main__':
	main()
