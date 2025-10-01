import pygame
from math import pi, exp, sqrt

class WheelAnimation(pygame.sprite.Sprite):
	image_width = 400
	def __init__(self, scaling=0.5):
		super().__init__()
		self.moving = False
		self.sprites = []
		# self.dtheta_d = 5
		# for angle in range(-180, 180, self.dtheta_d):
		# 	fname = 'frames/{}.png'.format(angle).replace('-','m')
		# 	image = pygame.image.load(fname)
		# 	image_scaled = pygame.transform.scale(image, (int(image.size[0] * scaling), int(image.size[1] * scaling)))
		# 	self.sprites.append(image_scaled)
		for fname in ['frames/tire.png', 'frames/tire_s.png', 'frames/wheel.png', 'frames/wheel_s.png']:
			image = pygame.image.load(fname)
			image_scaled = pygame.transform.scale(image, (int(image.size[0] * scaling), int(image.size[1] * scaling)))
			self.sprites.append(image_scaled)

		self.rect = image_scaled.get_rect()
		self.radius = self.rect.width/2
		self.image = self.sprites[0] #temporary, should not be displayed

	def planroll(self, ctr_x0, ctr_x1, ctr_y, theta0=0, vmin=40, vmax=200, T=5):
		self.ctr_x0 = ctr_x0
		self.ctr_x1 = ctr_x1
		self.ctr_y = ctr_y
		self.theta0 = theta0
		self.rect.topleft = [self.ctr_x0 - self.radius, self.ctr_y - self.radius]

		#horizontal speed v vs. t shall be an upside-down Gaussian: v = vmax - gaussian + vmin
		self.T = T  # time to complete motion, s
		S = self.ctr_x1 - self.ctr_x0  # total distance to go, px
		self.vmin = vmin # px/s
		self.vmax = vmax  # px/s
		#solve for a, the parameter of the Gaussian, using the integral:
		# int v dt = (vmax + vmin)T - vmax sqrt(pi/a) = S, then rearrange for a:
		a = (vmax ** 2) * pi / (S ** 2 - 2 * T * S * (vmax + vmin) + (T ** 2) * ((vmax + vmin) ** 2))
		self.a = a

	def go(self):
		self.moving = True

	def get_dx(self, t, dt_approx):
		vmin = self.vmin
		vmax = self.vmax
		a = self.a
		T = self.T
		v = vmax * (1 - exp(-1 * a * (t-T/2)**2)) + vmin
		return v * dt_approx * self.moving

	def update(self, deltax):
		deltatheta = self.theta0 + (180/pi)*deltax/self.radius

		#idx_theta = deltatheta/self.dtheta_d
		#self.current_sprite = round(idx_theta) % len(self.sprites)
		if self.moving == True:
			self.rect.topleft = [self.ctr_x0 - self.radius + deltax, self.ctr_y - self.radius]
			if self.ctr_x0 + deltax >= self.ctr_x1:
				self.moving = False

		def rot_center(image, angle):
			"""rotate an image while keeping its center and size"""
			orig_rect = image.get_rect()
			rot_image = pygame.transform.rotate(image, angle)
			rot_rect = orig_rect.copy()
			rot_rect.center = rot_image.get_rect().center
			rot_image = rot_image.subsurface(rot_rect).copy()
			return rot_image

		tire = self.sprites[0].copy() #rot_center(self.sprites[0], -1*deltatheta)
		tire.blit(self.sprites[1], tire.get_rect())
		wheel = rot_center(self.sprites[2], -1*deltatheta)
		tire.blit(wheel, tire.get_rect())
		tire.blit(self.sprites[3], tire.get_rect())
		self.image = tire


def splash(disp1, clock, screen_width, screen_height):
    # Creating the sprites and groups
    moving_sprites = pygame.sprite.Group()
    scaling = 1
    wheel = WheelAnimation(scaling =scaling)
    wheel.planroll(ctr_x0=0 - wheel.radius, ctr_x1=screen_width + wheel.radius, ctr_y=screen_height // 2, theta0=180, vmin=40, vmax=200, T=7)
    moving_sprites.add(wheel)

    fps_max = 60
    dt_approx = (1/fps_max)

    wheel.go()
    wheel_deltax = 0
    wheel_t = 0
    while wheel_deltax < wheel.ctr_x1 - wheel.ctr_x0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        wheel_deltax += wheel.get_dx(wheel_t, dt_approx)

        # Drawing
        disp1.fill((0, 0, 0))
        moving_sprites.draw(disp1)
        moving_sprites.update(wheel_deltax)

        pygame.display.flip()
        clock.tick(fps_max)
        wheel_t += dt_approx * wheel.moving