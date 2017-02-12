import os
import re
import argparse

class GameHelper:
    def __init__(self):
        self.DEFAULT_GAME_FILE = 'OldHamletsAdventure.ntg'
    def clearConsole(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def formatParagraph(self, text, lineLength = 100):
        lines = text.split('\n')
        regex = re.compile(r'.{1,100}(?:\s+|$)')
        return '\n' + '\n'.join(s.rstrip() for line in lines for s in regex.findall(line)) + '\n'

    def finishGameLoop(self):
        self.clearConsole()
        exit()

    def getGameFile(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-g", dest="filename", required=False)
        args = parser.parse_args()
        if args.filename != None:
            return args.filename
        else:
            return self.DEFAULT_GAME_FILE




