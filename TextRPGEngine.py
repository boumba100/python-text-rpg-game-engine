import os
import re
import StoryConnection
import GameHelper


gameHelper = GameHelper.GameHelper()
gameHelper.clearConsole()
storyConn = StoryConnection.StoryConnection(gameHelper.getGameFile())

gameExit = False
print(gameHelper.formatParagraph(storyConn.getRoomDescription()))
while not gameExit:
    userCommand = re.sub( '\s+', ' ', input(">") ).strip().split(" ")
    if userCommand[0] == "exit":
        storyConn.closeConnection()
        gameHelper.finishGameLoop()
        break
    elif userCommand[0] == "delete":
        os.remove("gameSave.ntg")
        gameExit = True
    else:
       response = storyConn.processUserInput(userCommand)
       if "GAME OVER" in response:
           os.remove("gameSave.ntg")
           break
       elif "&$%!" in response:
           response = response.replace("&$%!", "")
           print(gameHelper.formatParagraph(response))
           break
       else:
           print(gameHelper.formatParagraph(response))



