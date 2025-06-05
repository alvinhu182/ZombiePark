import pgzrun
import random

WIDTH = 1200
HEIGHT = 720
white = (255, 255, 255)
black = (0, 0, 0)

background = Actor("background")
main_char = Actor('player_idle')
background_store = Actor("background_store")
background_game_over = Actor("background_game_over")

balas = []
playing_music = False
activated_sounds = True

class Zombie:
    def __init__(self, image_base_name, start_pos, direction):
        self.image_base_name = image_base_name
        self.actor = Actor(f"{image_base_name}_1", start_pos)
        self.direction = direction
        self.vida = 3
        self.animation_frames = 3
        self.current_frame = 1
        self.animation_speed = 5
        self.animation_counter = 0

    def respawn(self):
        self.vida = 3
        self.direction = random.choice([-1, 1])
        self.actor.x = 0 if self.direction == 1 else WIDTH
        self.actor.y = random.randint(30, 600)

    def update(self, speed):
        if self.vida <= 0:
            return
        self.actor.x += speed * self.direction
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame += 1
            if self.current_frame > self.animation_frames:
                self.current_frame = 1
            self.actor.image = f"{self.image_base_name}_{self.current_frame}"

class MainChar:
    def __init__(self):
        self.actor = Actor('player_idle', (WIDTH//2, HEIGHT//2))
        self.state = "idle"  # idle, up, down
        self.current_frame = 1
        self.animation_frames = 3
        self.animation_speed = 5
        self.animation_counter = 0
        self.facing = "right"  # Novo: direção que o personagem está virado

    def update(self):
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame += 1
            if self.current_frame > self.animation_frames:
                self.current_frame = 1

            if self.state == "up":
                self.actor.image = f"main_char_up_{self.current_frame}"
            elif self.state == "down":
                self.actor.image = f"main_char_down_{self.current_frame}"
            else:
                self.actor.image = "player_idle"

    def move_up(self, speed):
        self.actor.y -= speed
        self.actor.y = max(40, self.actor.y)
        if self.state != "up":
            self.state = "up"
            self.current_frame = 1
            self.animation_counter = 0

    def move_down(self, speed):
        self.actor.y += speed
        self.actor.y = min(680, self.actor.y)
        if self.state != "down":
            self.state = "down"
            self.current_frame = 1
            self.animation_counter = 0

    def idle(self):
        if self.state != "idle":
            self.state = "idle"
            self.actor.image = "player_idle"
            self.current_frame = 1
            self.animation_counter = 0

main_char_obj = MainChar()

zombies = []
for i in range(3):
    start_x = 0 if i % 2 == 0 else WIDTH
    direction = 1 if start_x == 0 else -1
    z = Zombie(f'zombie{i+1}', (start_x, random.randint(30, 600)), direction)
    zombies.append(z)

score = 0
total_score = 0
health = 3
game_over = False
actual_screen = 'menu'
upgrades = {
    "char_speed": {"level": 0, "price": 5},
    "health": {"level": 0, "price": 5},
    "bullet_speed": {"level": 0, "price": 5},
    "bullet_damage": {"level": 0, "price": 5},
}

button_play = Rect((300, 250), (250, 50))
button_restart = Rect((300, 300), (200, 50))
button_menu = Rect((300, 370), (200, 50))
button_store = Rect((310, 320), (180, 40))
button_sound = Rect((50, 500), (180, 40))

def start_game():
    global score, health, game_over, actual_screen, total_score
    main_char_obj.actor.x, main_char_obj.actor.y = WIDTH / 2, HEIGHT / 2
    main_char_obj.idle()
    for z in zombies:
        z.respawn()
    score = 0
    health = 3 + upgrades["health"]["level"]
    game_over = False
    actual_screen = "game"

def update():
    global actual_screen, health, game_over, score, total_score
    if actual_screen != "game":
        return

    char_speed = 5 + upgrades["char_speed"]["level"]
    moving = False

    if keyboard.up:
        main_char_obj.move_up(char_speed)
        moving = True
    elif keyboard.down:
        main_char_obj.move_down(char_speed)
        moving = True
    else:
        main_char_obj.idle()

    if keyboard.left:
        main_char_obj.facing = "left"
    elif keyboard.right:
        main_char_obj.facing = "right"

    main_char_obj.update()

    zombie_speed = 2 + score / 5
    for z in zombies:
        if z.vida > 0:
            z.update(zombie_speed)
            if z.actor.colliderect(main_char_obj.actor):
                if activated_sounds:
                    sounds.hurt.play()
                health -= 1
                if health <= 0:
                    game_over = True
                    if activated_sounds:
                        sounds.game_over.play()
                    actual_screen = "End"
                z.respawn()
            elif z.actor.x < -50 or z.actor.x > WIDTH + 50:
                z.respawn()

    bullet_speed = 10 + upgrades["bullet_speed"]["level"] * 2
    bullet_damage = 1 + min(upgrades["bullet_damage"]["level"], 3)

    for bala in balas[:]:
        if hasattr(bala, 'direcao'):
            if bala.direcao == "direita":
                bala.x += bullet_speed
            elif bala.direcao == "esquerda":
                bala.x -= bullet_speed
        else:
            bala.x += bullet_speed
        if bala.x < -50 or bala.x > WIDTH + 50:
            balas.remove(bala)
            continue

        for z in zombies:
            if z.vida > 0 and bala.colliderect(z.actor):
                z.vida -= bullet_damage
                balas.remove(bala)
                if z.vida <= 0:
                    score += 1
                    total_score += 1
                    z.respawn()
                break

def draw():
    global playing_music, background_game_over
    if actual_screen == "store":
        background_store.draw()
    else:
        background.draw()

    if actual_screen == "menu":
        screen.draw.text("ZombiePark", center=(WIDTH // 2, 150), color="yellow", fontsize=95)
        button_y_start = 250
        button_spacing = 70

        button_play.topleft = (480, 600)
        screen.draw.filled_rect(button_play, (255, 0, 0))
        screen.draw.text("PLAY", center=button_play.center, color=white, fontsize=30)

        button_store.topleft = (WIDTH // 2 - 100, button_y_start + button_spacing)
        screen.draw.filled_rect(button_store, (0, 0, 255))
        screen.draw.text("UPGRADE", center=button_store.center, color=white, fontsize=30)

        button_sound.center = (1050, 650)
        screen.draw.filled_rect(button_sound, (128, 0, 128))
        screen.draw.text("SOUND: " + ("ON" if activated_sounds else "OFF"), center=button_sound.center, color=white, fontsize=30)

        if not playing_music and activated_sounds:
            sounds.menu_song.play(-1)
            playing_music = True
        elif not activated_sounds and playing_music:
            sounds.menu_song.stop()
            playing_music = False

    elif actual_screen == "game":
        if playing_music:
            sounds.menu_song.stop()
            playing_music = False
        main_char_obj.actor.draw()
        for z in zombies:
            if z.vida > 0:
                z.actor.draw()
        screen.draw.text(f'Score: {score}', (15, 20), color=black)
        screen.draw.text(f'Health: {health}', (15, 40), color=black)
        for bala in balas:
            screen.draw.filled_rect(Rect((bala.x, bala.y), (20, 5)), (255, 255, 0))

    elif actual_screen == "End":
        background_game_over.draw()
        screen.draw.text("GAME OVER", center=(WIDTH // 2, 180), color=white, fontsize=40)
        screen.draw.text(f"FINAL SCORE: {score}", center=(WIDTH // 2, 230), color=white, fontsize=30)
        screen.draw.filled_rect(button_restart, (0, 128, 0))
        screen.draw.text("REINICIAR", center=button_restart.center, fontsize=30, color=white)
        screen.draw.filled_rect(button_menu, (0, 0, 128))
        screen.draw.text("MENU", center=button_menu.center, fontsize=30, color=white)

    elif actual_screen == "store":
        screen.draw.text("UPGRADE STORE", center=(WIDTH // 2, 50), fontsize=50, color=black)
        y_start = 150
        y_gap = 60
        for i, (key, upgrade) in enumerate(upgrades.items()):
            text = f"{key.upper()}: Nível {upgrade['level']} - Preço: {upgrade['price']} pts"
            screen.draw.text(text, (100, y_start + i * y_gap), fontsize=30, color=white)
        screen.draw.text(f"Total Score: {total_score}", topright=(WIDTH - 20, 10), fontsize=30, color=black)
        screen.draw.filled_rect(button_menu, (0, 0, 128))
        screen.draw.text("VOLTAR", center=button_menu.center, fontsize=30, color=white)

def on_key_down(key):
    global balas
    if actual_screen == "game" and key == keys.SPACE:
        nova_bala = Actor("bala")
        if activated_sounds:
            sounds.pewpew.play()
        nova_bala.x = main_char_obj.actor.x
        nova_bala.y = main_char_obj.actor.y

        if main_char_obj.facing == "left":
            nova_bala.direcao = "esquerda"
        else:
            nova_bala.direcao = "direita"
        balas.append(nova_bala)

def on_mouse_down(pos):
    global actual_screen, total_score, activated_sounds
    if actual_screen == "menu":
        if button_play.collidepoint(pos):
            start_game()
        elif button_store.collidepoint(pos):
            actual_screen = "store"
        elif button_sound.collidepoint(pos):
            activated_sounds = not activated_sounds

    elif actual_screen == "End":
        if button_restart.collidepoint(pos):
            start_game()
        elif button_menu.collidepoint(pos):
            actual_screen = "menu"

    elif actual_screen == "store":
        y_start = 150
        y_gap = 60
        keys_list = list(upgrades.keys())
        for i, key in enumerate(keys_list):
            rect = Rect((100, y_start + i * y_gap - 10), (800, 40))
            if rect.collidepoint(pos):
                upgrade = upgrades[key]
                if total_score >= upgrade["price"]:
                    total_score -= upgrade["price"]
                    upgrade["level"] += 1
                    upgrade["price"] = int(upgrade["price"] * 1.8)

        if button_menu.collidepoint(pos):
            actual_screen = "menu"

pgzrun.go()
