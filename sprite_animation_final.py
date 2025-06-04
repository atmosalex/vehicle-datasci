import pygame, sys
import anim_wheel


# General setup
pygame.init()
clock = pygame.time.Clock()

# Game Screen
screen_width = 800
screen_height = 400
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Sprite Animation")

# Creating the sprites and groups
moving_sprites = pygame.sprite.Group()
wheel = anim_wheel.WheelAnimation(scaling =1)
wheel.planroll(ctr_x0 = 0 - wheel.radius, ctr_x1 = screen_width + wheel.radius, ctr_y=200, theta0=0, vmin=40, vmax=200, T=7)
moving_sprites.add(wheel)


fps_max = 60
dt_approx = (1/fps_max)
wheel_t = 0
wheel_deltax = 0

wheel.go()
wheel_deltax = 0
wheel_t = 0
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		# if event.type == pygame.KEYDOWN:
		# 	wheel.go()
		# 	wheel_deltax = 0
		# 	wheel_t = 0

	wheel_deltax += wheel.get_dx(wheel_t, dt_approx)

	# Drawing
	screen.fill((0,0,0))
	moving_sprites.draw(screen)
	moving_sprites.update(wheel_deltax)

	pygame.display.flip()
	clock.tick(fps_max)
	wheel_t += dt_approx * wheel.moving
