from deck import *
#from roll import *
import api

class plugin_load:
    def __init__(self):
        api.match_update('group', 'draw\s*(.+)', Deck.deck_get, 'reg', 50)
        return

if __name__ != "__main__":
    plugin_load()
