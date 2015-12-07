import sdl2.ext
import sdl2
from sdl2 import sdlgfx

from utils import sysfont
from random import randint

import sys



def draw_polygon(renderer, points, color):
	n_pts = len(points)
	xarray = (sdl2.Sint16 * n_pts)()
	yarray = (sdl2.Sint16 * n_pts)()

	for i in range(n_pts):
		xarray[i] = points[i][0]
		yarray[i] = points[i][1]
	#unecessary
	#xptr = ctypes.cast(xarray, ctypes.POINTER(sdl2.Sint16))
	#yptr = ctypes.cast(yarray, ctypes.POINTER(sdl2.Sint16))

	sdlgfx.filledPolygonRGBA(renderer, xarray, yarray, n_pts, *color)
	#do I need to del or somehow free the arrays here?
	#test seems to indicate that I don't



WIDTH = 640
HEIGHT = 480

BLACK = sdl2.ext.Color(  0,   0,   0)
WHITE = sdl2.ext.Color(255, 255, 255)
RED   = sdl2.ext.Color(255,   0,   0)
GREEN = sdl2.ext.Color(  0, 255,   0)
BLUE  = sdl2.ext.Color(  0,   0, 255)

colors = [BLACK, WHITE, RED, GREEN, BLUE]

def test1(num_polys):
	for i in range(num_polys):
		points = [(randint(0, WIDTH), randint(0, HEIGHT)) for i in range(randint(3, 10))]
		draw_polygon(ren.renderer, points, colors[randint(0, 4)])
		ren.present()

def test_surface_drawing():
	win_surf = window.get_surface()

	test1 = sprite_factory.from_text("A text sprite")
	degrees = 0
	while degrees < 180:
		ren.clear() #fill?
		rot = sdlgfx.rotozoomSurface(test1.surface, degrees, 3, sdlgfx.SMOOTHING_ON)
		
		#same lame copy necessary as below
		tmp = rot.contents
		pos = WIDTH//2 - tmp.w//2, HEIGHT//2 -tmp.h//2

		sdl2.SDL_BlitSurface(rot, None, win_surf, sdl2.rect.SDL_Rect(pos[0], pos[1], 0, 0))

		degrees += 1
		sdl2.SDL_Delay(1000//90)
		window.refresh() #equ to sdl2.SDL_UpdateWindowSurface(window.window) ...?

def test_surface_sprites():
	test1 = sprite_factory.from_text("A text sprite")
	degrees = 0
	while degrees < 360:
		if get_events([sdl2.SDL_QUIT]):
			shutdown()
		ren.clear() #fill?
		rot = sdlgfx.rotozoomSurface(test1.surface, degrees, 3, sdlgfx.SMOOTHING_ON)

		#print(type(rot), type(rot.contents))
		#<class 'sdl2.surface.LP_SDL_Surface'> <class 'sdl2.surface.SDL_Surface'>

		#this is lame ... from_surface takes sdl2.surface.SDL_Surface which means calling contents
		#which creates a copy
		#Note that ctypes does not have OOR (original object return), it constructs a new, equivalent object each time you retrieve an attribute
		#so rot.contents creates a new ~52 byte surface
		rot = sprite_factory.from_surface(rot.contents)
		rot.position = WIDTH//2 - rot.size[0]//2, HEIGHT//2 -rot.size[1]//2


		degrees += 1
		sdl2.SDL_Delay(1000//90)
		sprite_renderer.render(rot)
		ren.present()


#change types to OR'd flags?  would mean I don't have to wrap a single
#type in []
def get_events(types=None):
	events = []
	for event in sdl2.ext.get_events():
		if not types or event.type in types:
			events += [event]
	
	return events


def main():
	global ren, window, sprite_factory, sprite_renderer
	sdl2.ext.init()

	window = sdl2.ext.Window("testing", size=(WIDTH, HEIGHT))
	window.show()

	ren = sdl2.ext.Renderer(window, flags=sdl2.SDL_RENDERER_SOFTWARE)
	font_file = sysfont.get_font("freesans")
	print(font_file)
	font_manager = sdl2.ext.FontManager(font_file, size=24)

	#fontmanager=font_manager will be default_args passed to every sprite creation method
	sprite_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE, renderer=ren, fontmanager=font_manager, free=True)
	sprite_renderer = sprite_factory.create_sprite_render_system(window)

	#test1(1000)
	#test_surface_drawing()
	#sdl2.SDL_Delay(1000)
	#test_surface_sprites()

	ren.present()

	while True:
		for event in get_events():
			if event.type == sdl2.SDL_QUIT:
				shutdown()
			elif event.type == sdl2.SDL_MOUSEBUTTONUP:
				mousex, mousey = event.button.x, event.button.y
			elif event.type == sdl2.SDL_KEYDOWN:
				sym = event.key.keysym.sym
				if sym == sdl2.SDLK_ESCAPE:
					shutdown()

		test_surface_sprites()



def shutdown():
	sdl2.ext.quit()
	sys.exit()


if __name__ == '__main__':
	main()
