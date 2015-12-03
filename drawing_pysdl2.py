import ctypes
import sdl2.ext
from sdl2 import sdlgfx


sdl2.ext.init()

window = sdl2.ext.Window("Drawing", size=(400, 300))
window.show()

context = sdl2.ext.Renderer(window)

# set up the colors
BLACK = sdl2.ext.Color(  0,   0,   0)
WHITE = sdl2.ext.Color(255, 255, 255)
RED   = sdl2.ext.Color(255,   0,   0)
GREEN = sdl2.ext.Color(  0, 255,   0)
BLUE  = sdl2.ext.Color(  0,   0, 255)



xlist = [146, 291, 236, 56, 0]
ylist = [0, 106, 277, 277, 106]
ptcnt = len(xlist)
xarray = (sdl2.Sint16 * ptcnt)()
yarray = (sdl2.Sint16 * ptcnt)()
for i in range(ptcnt):
	xarray[i] = xlist[i]
	yarray[i] = ylist[i]
xptr = ctypes.cast(xarray, ctypes.POINTER(sdl2.Sint16))
yptr = ctypes.cast(yarray, ctypes.POINTER(sdl2.Sint16))

def draw_shapes():
	context.clear(WHITE)
	sdlgfx.filledPolygonRGBA(context.renderer, xptr, yptr, ptcnt, *GREEN)
	sdlgfx.filledCircleRGBA(context.renderer, 300, 50, 20, *BLUE) 
	sdlgfx.ellipseRGBA(context.renderer, 320, 240, 20, 40, *RED)
	sdlgfx.boxRGBA(context.renderer, 200, 150, 300, 200, *RED)

	sdlgfx.thickLineRGBA(context.renderer, 60, 60, 120, 60, 4, *BLUE)
	sdlgfx.lineRGBA(context.renderer, 120, 60, 60, 120, *BLUE)
	sdlgfx.thickLineRGBA(context.renderer, 60, 120, 120, 120, 4, *BLUE)


	points = [380, 280, 382, 282, 384, 284, 386, 286, 388, 288]
	context.draw_point(points, BLACK)


draw_shapes()
context.present()

running = True
while running:
	for event in sdl2.ext.get_events():
		if event.type == sdl2.SDL_QUIT:
			running = False
			break
		elif event.type == sdl2.SDL_KEYDOWN:
			if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
				running = False
				break
		elif event.type == sdl2.SDL_WINDOWEVENT:
			if event.window.event == sdl2.SDL_WINDOWEVENT_EXPOSED:
				draw_shapes()
				context.present()

	sdl2.SDL_Delay(10)


sdl2.ext.quit()

