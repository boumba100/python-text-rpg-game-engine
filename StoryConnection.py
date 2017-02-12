import os
import sqlite3
import shutil
import Characters

class StoryConnection:
    def __init__(self, gameFilename):
        self.CHARACTER_NAME = "OldHamlet"
        self.GENERAL_SEARCH_ANSWER = "Search can not be performed here"
        self.HOME_ROOM = "orchard"
        self.GAME_ENDING = "gameEnding"
        self.SAVE_FILE_NAME = "gameSave.ntg"
        self.DIRECTION_OPTIONS = ["N", "S", "E", "W", "NORTH", "SOUTH", "EAST", "WEST"]
        self.characterDirection = 2 # N = 2; W = 3; S = 4; E = 5
        self.curentRoom = None
        self.currentWall = None
        self.conn = None
        self.gameFilename = gameFilename

        self.mainCharacter = Characters.MainCharacter()

        self.getConnection()
        self.updateCharacter()
        self.getHomeRoom()
        self.getCharacterPos()

    def __exit__(self, exc_type, exc_value, traceback):
        self.closeConnection()

    def fileExist(self, fileName):
        try:
            file = open(fileName)
            file.close()
            return True
        except:
            return False

    def getConnection(self):
        if not self.fileExist(self.SAVE_FILE_NAME):
            shutil.copyfile(self.gameFilename, self.SAVE_FILE_NAME)
        self.conn = sqlite3.connect(self.SAVE_FILE_NAME)

    def closeConnection(self):
        self.conn.close()

    def updateWallDescription(self):
        itemsString = self.mainCharacter.getItemsCsv()
        cursor = self.conn.cursor()
        cursor.execute("UPDATE walls SET isChanged=(?), itemTaken=(?) WHERE wallName=(?)",(1,1,self.currentWall[5]))
        cursor.execute("UPDATE character SET items=(?) WHERE name=(?)", (itemsString, self.CHARACTER_NAME))
        self.conn.commit()
        cursor.close()

    def updateCharacterItems(self):
        itemsString = self.mainCharacter.getItemsCsv()
        cursor = self.conn.cursor()
        cursor.execute("UPDATE character SET items=(?) WHERE name=(?)", (itemsString, self.CHARACTER_NAME))
        self.conn.commit()
        cursor.close()


    def unlockDoor(self):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE walls SET isChanged=(?), gateKey=(?) WHERE wallName=(?)",(1,"UNLOCKED",self.currentWall[5]))
        self.conn.commit()
        cursor.close()

    def updateCharacter(self):
        cursor = self.conn.cursor()
        #items = cursor.execute("SELECT item FROM walls WHERE itemTaken=1").fetchall()
        items = str(cursor.execute("SELECT items FROM character WHERE name=(?)",(self.CHARACTER_NAME,)).fetchone()[0]).split(",")
        cursor.close()
        if items[0] != 'None':
            for item in items:
                self.mainCharacter.addItem(item)

    def getHomeRoom(self):
        self.changeRoom(self.getCharacterPos())

    def changeRoom(self, newRoom):
        cursor = self.conn.cursor()
        self.curentRoom = cursor.execute("SELECT * FROM rooms WHERE roomName=(?)", (newRoom,)).fetchone()
        cursor.close()

    def getCharacterPos(self):
        cursor = self.conn.cursor()
        currentRoom = cursor.execute("SELECT currentRoom FROM character WHERE name=(?)",(self.CHARACTER_NAME,)).fetchone()
        self.conn.commit()
        cursor.close()
        return currentRoom[0]

    def saveCharacterPos(self):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE character SET currentRoom=(?) WHERE name=(?)", (self.curentRoom[1], self.CHARACTER_NAME))
        self.conn.commit()
        cursor.close()

    def updateItemStatus(self):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE walls SET item=(?), itemTaken=(?) WHERE wallName=(?)", ("TAKEN", 1, self.currentWall[5]))
        self.conn.commit()
        cursor.close()

    def getRoomDescription(self):
        cursor = self.conn.cursor()
        self.currentWall = cursor.execute("SELECT * FROM walls WHERE wallName=(?)",(self.curentRoom[self.characterDirection], )).fetchone()
        if self.currentWall[7] == None:
            return self.currentWall[0]
        else:
            return self.currentWall[6]

    def getGameEnding(self):
        cursor = self.conn.cursor()
        gameEnding = cursor.execute("SELECT story FROM gameStory WHERE name=(?)",(self.GAME_ENDING, )).fetchone()[0]
        return gameEnding

    def processUserInput(self, userInput):
        response = ""
        inputList = [str(x).upper() for x in userInput]
        for word in inputList:
            if word in self.DIRECTION_OPTIONS:
                self.faceDirection(word)
                response = self.getRoomDescription()
            elif word == "ENTER" or word == "FOLLOW" or word == "GO" or word == "TO":
                for possibleGate in inputList:
                    if possibleGate == self.currentWall[2]:
                        if self.currentWall[3] == "UNLOCKED":
                            self.changeRoom(self.currentWall[4])
                            response = self.getRoomDescription()
                            break
                        else:
                            for possibleKey in inputList:
                                if possibleKey == self.currentWall[3]:
                                    if self.mainCharacter.containsItem(possibleKey):
                                        self.changeRoom(self.currentWall[4])
                                        self.unlockDoor()
                                        response = self.getRoomDescription()
                                    else:
                                        response = "sorry that does not work!"
                                    break
                                response = "you might be missing something to be able to enter!"
            elif word == "UNLOCK" or word == "OPEN":
                for possibleGate in inputList:
                    if possibleGate == self.currentWall[2]:
                        if self.currentWall[3] == "UNLOCKED":
                            self.changeRoom(self.currentWall[4])
                            response = "this is not locked"
                            break
                        else:
                            for possibleKey in inputList:
                                if possibleKey == self.currentWall[3]:
                                    if self.mainCharacter.containsItem(possibleKey) or possibleKey.isdigit():
                                        self.unlockDoor()
                                        self.getRoomDescription()
                                        response = "You have successfully unlocked it!"
                                    else:
                                        response = "Sorry that does not work!"
                                    break
                                response = "You might be missing something to be able to unlock this!"
                            break
            elif word == "TAKE":
                itemList = str(self.currentWall[1]).split(",")
                for possibleItem in inputList:
                    if possibleItem in itemList:
                        if self.mainCharacter.containsItem(possibleItem):
                            response = "You have already taken that!"
                        elif self.currentWall[1] != "TAKEN":
                            self.mainCharacter.addItem(possibleItem)
                            self.updateWallDescription()
                            self.getRoomDescription()
                            response = "You have taken the " + str(possibleItem).lower()
                        else:
                            response = "You cannot do that!"
                        break
            elif word == "ITEMS":
                response = self.mainCharacter.getItemsString()
                break
            elif word == "TALK":
                if self.currentWall[9] == None:
                    response = "You can't do that!"
                else:
                    response = self.currentWall[9]
                break
            elif word == "SEARCH" :
                if self.currentWall[10] != None:
                    response = self.currentWall[10]
                else:
                    response = self.GENERAL_SEARCH_ANSWER
                break
            elif word == "KILL":
                if self.currentWall[11]:
                    if self.currentWall[7] == 1:
                        response == "You have already done that!"
                    elif self.currentWall[3] == "UNLOCKED":
                        response = self.currentWall[11]
                        self.updateWallDescription()
                    else:
                        for possibleWeapon in inputList:
                            if possibleWeapon == self.currentWall[3]:
                                if self.mainCharacter.containsItem(possibleWeapon):
                                    response = self.currentWall[11]
                                    self.updateWallDescription()
                                else:
                                    response = "You do not have that!"
                                break
                else:
                    response = "Sorry you can't do that!"
                break
            elif word == "HINT":
                if self.currentWall[2] == None:
                    response = "There is no way to pass through here"
                else:
                    response = "You are able to use the word : " + self.currentWall[2]
                break
            elif word == "PICK" or word == "chose": #note: for the game of old hamlet
                if self.currentWall[7] == None:
                    itemList = str(self.currentWall[14]).split(",")
                    pickKey = str(self.currentWall[16]).split(",")
                    replyList = str(self.currentWall[15]).split("|")
                    for possibleItem in inputList:
                        if possibleItem in itemList:
                            if possibleItem == pickKey[0]:
                                self.mainCharacter.addItem(pickKey[1])
                                self.updateWallDescription()
                                self.getRoomDescription()
                                return replyList[itemList.index(possibleItem)]
                            else:
                                return "GAME OVER!\n\n" + replyList[itemList.index(possibleItem)]
                else:
                    response = "You have already done that!"
            elif word == "TRADE":
                neededItems = str(self.currentWall[12]).split(",")
                if neededItems[0] == "None":
                    response = "Trade can be performed here!"
                    break
                else:
                    for neededItem in neededItems:
                        if neededItem not in inputList:
                            return "You might be missing something to do this trade!"
                        elif not self.mainCharacter.containsItem(neededItem):
                            return "You do not have " + neededItem
                    for neededItem in neededItems:
                        self.mainCharacter.removeItem(neededItem)
                    self.mainCharacter.addItem(self.currentWall[13])
                    self.updateCharacterItems()
                    if self.currentWall[13] == "GAMEDONE":
                        return self.getGameEnding() + " &$%!"
                    else:
                        return "You have received " + self.currentWall[13] + " for your trade"
            elif word == "SAVE":
                self.saveCharacterPos()
                response = "OK game status successfully saved!"
                break

        if response == "":
            return "Sorry you can't do that!"
        else:
            return response

    def faceDirection(self, direction):
        if direction == "W" or direction == "WEST":
            self.characterDirection = 3
        elif direction == "N" or direction == "NORTH":
            self.characterDirection = 2
        elif direction == "S" or direction == "SOUTH":
            self.characterDirection = 4
        elif direction == "E" or direction == "EAST" :
            self.characterDirection = 5

















