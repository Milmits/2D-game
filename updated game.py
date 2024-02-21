import os.path
import pygame
from pygame.locals import QUIT, KEYDOWN, K_LEFT, K_RIGHT, K_y, K_n
import random
import mixer


pygame.init()
# Загрузка экрана
loading_screen = pygame.image.load('Fon for begining/Flag.png')
loading_rect = loading_screen.get_rect()
finish_flag = pygame.image.load('Fon for begining/finish_flag.png')
finish_flag_rect = finish_flag.get_rect()
# Основные цвета
white = (255, 255, 255)
black = (0, 0, 0)



#logo
icon = pygame.image.load('Logotip/icon.png')
pygame.display.set_icon(icon)
#music
pygame.mixer.init()
music_folder = "music"
playlist = ["LS.mp3", "PS.mp3", "SZ.mp3"]
full_paths = [os.path.join(music_folder, file) for file in playlist]
pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
pygame.mixer.music.set_volume(0.01)
current_track = 0
pygame.mixer.music.load(full_paths[current_track])
pygame.mixer.music.play()

pygame.MOUSEBUTTONDOWN


# create the window
width = 500
height = 500
screen_size = (width, height)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Car Game')


# colors
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)

# road and marker sizes
road_width = 300
marker_width = 10
marker_height = 50

# lane coordinates

left_lane = 150
center_lane = 250
right_lane = 350
lanes = [left_lane, center_lane, right_lane]

# road and edge markers
road = (100, 0, road_width, height)
left_edge_marker = (95, 0, marker_width, height)
right_edge_marker = (395, 0, marker_width, height)

# for animating movement of the lane markers
lane_marker_move_y = 0

# player's starting coordinates
player_x = 250
player_y = 400

# frame settings
clock = pygame.time.Clock()
fps = 120

# game settings
gameover = False
show_about_screen = False
show_loading_screen = True
speed = 1
score = 0

class Vehicle(pygame.sprite.Sprite):

    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)

        # scale the image down so it's not wider than the lane
        image_scale = 45 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))

        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class PlayerVehicle(Vehicle):

    def __init__(self, x, y):
        image = pygame.image.load('images/car.png')
        super().__init__(image, x, y)

# sprite groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

# create the player's car
player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# load the vehicle images
image_filenames = ['pickup_truck.png', 'semi_trailer.png', 'taxi.png', 'van.png']
vehicle_images = []
for image_filename in image_filenames:
    image = pygame.image.load('images/' + image_filename)
    vehicle_images.append(image)

# load the crash image
crash = pygame.image.load('images/crash.png')
crash_rect = crash.get_rect()

# game loop
running = True

while running:

    clock.tick(fps)

#Реализация бесконечного цикла аудиодорожек
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == pygame.USEREVENT + 1:
            # Переключаемся на следующий трек при окончании текущего
            current_track = (current_track + 1) % len(playlist)
            pygame.mixer.music.load(full_paths[current_track])
            pygame.mixer.music.play()

        # move the player's car using the left/right arrow keys
        if event.type == KEYDOWN:

            if event.key == K_LEFT and player.rect.center[0] > left_lane:
                player.rect.x -= 100
            elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                player.rect.x += 100

            # check if there's a side swipe collision after changing lanes
            for vehicle in vehicle_group:
                if pygame.sprite.collide_rect(player, vehicle):

                    gameover = True
                    show_loading_screen = False
                    show_about_screen = False

                    # place the player's car next to other vehicle
                    # and determine where to position the crash image
                    if event.key == K_LEFT:
                        player.rect.left = vehicle.rect.right
                        crash_rect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                    elif event.key == K_RIGHT:
                        player.rect.right = vehicle.rect.left
                        crash_rect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]


    # draw the grass
    screen.fill(green)

    # draw the road
    pygame.draw.rect(screen, gray, road)

    # draw the edge markers
    pygame.draw.rect(screen, yellow, left_edge_marker)
    pygame.draw.rect(screen, yellow, right_edge_marker)

    # draw the lane markers
    lane_marker_move_y += speed * 1.1
    if lane_marker_move_y >= marker_height * 2:
        lane_marker_move_y = 0
    for y in range(marker_height * -2, height, marker_height * 2):
        pygame.draw.rect(screen, white, (left_lane + 45, y + lane_marker_move_y, marker_width, marker_height))
        pygame.draw.rect(screen, white, (center_lane + 45, y + lane_marker_move_y, marker_width, marker_height))

    # draw the player's car
    player_group.draw(screen)

    # add a vehicle
    if len(vehicle_group) < 2:

        # ensure there's enough gap between vehicles
        add_vehicle = True
        for vehicle in vehicle_group:
            if vehicle.rect.top < vehicle.rect.height * 1.5:
                add_vehicle = False

        if add_vehicle:

            # select a random lane
            lane = random.choice(lanes)

            # select a random vehicle image
            image = random.choice(vehicle_images)
            vehicle = Vehicle(image, lane, height / -2)
            vehicle_group.add(vehicle)

    # make the vehicles move
    for vehicle in vehicle_group:
        vehicle.rect.y += speed

        # remove vehicle once it goes off screen
        if vehicle.rect.top >= height:
            vehicle.kill()

            # add to score
            score += 1

            # speed up the game after passing 5 vehicles
            if score > 0 and score % 5 == 0:
                speed += 1

    # draw the vehicles
    vehicle_group.draw(screen)

    # display the score
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    text = font.render('Score: ' + str(score), True, white)
    text_rect = text.get_rect()
    text_rect.center = (450, 400)
    screen.blit(text, text_rect)

    # check if there's a head on collision
    if pygame.sprite.spritecollide(player, vehicle_group, True):
        gameover = True
        show_loading_screen = False
        show_about_screen = False
        crash_rect.center = [player.rect.center[0], player.rect.top]
    pygame.display.update()


    # display game over
    if show_loading_screen:
        screen.fill((220, 20, 60))
        loading_rect = loading_screen.get_rect(center=screen.get_rect().center)
        screen.blit(loading_screen, loading_rect)
        pygame.display.flip()

        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pos()
        screen.fill((224, 255, 255))
        font = pygame.font.Font(pygame.font.get_default_font(), 60)
        text_logo = font.render('CAR GAME', True, ((139, 0, 0)))

        font1 = pygame.font.Font(pygame.font.get_default_font(), 30)
        text_paly = font1.render('PLAY', True, (139, 0, 0))
        text_about_game = font1.render('ABOUT GAME', True, (139, 0, 0))
        text_quit = font1.render('QUIT', True, (139, 0, 0))

        text_logo_rect = text_logo.get_rect(topleft=(85, 250))
        text_paly_rect = text_paly.get_rect(topleft=(210, 350))
        text_about_game_rect = text_about_game.get_rect(topleft=(150, 400))
        text_quit_rect = text_quit.get_rect(topleft=(215, 450))

        screen.blit(text_logo, text_logo_rect)
        screen.blit(text_paly, text_paly_rect)
        screen.blit(text_about_game, text_about_game_rect)
        screen.blit(text_quit, text_quit_rect)


        pygame.display.update([text_logo_rect, text_paly_rect, text_about_game_rect, text_quit_rect])


        while show_loading_screen:
            clock.tick(fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    show_loading_screen = False
                    show_about_screen = False
                    gameover = False
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if text_paly_rect.collidepoint(mouse_pos) and event.button == 1:
                        show_about_screen = False
                        gameover = False
                        show_loading_screen = False
                        player.rect.center = [player_x, player_y]
                        speed = 1
                        score = 0
                        vehicle_group.empty()
                        pygame.display.update()
                    elif text_about_game_rect.collidepoint(mouse_pos) and event.button == 1:
                        show_about_screen = True
                        show_loading_screen = False
                        gameover = False


                    elif text_quit_rect.collidepoint(mouse_pos) and event.button == 1:
                        gameover = False
                        running = False
                        show_loading_screen = False
                        show_about_screen = False
    if show_about_screen:
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pos()
        screen.fill(black)
        pygame.display.update()
        font107 = pygame.font.Font(pygame.font.get_default_font(), 50)
        aboute_game1 = font107.render('ABOUT GAME', True, red)
        aboute_game1_rect = aboute_game1.get_rect(topleft=(82, 20))
        font35 = pygame.font.Font(pygame.font.get_default_font(), 20)
        point_back = font35.render('BACK', True, red)
        point_back_rect = point_back.get_rect(topleft=(420, 450))

        font1 = pygame.font.Font(pygame.font.get_default_font(), 15)
        information = font1.render('Описание Игры:', True, white)
        information_rect = information.get_rect(topleft=(17, 115))

        information1 = font1.render('Car Game предлагает вам волнующую возможность сразиться', True, white)
        information1_rect = information.get_rect(topleft=(17, 135))

        information2 = font1.render('за рулём мощного автомобиля в захватывающих гонках', True, white)
        information2_rect = information.get_rect(topleft=(17, 155))

        information6 = font1.render('на выживание.', True, white)
        information6_rect = information.get_rect(topleft=(17, 175))

        information3 = font1.render('Вам предстоит мастерски маневрировать, избегать различных', True, white)
        information3_rect = information.get_rect(topleft=(17, 195))

        information4 = font1.render('препятствий и преодолевать вызовы на пути к победе', True, white)
        information4_rect = information.get_rect(topleft=(17, 215))

        information5 = font1.render('Разработчик: Кучук М.М.', True, red)
        information5_rect = information.get_rect(topleft=(17, 235))

        screen.blit(aboute_game1, aboute_game1_rect)
        screen.blit(information, information_rect)
        screen.blit(information1, information1_rect)
        screen.blit(information2, information2_rect)
        screen.blit(information3, information3_rect)
        screen.blit(information4, information4_rect)
        screen.blit(information5, information5_rect)
        screen.blit(information6, information6_rect)
        screen.blit(point_back, point_back_rect)
        pygame.display.update()

        while show_about_screen:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameover = False
                    running = False
                    show_loading_screen = False
                    show_about_screen = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if point_back_rect.collidepoint(mouse_pos) and event.button == 1:
                        show_loading_screen = True
                        show_about_screen = False
                        gameover = False

    if gameover:

        finish_flag_rect = finish_flag.get_rect(center=screen.get_rect().center)
        screen.blit(finish_flag, finish_flag_rect)
        pygame.display.flip()
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pos()
        screen.blit(crash, crash_rect)
        pygame.display.update()

        font = pygame.font.Font(pygame.font.get_default_font(), 45)
        text = font.render('GAME OVER', True, (220, 20, 60))

        font1 = pygame.font.Font(pygame.font.get_default_font(), 33)
        text_restart = font1.render('Restart', True, (255, 20, 147))

        font2 = pygame.font.Font(pygame.font.get_default_font(), 33)
        text_quit = font2.render('Quit', True, (128, 0, 128))

        font37 = pygame.font.Font(pygame.font.get_default_font(), 20)
        text_back2 = font37.render('BACK', True, (220, 20, 60))


        text_rect = text.get_rect(topleft=(130, 68))
        text_restart_rect1 = text_restart.get_rect(topleft=(210, 140))
        text_quit_rect2 = text_quit.get_rect(topleft=(231, 205))
        text_back2_rect = text_back2.get_rect(topleft=(420, 450))
        screen.fill((255, 250, 250))
        screen.blit(text, text_rect)
        screen.blit(text_restart, text_restart_rect1)
        screen.blit(text_quit, text_quit_rect2)
        screen.blit(text_back2, text_back2_rect)
        pygame.display.update([text_rect, text_restart_rect1, text_quit_rect2, text_back2_rect])

        while gameover:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameover = False
                    running = False
                    show_loading_screen = False
                    show_about_screen = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if text_restart_rect1.collidepoint(mouse_pos) and event.button == 1:  # Левая кнопка мыши
                        gameover = False
                        player.rect.center = [player_x, player_y]
                        speed = 1
                        score = 0
                        vehicle_group.empty()
                        pygame.display.update()
                    elif text_back2_rect.collidepoint(mouse_pos) and event.button == 1:
                        show_loading_screen = True
                        show_about_screen = False
                        gameover = False
                    elif text_quit_rect2.collidepoint(mouse_pos) and event.button == 1:  # Левая кнопка мыши
                        gameover = False
                        running = False

    pygame.display.update()


pygame.quit()