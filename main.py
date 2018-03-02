from src.game import Game
from src.menu import Menu


def main():
    menu = Menu()
    menu.run()
    if not menu.config.start_game:
        exit(0)
    game = Game(config=menu.config)
    new_game = game.run()
    if new_game:
        main()

if __name__ == '__main__':
    main()
