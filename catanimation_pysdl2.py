import sdl2.ext

WHITE = sdl2.ext.Color(255, 255, 255)

sdl2.ext.init()

window = sdl2.ext.Window("Drawing", size=(400, 300))
window.show()
renderer = sdl2.ext.Renderer(window)

factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
print(type(renderer), "\n", type(renderer.renderer))
sprite = factory.from_image("cat.png")

spriterenderer = factory.create_sprite_render_system(window)

RIGHT = 1
LEFT = 2
UP = 3
DOWN = 4
catx = 10
caty = 10
direction = RIGHT


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

	if direction == RIGHT:
		catx += 5
		if catx == 280:
			direction = DOWN
	elif direction == LEFT:
		catx -= 5
		if catx == 10:
			direction = UP
	elif direction == UP:
		caty -= 5
		if caty == 10:
			direction = RIGHT
	elif direction == DOWN:
		caty += 5
		if caty == 220:
			direction = LEFT

	sprite.position = catx, caty
	renderer.clear(WHITE)
	spriterenderer.render(sprite)
	sdl2.SDL_Delay(10)


sdl2.ext.quit()

