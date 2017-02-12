class MainCharacter:
    def __init__(self):
        self.items = []
        self.health = 100

    def addItem(self, item):
        self.items.append(str(item).upper())

    def containsItem(self, item):
        if item in self.items:
            return True
        else:
            return False

    def getItemsString(self):
        itemsString = "Current items : \n"
        for item in self.items:
            itemsString += item +"\n"
        return itemsString

    def getItemsCsv(self):
        csvString = ""
        for item in self.items:
            csvString += item + ","
        return csvString

    def removeItem(self, item):
        self.items.remove(item)

