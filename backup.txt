import pgzrun
import random

#aqui eu defino a largura e a altura do jogo
WIDTH = 1200
HEIGHT = 720
#variaveis de cor
white = (255, 255, 255)
black = (0, 0, 0)

#aqui é criado a tela de fundo do jogo, da loja e o fim do jogo
background = Actor("background")
main_char = Actor('player_idle')
background_store = Actor("background_store")
background_game_over = Actor("background_game_over")

#balas [] porque não começa com nenhuma bala, quando atiramos, preenche esse array
bullets = []
#playing_music é pra controlar se a musica do menu está tocando, e activated_sounds começa como True, porque o jogo já começa com
playing_music = False
activated_sounds = True

#classe do zombie com as caracteristicas deles
class Zombie:
    #init é o construtor dessa classe, quando usamos self aqui, nos referimos aos zombies
    #aqui recebe o nome da imagem, posição inicial e a direção, se é esquerda ou direita
    def __init__(self, image_base_name, start_pos, direction):
        self.image_base_name = image_base_name
        self.actor = Actor(f"{image_base_name}_1", start_pos)
        self.direction = direction
        #cada zombie tem uma vida o zombie 1 tem 3, o 2 tem 5 e o 3 tem 7
        if image_base_name == "zombie1":
            self.max_vida = 3
        elif image_base_name == "zombie2":
            self.max_vida = 5
        else:
            self.max_vida = 7
            #aqui ele esta dizendo vida do zombie = vida maxima no caso, 3 5 ou 7
        self.vida = self.max_vida
        self.animation_frames = 3
        self.current_frame = 1
        self.animation_speed = 5
        self.animation_counter = 0
        
    #função para fazer os zombies nascerem, qual direção (-1 esquerda 1 direita) no eixo x 
    def respawn(self):
        self.vida = self.max_vida
        self.direction = random.choice([-1, 1])
        #se o zombie começar no 0,  ele vai da esquerda pra direita, se ele começar no 1, vai da direita pra esquerda
        self.actor.x = 0 if self.direction == 1 else WIDTH
        #aqui é o eixo y, ele vai nascer entra 30 até 600
        self.actor.y = random.randint(30, 600)

    #função que recebe a velocidade dos zombies como parametro
    def update(self, speed):
        #se a vida do zombie for <= 0 ele morre e não executa o resto do codigo
        if self.vida <= 0:
            return
        #aqui 1 ele vai pra direita, -1 pra esquerda e aqui calcula com a velocidade do zombie
        self.actor.x += speed * self.direction
        #verifica se já passou o tempo para mudar de sprite(serve para as animações)
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            #qnd passar o tempo ele muda o frame pro proximo
            self.current_frame += 1
            #se o frame atual for maior que a quantidade de animação, ele volta pra 1, pra repetir
            if self.current_frame > self.animation_frames:
                self.current_frame = 1
            self.actor.image = f"{self.image_base_name}_{self.current_frame}"
#classe para definir os parametros do personagem principal
class MainChar:
    def __init__(self):
        #para o personagem nascer no meio da tela de largura e altura
        self.actor = Actor('player_idle', (WIDTH//2, HEIGHT//2))
        #começa como idle e depois vai mudando de frame
        self.state = "idle"
        self.current_frame = 1
        self.animation_frames = 3
        self.animation_speed = 5
        self.animation_counter = 0
        self.facing = "right"
        #aqui é para o player n ficar atirando sem parar
        self.shooting_timer = 0

    def update(self):
        #aqui diz que se ele acabou de atirar, ele tem que esperar pro proximo tiro
        if self.shooting_timer > 0:
            #diminui o valor do temporizador de tiro, para que o personagem possa atirar
            self.shooting_timer -= 1
            return
        #veririca se o contador chegou no tempo para trocar de frame
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_counter = 0
            self.current_frame += 1
            #se a quantidade de frame atual for maior que a quantidade de animações, ele volta pro primeiro frame
            if self.current_frame > self.animation_frames:
                self.current_frame = 1
            #se apertar a tecla pra cima, o personagem se move pra cima, mudando a sprite
            if self.state == "up":
                self.actor.image = f"main_char_up_{self.current_frame}"
                #a mesma coisa só que pra baixo
            elif self.state == "down":
                self.actor.image = f"main_char_down_{self.current_frame}"
                #fica parado
            else:
                self.actor.image = "player_idle"
    #aqui é a velocidade do personagem
    def move_up(self, speed):
        self.actor.y -= speed
        #aqui é para ele não subir no limite da tela
        self.actor.y = max(40, self.actor.y)
        #se o personagem não estava subindo, agora está
        if self.state != "up":
            self.state = "up"
            #reseta o quadro atual da animação para a primeira animação
            self.current_frame = 1
            #reinincia o contador da animação 
            self.animation_counter = 0
    #move_down é a mesma coisa que o move_up, só que pra baixo, e o limite de tela é o limite de baixo
    def move_down(self, speed):
        self.actor.y += speed
        self.actor.y = min(680, self.actor.y)
        if self.state != "down":
            self.state = "down"
            self.current_frame = 1
            self.animation_counter = 0
    #se o personagem fica parado, troca a sprite pra player_idle
    def idle(self):
        if self.state != "idle":
            self.state = "idle"
            self.actor.image = "player_idle"
            self.current_frame = 1
            self.animation_counter = 0
#guarda o personagem numa instancia variavel main_char_obj
main_char_obj = MainChar()
#segue a mesma lógica das balas, começa vazio e vai aparecendo os zombies
zombies = []

#funçao para criar os zombies, sendo aleatorio entre o 1 ,2 ,3 
def criate_zumbi():
    tipo = random.choice(["zombie1", "zombie2", "zombie3"])
    #decide se o zombie vai nascer  no lado esquerdo ou direito
    start_x = 0 if random.choice([True, False]) else WIDTH
    # se for 1 ele vai para a direita,  -1 esquerda
    direction = 1 if start_x == 0 else -1
    #aqui vai vir um dos 3 tipos de zombies, e vão nascer aleatoriamente entre altura de 30 e 600
    z = Zombie(tipo, (start_x, random.randint(30, 600)), direction)
    #adiciona o zombie na lista
    zombies.append(z)

#pontuação começa com 0, total score com 0, vida com 3, a tela inicial é o menu
score = 0
total_score = 0
health = 3
game_over = False
actual_screen = 'menu'

#aqui ficam os upgrades para serem comprados na loja
upgrades = {
    "char_speed": {"level": 0, "price": 5},
    "health": {"level": 0, "price": 5},
    "bullet_speed": {"level": 0, "price": 5},
    "bullet_damage": {"level": 0, "price": 5},
}

#cria os botões, play, restart, menu, loja e som
button_play = Rect((300, 250), (250, 50))
button_restart = Rect((300, 300), (200, 50))
button_menu = Rect((300, 370), (200, 50))
button_store = Rect((310, 320), (180, 40))
button_sound = Rect((50, 500), (180, 40))

#aqui é onde restarta o jogo, colocando o personagem no centro da tela, 
def start_game():
    global score, health, game_over, actual_screen, total_score, zombies
    #aqui eu coloco o main_char_obj que pegamos na linha 137 e coloca no centro da tela, com largura/2 e altura/2
    main_char_obj.actor.x, main_char_obj.actor.y = WIDTH / 2, HEIGHT / 2
    main_char_obj.idle()
    #cria zombies
    zombies = []
    criate_zumbi()
    #começa com 0 pontos a vida + o upgrade que tiver de vidas
    score = 0
    health = 3 + upgrades["health"]["level"]
    game_over = False
    #tela de jogo
    actual_screen = "game"

def update():
    #variaveis global
    global actual_screen, health, game_over, score, total_score
    # se a tela atual não for a tela do jogo, ele retorna, sem executar o restante
    if actual_screen != "game":
        return
    #define a velocidade do personagem + a quantidade no upgrade
    char_speed = 5 + upgrades["char_speed"]["level"]
    #variavel pra saber se o personagem está andando
    moving = False
    #se apertar a tecla pra cima, ele pega o personagem principal, e move pra cima, chamando afunção move_up de acordo com a velocidade dele
    if keyboard.up:
        main_char_obj.move_up(char_speed)
        #quando eu clico na seta, ele muda o moving pra True( que era false quando parado)
        moving = True
        #a mesma coisa de cida, só que indo pra baixo
    elif keyboard.down:
        main_char_obj.move_down(char_speed)
        moving = True
    else:
        main_char_obj.idle()
    #se apertar pra esquerda, ele vai atirar pra esquerda, e se tiver pra direita ele vai atirar na direita
    if keyboard.left:
        main_char_obj.facing = "left"
    elif keyboard.right:
        main_char_obj.facing = "right"
    #essa linha chama a função update, do objeto main_char (personagem principal)
    main_char_obj.update()
    #a cada 5 zombies mortos, a velocidade dos zombies aumentam
    zombie_speed = 2 + score / 5

    #essa linha a cada 5 pontos nasce um zombie a mais, chamando a função zombies, de acordado com a quantidade de zombies
    Qzumbi = score // 5 + 1
    if len(zombies) < Qzumbi:
        criate_zumbi()
    #aqui são algumas interações com os zombies, se a vida dele for maior que 0 ele está vivo
    for z in zombies:
        if z.vida > 0:
            #atualiza a velocidade do zombi 
            z.update(zombie_speed)
            #se o zumbi colidir com o personagem princiap, ativa o som hurt, diminui uma vida, e se a vida chegar em 0, acaba, toca a musica de game over e muda de tela
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
                #se o zombie sair da tela ele respawna
            elif z.actor.x < -50 or z.actor.x > WIDTH + 50:
                z.respawn()
    
    bullet_speed = 10 + upgrades["bullet_speed"]["level"] * 2
    bullet_damage = 1 + min(upgrades["bullet_damage"]["level"], 3)

    #o tiro verifica a direção da bala
    for bullet in bullets[:]:
        if hasattr(bullet, 'direction'):
            if bullet.direction == "right":
                bullet.x += bullet_speed
            elif bullet.direction == "left":
                bullet.x -= bullet_speed
        else:
            bullet.x += bullet_speed
        if bullet.x < -50 or bullet.x > WIDTH + 50:
            bullets.remove(bullet)
            continue

        for z in zombies:
            if z.vida > 0 and bullet.colliderect(z.actor):
                z.vida -= bullet_damage
                bullets.remove(bullet)
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
                bar_width = 40
                bar_height = 6
                health_ratio = z.vida / z.max_vida
                screen.draw.filled_rect(Rect((z.actor.x - 20, z.actor.y - 40), (bar_width, bar_height)), (255, 0, 0))
                screen.draw.filled_rect(Rect((z.actor.x - 20, z.actor.y - 40), (bar_width * health_ratio, bar_height)), (0, 255, 0))
        screen.draw.text(f'Score: {score}', (15, 20), color=black)
        screen.draw.text(f'Health: {health}', (15, 40), color=black)
        for bullet in bullets:
            screen.draw.filled_rect(Rect((bullet.x, bullet.y), (20, 5)), (255, 255, 0))

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
    global bullets
    if actual_screen == "game" and key == keys.SPACE:
        new_bullet = Actor("bullet")
        if activated_sounds:
            sounds.pewpew.play()
        new_bullet.x = main_char_obj.actor.x
        new_bullet.y = main_char_obj.actor.y

        if main_char_obj.facing == "left":
            new_bullet.direction = "left"
            main_char_obj.actor.image = "main_char_shooting_left"
        else:
            new_bullet.direction = "right"
            main_char_obj.actor.image = "main_char_shooting_right"

        main_char_obj.shooting_timer = 30
        bullets.append(new_bullet)

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
