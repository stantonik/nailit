def start():
    import pygame as pg
    import serial
    from . import assets
    # Initialize serial
    baud_rate = 9600 
    port = ''
    ser = None

    if len(port) == 0:
        import glob
        ports = glob.glob('/dev/tty.usb*')
        if len(ports) > 0: 
            port = ports[0]

    print(f"selected port for controller : {port}")

    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
    except: pass

    # Initialize pygame
    pg.init()
    pg.mixer.init()

    # Create window
    screen = pg.display.set_mode(assets.SCREEN_SIZE)
    pg.display.set_caption("Nail it!")
    clock = pg.time.Clock()

    # Load textures, sounds, fonts..
    assets.load_textures()
    assets.load_sounds()
    assets.load_fonts()

    # Create panels
    from .panels import Panel, Game, Menu, LeaderBoard

    menu = Menu()
    game = None

    Panel.set_displayed(menu)

    # Game loop
    delta_time = 0
    while Panel.displayed.running:
        # Read serial assets
        if game and ser and ser.in_waiting > 0:
            assets = ser.readline().decode('utf-8').strip()
            try:
                key = int(assets)
                game.read_controller_key(key)
            except ValueError: pass

        # Event handler
        for event in pg.event.get():
            Panel.displayed.event_handler(event)

        # Update and draw
        Panel.displayed.update(delta_time) 
        Panel.displayed.draw(screen)

        # Check the exit of each panel
        status = Panel.displayed.get_status()
        if status != 'ok':
            if status == 'start':
                game = Game()
                game.create_player(menu.player_name)
                Panel.set_displayed(game)
            elif status == 'leaderboard':
                Panel.set_displayed(LeaderBoard())
            elif status == 'menu':
                Panel.set_displayed(menu)
            elif status == 'restart':
                game = Game()
                game.create_player(menu.player_name)
                Panel.set_displayed(game)

        # Setup FPS and calculate dt
        delta_time = clock.tick(60) / 1000.0
        pg.display.flip()

    pg.quit()
    if ser != None: 
        ser.close()

if __name__ == "__main__":
    start()
