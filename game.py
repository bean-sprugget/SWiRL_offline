import pygame, sys, math

pygame.init()

screen = pygame.display.set_mode()
(width, height) = pygame.display.get_window_size()
pygame.display.set_caption("SWiRL")

# actual code

red = (240, 20, 20)
blue = (20, 20, 240)
white = (255, 255, 255)
transparent = (100, 100, 100)

max_speed = 10
rocket_speed = 30

launch_force = 50

class Dummy(pygame.sprite.Sprite):
  def __init__(self, s_width, s_height):
    pygame.sprite.Sprite.__init__(self)

    self.airborne = False
    self.num_jumps = 2
    self.speed = [0, 0]
    self.color = blue
    self.position = ((3 * width) / 4, height - (s_height / 2) - 1)

    # set the image to 's_width' x 's_height' rectangle of 'color' color
    self.image = pygame.Surface([s_width, s_height])
    self.image.fill(self.color)

    self.rect = self.image.get_rect() # make object have same dimensions as the image
    self.rect.center = self.position

  def movement(self):
    if self.airborne:
      self.speed[1] += 2 # gravity
    else:
      self.speed[0] *= 0.75 # friction
      self.speed[1] = 0
      self.rect.bottom = height

    if self.rect.left < 0:
      self.rect.left = 0
      self.speed[0] = 0
    if self.rect.right > width:
      self.rect.right = width
      self.speed[0] = 0

  def launched(self, angle):
    self.rect = self.rect.move([0, -1])
    self.speed[0] += math.cos(angle) * launch_force
    self.speed[1] += math.sin(angle) * launch_force

  def update(self):
    self.airborne = self.rect.bottom < height

    self.movement()

    self.rect = self.rect.move(self.speed)

class Rocket(pygame.sprite.Sprite):
  def __init__(self, diameter, spawn_pos, angle):
    pygame.sprite.Sprite.__init__(self)

    self.image = pygame.Surface([diameter, diameter])
    self.image.fill(transparent)
    self.image.set_colorkey(transparent)
    pygame.draw.circle(self.image, (0, 0, 0), (diameter // 2, diameter // 2), diameter // 2)
    self.rect = self.image.get_rect()
    self.rect.center = spawn_pos

    self.speed = [rocket_speed * math.cos(angle), rocket_speed * math.sin(angle)]

  def update(self, dummy):
    self.rect = self.rect.move(self.speed)

    # delete self if out of bounds
    if self.rect.center[0] >= width or self.rect.center[0] <= 0 or self.rect.center[1] <= 0 or self.rect.center[1] >= height:
      rocket_sprite.remove(self)
    
    # if grounded -> check collision with bottom, launch at angle based on angle from rocket to center of dummy with "launch_force"
    # if airborne -> check collision in general, delete dummy
    # in either case, delete the rocket
    if dummy.airborne:
      collisions = pygame.sprite.spritecollideany(dummy, rocket_sprite)
      if collisions != None:
        dummy_sprite.remove(dummy)
        rocket_sprite.remove(self)
    else:
      if dummy.rect.bottom <= self.rect.bottom and dummy.rect.left <= self.rect.center[0] <= dummy.rect.right:
        launch_angle = math.atan2(dummy.rect.top - self.rect.bottom, dummy.rect.center[0] - self.rect.center[0])
        dummy.launched(launch_angle)
        rocket_sprite.remove(self)

class Scout(pygame.sprite.Sprite):
  def __init__(self, s_width, s_height, is_blue_team):
    pygame.sprite.Sprite.__init__(self)
    
    self.airborne = False
    self.num_jumps = 2
    self.speed = [0, 0]

    self.color = red
    self.position = ((1 * width) / 4, height - (s_height / 2))

    if is_blue_team:
      self.color = blue
      self.position = ((3 * width) / 4, height - (s_height / 2))

    # set the image to 's_width' x 's_height' rectangle of 'color' color
    self.image = pygame.Surface([s_width, s_height])
    self.image.fill(self.color)

    self.rect = self.image.get_rect() # make object have same dimensions as the image
    self.rect.center = self.position

  def movement(self):
    key = pygame.key.get_pressed()

    # air speed
    if self.airborne:
      if key[pygame.K_a] and self.speed[0] > -max_speed and self.rect.left > 0:
        self.speed[0] -= 1
      if key[pygame.K_d] and self.speed[0] < max_speed and self.rect.right < width:
        self.speed[0] += 1
      
      self.speed[1] += 2 # gravity
      
    else:
      if key[pygame.K_a] != key[pygame.K_d]:
        if key[pygame.K_a] and self.rect.left > 0:
          self.speed[0] = -max_speed
        elif key[pygame.K_d] and self.rect.right < width:
          self.speed[0] = max_speed
      else:
        self.speed[0] *= 0.75 # friction

      # stop gravity
      self.speed[1] = 0
      self.rect.bottom = height
      self.num_jumps = 2
    
    if self.rect.left < 0:
      self.rect.left = 0
      self.speed[0] = 0
    if self.rect.right > width:
      self.rect.right = width
      self.speed[0] = 0
    
  def jump(self):
    if (self.num_jumps > 0):
      key = pygame.key.get_pressed()
      if key[pygame.K_a] != key[pygame.K_d]:
        if key[pygame.K_a] and self.rect.left > 0:
          self.speed[0] = -max_speed
        elif key[pygame.K_d] and self.rect.right < width:
          self.speed[0] = max_speed
      else:
        self.speed[0] = 0 # neutral jump
      self.rect = self.rect.move([0, -1])
      self.speed[1] = -20
      self.num_jumps -= 1

  def shoot(self):
    mouse_pos = pygame.mouse.get_pos()
    shot_tuple = (mouse_pos[0] - self.rect.center[0], mouse_pos[1] - self.rect.center[1])
    rocket = Rocket(8, self.rect.center, math.atan2(shot_tuple[1], shot_tuple[0]))
    rocket_sprite.add(rocket)

  def update(self):
    self.airborne = self.rect.bottom < height
    self.movement()

    self.rect = self.rect.move(self.speed)

red = Scout(50, 50, False)
red_sprite = pygame.sprite.Group()
red_sprite.add(red)

dummy = Dummy(50, 50)
dummy_sprite = pygame.sprite.Group()
dummy_sprite.add(dummy)

rocket_sprite = pygame.sprite.Group()


# game loop
clock = pygame.time.Clock()
while True:
  clock.tick(60)
  screen.fill(white)

  dummy_sprite.draw(screen)
  red_sprite.draw(screen)
  rocket_sprite.draw(screen)

  dummy_sprite.update()
  red_sprite.update()
  rocket_sprite.update(dummy)

  pygame.display.update()
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit()
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_w:
        red.jump()
    elif event.type == pygame.MOUSEBUTTONDOWN:
      if event.button == 1:
        red.shoot()