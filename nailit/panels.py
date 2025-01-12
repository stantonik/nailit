class Panel:
    displayed : 'Panel' = None
    def __init__(self):
        self.running = False
        self.status = 'ok'
        pass

    @classmethod
    def set_displayed(cls, panel : 'Panel'):
        # Choose which panel is displayed
        if cls.displayed:
            cls.displayed.running = False
        cls.displayed = panel
        cls.displayed.running = True

    def get_status(self):
        status = self.status;
        self.status = 'ok'
        return status

    def event_handler(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass

########## GAME ############

import pygame as pg
from .assets import *
from .objects import *

class Game(Panel):
    def __init__(self):
        super().__init__()
        self.pause = False
        self.gameover = False
        self.player : Player

        # Play background music
        sounds["bg"].play(-1)

        # Instantiate carpet gears
        self.sprites = pg.sprite.Group()
        for i in range(5):
            self.sprites.add(CarpetGear(25 + i * (SCREEN_WIDTH - 50) // 4, SCREEN_HEIGHT // 2, 20))
        # Instantiate hammer
        self.hammer = Hammer(SCREEN_WIDTH, SCREEN_HEIGHT // 2 - 70, 200)
        self.sprites.add(self.hammer)
        # Create plank
        self.plank = WoodPlanck(-250, SCREEN_HEIGHT // 2 - 25)
        self.nail_sequence = NailSequence()

        # Gameover and pause buttons
        self.restart_button = Button((SCREEN_WIDTH) // 2 - 80, 320, 40, 40, "restart_button")
        self.home_button = Button((SCREEN_WIDTH) // 2 + 40, 320, 40, 40, "home_button")

    def create_player(self, name):
        self.player = Player(name)

    def check_gameover(self):
        if self.player.life <= 0 and not self.gameover:
            self.gameover = True
            self.player.save()
            sounds["bg"].stop()

    def read_controller_key(self, key):
        # Simulate a key event when receiving the controller key
        event = pg.event.Event(pg.KEYDOWN, key=key)
        pg.event.post(event)

    def event_handler(self, event):
        if event.type == pg.QUIT:
            self.running = False 
            self.status = 'quit'
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and not self.gameover:
                self.hammer.hit()
                miss = True
                # Check collision with each nail
                for nail in self.plank.nail_group:
                    if nail.rect.colliderect(self.hammer.collide_rect) and not nail.hit:
                        # Nail hit
                        nail.rect.y += nail.length * 0.8
                        nail.hit = True
                        miss = False
                        sounds["hammer_hit"].play()

                        self.player.hammed += 1
                        self.player.hammed_inarow += 1
                        break
                if miss:
                    sounds["hammer_miss"].play()
                    self.player.hit += 1
                    self.player.hammed_inarow = 0
                    self.player.missed_inarow += 1
            elif event.key == pg.K_ESCAPE and not self.gameover:
                # Pause with <ESC>
                self.pause = not self.pause

        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.gameover or self.pause:
                if self.home_button.rect.collidepoint(event.pos):
                    self.running = False
                    sounds["bg"].stop()
                    self.status = 'menu'
                elif self.restart_button.rect.collidepoint(event.pos):
                    self.running = False
                    sounds["bg"].stop()
                    self.status = 'restart'

    def update(self, dt):
        if not self.pause and not self.gameover:
            self.plank.update(dt)
            self.sprites.update(dt)
            self.player.update(dt)

            self.check_gameover()

            # Round end
            if self.plank.timer > WoodPlanck.period:
                # Update player stats
                self.player.total_nails += len(self.plank.nail_group)
                self.player.calculate_stats()

                # Spawn a new plank
                self.plank.timer = 0
                self.plank = WoodPlanck(-250, SCREEN_HEIGHT // 2 - 25)

            # Handle nail sequences
            if self.plank.rect.x + self.plank.width > self.plank.nail_spawn.x + 5 and not self.nail_sequence.running and not self.plank.nailed and self.plank:
                self.nail_sequence.next()
                self.nail_sequence.set_plank(self.plank)

            self.nail_sequence.update(dt)

    def draw(self, screen):
        screen.fill(BG_COLOR)
        robot = pg.transform.smoothscale(textures["robot"], (300, 300))
        screen.blit(robot, (WoodPlanck.nail_spawn.x - 300 // 2 , -140))
        self.plank.draw(screen)
        self.sprites.draw(screen)
        pg.draw.line(screen, BLACK, (0, SCREEN_HEIGHT // 2 + 25), (SCREEN_WIDTH, SCREEN_HEIGHT // 2 + 25), 5)
        pg.draw.line(screen, BLACK, (0, SCREEN_HEIGHT // 2 - 25), (SCREEN_WIDTH, SCREEN_HEIGHT // 2 - 25), 5)

        # Display accuracy
        accuracy_txt = font_30.render(f"{self.player.accuracy}%", True, BLACK)
        screen.blit(accuracy_txt, ((SCREEN_WIDTH - accuracy_txt.get_width()) // 2, 30))

        # Display life
        for i in range(self.player.life):
            screen.blit(textures["heart"], (20 + i * 35, 20))
        
        # Pause window
        if self.pause:
            bg = pg.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2));
            bg.fill(BG_COLOR)
            pg.draw.rect(bg, BLACK, pg.Rect(0, 0, bg.get_width(), bg.get_height()), 2)

            pause_title = font_30.render("Pause", True, BLACK)
            bg.blit(pause_title, ((bg.get_width() - pause_title.get_width()) // 2, 10))

            screen.blit(bg, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4))
        # Gameover window
        elif self.gameover:
            bg = pg.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2));
            bg.fill(BG_COLOR)
            pg.draw.rect(bg, BLACK, pg.Rect(0, 0, bg.get_width(), bg.get_height()), 2)

            text = font_30.render("Game over !", True, BLACK)
            bg.blit(text, ((bg.get_width() - text.get_width()) // 2, 10))

            stats = list(self.player.get_stats().items())[:-1]
            for i, stat in enumerate(stats):
                text = font_30.render(f"{stat[0].replace('_', ' ')} : {stat[1]}", True, BLACK)
                bg.blit(text, ((bg.get_width() - text.get_width()) // 2, 50 + i * (text.get_height() + 5)))

            screen.blit(bg, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4))
        if self.pause or self.gameover:
            self.home_button.draw(screen)
            self.restart_button.draw(screen)


########## MENU ############

class Menu(Panel):
    def __init__(self):
        super().__init__()
        self.input_active = False
        self.player_name = ''
        self.cursor_timer = 0
        self.cursor_visible = True

        # Inputs
        self.input_box = pg.Rect(200, 250, 400, 50)
        self.play_button = Button(SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT - 150, 70, 70, "play_button")
        self.score_button = Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT - 150, 70, 70, "score_button")

    def event_handler(self, event):
        if event.type == pg.QUIT:
            self.running = False
            self.status = 'quit'
            return

        if event.type == pg.MOUSEBUTTONDOWN:
            if self.input_box.collidepoint(event.pos):
                self.input_active = not self.input_active
            elif self.play_button.rect.collidepoint(event.pos) and len(self.player_name) > 0:
                self.running = False
                self.status = 'start'
            elif self.score_button.rect.collidepoint(event.pos):
                self.running = False
                self.status = 'leaderboard'
            else:
                self.input_active = False

        if event.type == pg.KEYDOWN:
            if self.input_active:
                if event.key == pg.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pg.K_RETURN and len(self.player_name) > 0:
                    self.running = False
                    self.status = 'start'
                elif event.unicode.isalnum():
                    self.player_name += event.unicode 

    def update(self, dt):
        # Cursor blinking logic
        self.cursor_timer += pg.time.Clock().get_time()
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen):
        screen.fill(BG_COLOR)

        title = font_70.render("Nail it!", True, BLACK)
        description = font_30.render("Hammer the nails on rythm to make the perfect house for your cat !", True, BLACK)
        txt_surface = font_30.render(self.player_name, True, BLACK)
        enter_name_txt = font_30.render("Enter your name :", True, BLACK) 

        width = max(400, txt_surface.get_width() + 10)
        self.input_box.w = width

        screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 30))
        screen.blit(description, ((SCREEN_WIDTH - description.get_width()) // 2, 100))
        screen.blit(enter_name_txt, ((SCREEN_WIDTH - enter_name_txt.get_width()) // 2, self.input_box.y - enter_name_txt.get_height() - 10))
        screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 10))
        pg.draw.rect(screen, BLACK, self.input_box, 2)

        screen.blit(self.play_button.image, self.play_button.rect);
        screen.blit(self.score_button.image, self.score_button.rect);

        # Blink the cursor
        if self.input_active and self.cursor_visible:
            cursor_x = self.input_box.x + 5 + txt_surface.get_width()
            cursor_y = self.input_box.y + 10
            cursor_height = txt_surface.get_height()
            pg.draw.line(screen, BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

########## LEADER BOARD ############

from pathlib import Path
import csv

class LeaderBoard(Panel):
    def __init__(self):
        super().__init__()
        # Button instances
        self.return_but = Button((SCREEN_WIDTH - 40) // 2, SCREEN_HEIGHT - 70, 40, 40, "return_button")

        # Get the top 5 players
        self.top5_players = []
        players = dict()
        for file in Path(SCOREBOARDS_DIR).iterdir():
            if file.is_file(): 
                if file.suffix == ".csv":
                    with open(file, 'r') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row["party"] == "best":
                                players[file.stem] = row
                                break

        # Sort by score in descending order and take the top 5
        self.top5_players = sorted(players.items(), key=lambda item: float(item[1]["score"]), reverse=True)[:5]

    def event_handler(self, event):
        if event.type == pg.QUIT:
            self.running = False
            self.status = 'quit'
            return

        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.return_but.rect.collidepoint(event.pos):
                self.running = False
                self.status = 'menu'

    def draw(self, screen):
        screen.fill(BG_COLOR)

        title = font_70.render("Leader Board", True, BLACK)
        screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 30))
        screen.blit(self.return_but.image, self.return_but.rect);
    
        board_height = 160
        top5_txt = font_30.render("Top 5", True, BLACK)
        screen.blit(top5_txt, ((SCREEN_WIDTH - top5_txt.get_width()) // 2, board_height))
        for i, player in enumerate(self.top5_players):
            word = font_30.render(f"{i + 1}. {player[0]} -> score: {player[1]['score']} | {player[1]['accuracy']}%", True, BLACK)
            screen.blit(word, (220, board_height + 40 + (i * (word.get_height() + 10))))

        if len(self.top5_players) == 0:
            word = font_30.render("Empty", True, BLACK)
            screen.blit(word, ((SCREEN_WIDTH - word.get_width()) // 2, 220))
