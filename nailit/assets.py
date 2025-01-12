# Constants
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 800, 500

# Paths
SCOREBOARDS_DIR = "./assets/logs/"

# Colors
BG_COLOR = (255, 234, 189)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Textures
def load_textures():
    from pygame.image import load
    from pygame.transform import smoothscale
    global textures
    textures = { 
                "gear": load("./assets/img/gear.png").convert_alpha(), 
                "hammer": load("./assets/img/hammer.png").convert_alpha(), 
                "nail": load("./assets/img/nail.png").convert_alpha(), 
                "play_button": load("./assets/img/play.png").convert_alpha(), 
                "score_button": load("./assets/img/leaderboard.png").convert_alpha(), 
                "return_button": load("./assets/img/return.png").convert_alpha(), 
                "restart_button": load("./assets/img/restart.png").convert_alpha(), 
                "home_button": load("./assets/img/home.png").convert_alpha(), 
                "robot": load("./assets/img/robot.png").convert_alpha(), 
                "heart": smoothscale(load("./assets/img/heart.png"), (30, 30)).convert_alpha(), 
                }

# Sounds
def load_sounds():
    from pygame.mixer import Sound
    global sounds
    sounds = {
            "nail": Sound("./assets/sounds/nail.mp3"),
            "hammer_hit": Sound("./assets/sounds/hammer_hit.mp3"),
            "hammer_miss": Sound("./assets/sounds/hammer_miss.mp3"),
            "bg": Sound("./assets/sounds/bg.mp3"),
            }

# Fonts
def load_fonts():
    from pygame.font import Font
    global font_30, font_70
    font_30 = Font(None, 30)
    font_70 = Font(None, 70)
