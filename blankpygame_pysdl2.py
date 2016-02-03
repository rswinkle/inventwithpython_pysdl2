import sdl2.ext, sys

sdl2.ext.init()

window = sdl2.ext.Window("Hello PySDL2 World", size=(400, 300))
window.show()
renderer = sdl2.ext.Renderer(window)
while True:
	for event in sdl2.ext.get_events():
		if event.type == sdl2.SDL_QUIT:
			sdl2.ext.quit()
			sys.exit()
	renderer.present()
