from tkinter import *
import math

# Represents a line between two nodes
class Line:
    def __init__(self, canvas, x1, y1, x2, y2):
        # the canvas on which the line is drawn
        self.canvas = canvas
        # the tkinter ID for the line itself
        self.lineId = canvas.create_line(x1, y1, x2, y2)
        # the coordinates representing the arrows on the line
        arrowCoords = self.__genArrowCoords(x1, y1, x2, y2)
        # the tkinter ID for the first arrow line
        self.arrowId1 = canvas.create_line(*arrowCoords[0])
        # the tkinter ID for the second arrow line
        self.arrowId2 = canvas.create_line(*arrowCoords[1])

    # sets the coordinates for the line
    def setCoords(self, x1, y1, x2, y2):
        # sets the coordinates of the line in tkinter
        self.canvas.coords(self.lineId, x1, y1, x2, y2)
        # sets the coordinates for the smaller arrow lines in tkinter
        arrowCoords = self.__genArrowCoords(x1, y1, x2, y2)
        self.canvas.coords(self.arrowId1, *arrowCoords[0])
        self.canvas.coords(self.arrowId2, *arrowCoords[1])

    # removes the line from tkinter
    def remove(self):
        for id in [self.lineId, self.arrowId1, self.arrowId2]:
            self.canvas.delete(id)

    # updates the direction
    def update(self, direction, x1, y1, x2, y2):
        lineCoords = self.canvas.coords(self.lineId)
        lineCoords[direction * 2] = (x1 + x2) / 2.0
        lineCoords[direction * 2 + 1] = (y1 + y2) / 2.0
        self.setCoords(*lineCoords)

    # generates the coordinates for an arrow given a line start and end point
    @staticmethod
    def __genArrowCoords(x1, y1, x2, y2):
        midx = (x1 + x2) / 2.0
        midy = (y1 + y2) / 2.0

        vectx = x2 - x1
        vecty = y2 - y1
        length = math.sqrt(vectx * vectx + vecty * vecty)
        if length != 0:
            vectx = vectx * Node.arrowLength / length
            vecty = vecty * Node.arrowLength / length

            perpx = -vecty
            perpy = vectx

            coords1 = [midx, midy, midx + perpx - vectx, midy + perpy - vecty]
            coords2 = [midx, midy, midx - perpx - vectx, midy - perpy - vecty]
        else:
            coords1 = [midx, midy, midx, midy]
            coords2 = [midx, midy, midx, midy]

        return coords1, coords2

#Represents a node in the graph to be searched, or a location on the board
class Node:
    #the halfWidth of the Node when drawn on the canvas
    halfWidth = 10
    arrowLength = 5

    def __init__(self, canvas, creator, x, y):
        #the canvas id for the Node
        self.itemId = canvas.create_rectangle(x - Node.halfWidth,
                                              y - Node.halfWidth,
                                              x + Node.halfWidth,
                                              y + Node.halfWidth,
                                              fill='blue',
                                              activefill='purple')
        #the canvas on which the Node is drawn
        self.canvas = canvas
        #the parent object of the Node
        self.creator = creator

        self.canvas.tag_bind(self.itemId, '<ButtonPress-1>', self.__startMove)
        self.canvas.tag_bind(self.itemId, '<B1-Motion>', self.__continueMove)
        self.canvas.tag_bind(self.itemId, '<ButtonRelease-1>', self.__endMove)
        secondaryButtons = ['2', '3']
        for but in secondaryButtons:
            self.canvas.tag_bind(self.itemId, '<ButtonPress-'+but+'>', self.__startConnect)
            self.canvas.tag_bind(self.itemId, '<B'+but+'-Motion>', self.__continueConnect)
            self.canvas.tag_bind(self.itemId, '<ButtonRelease-'+but+'>', self.__endConnect)

        #the line originating from the Node currently being drawn
        self.curLine = None
        #the adjacent Nodes to the Node
        self.neighbors = {}
        #the parent Nodes adjacent to this Node
        self.parents = {}
        #accumulates the expected number of goal Nodes that will be landed on
        self.expected = None
        #holds the current best dice to choose at this Node
        self.dice = None
        #the best choices to make for each number rolled
        self.bestRollChoices = None
        #whether the Node is a goal
        self.isGoal = False

    #called when left mouse is pressed down on Node
    def __startMove(self, event):
        if (self.creator.clickFlag == 'none'):
            coords = self.canvas.coords(self.itemId)
            self.__coords = (coords[0] - event.x,
                             coords[1] - event.y,
                             coords[2] - event.x,
                             coords[3] - event.y)

    #called when mouse is dragged after having been left-pressed on Node
    def __continueMove(self, event):
        if (self.creator.clickFlag == 'none'):
            x1 = self.__coords[0] + event.x
            y1 = self.__coords[1] + event.y
            x2 = self.__coords[2] + event.x
            y2 = self.__coords[3] + event.y

            self.canvas.coords(self.itemId, x1, y1, x2, y2)
            for (neighbor, (line, direction)) in self.neighbors.items():
                line.update(direction, x1, y1, x2, y2)
            for (neighbor, (line, direction)) in self.parents.items():
                line.update(direction, x1, y1, x2, y2)

    #called when mouse is released after having been left-pressed on Node
    def __endMove(self, event):
        if self.creator.clickFlag == 'setOrigin':
            self.creator.setOrigin(self)
        elif self.creator.clickFlag == 'setGoal':
            self.creator.setGoal(self)
        else:
            self.__continueMove(event)

    #called when right mouse is pressed down on Node
    def __startConnect(self, event):
        coords = self.canvas.coords(self.itemId)
        startx = (coords[0]+coords[2])/2.0
        starty = (coords[1]+coords[3])/2.0
        self.curLine = Line(self.canvas, startx, starty, event.x, event.y)

    #called when mouse is dragged after having been right pressed on Node
    def __continueConnect(self, event):
        coords = self.canvas.coords(self.itemId)
        startx = (coords[0]+coords[2])/2.0
        starty = (coords[1]+coords[3])/2.0
        self.curLine.setCoords(startx, starty, event.x, event.y)

    #called when mouse is released after having been right pressed on Node
    def __endConnect(self, event):
        othNode = self.creator.getNodeAt(event.x, event.y, self)
        if othNode:
            if othNode == self:
                self.curLine.remove()
                for neighbor, (line, dir) in self.neighbors.items():
                    line.remove()
                    del neighbor.parents[self]
                for parent, (line, dir) in self.parents.items():
                    line.remove()
                    del parent.neighbors[self]
                self.creator.destroyNode(self)
            elif othNode in self.neighbors or othNode in self.parents:
                self.curLine.remove()

                val = othNode.parents.get(self)
                if val:
                    line, _ = val
                    line.remove()
                    del othNode.parents[self]
                    del self.neighbors[othNode]
                val = othNode.neighbors.get(self)
                if val:
                    line, _ = val
                    line.remove()
                    del othNode.neighbors[self]
                    del self.parents[othNode]
            else:
                coords = self.canvas.coords(self.itemId)
                othCoords = self.canvas.coords(othNode.itemId)
                startx = (coords[0] + coords[2]) / 2.0
                starty = (coords[1] + coords[3]) / 2.0
                endx = (othCoords[0] + othCoords[2]) / 2.0
                endy = (othCoords[1] + othCoords[3]) / 2.0
                self.curLine.setCoords(startx, starty, endx, endy)

                self.neighbors[othNode] = (self.curLine, 0)
                othNode.parents[self] = (self.curLine, 1)
        else:
            self.curLine.remove()
        self.curLine = None

#allows the user to create a graph that represents a level
class LevelCreator:
    def __init__(self, master):
        #the width of the level creation canvas
        self.width = 800
        #the height of the level creation canvas
        self.height = 400
        #the level creation canvas
        self.canvas = Canvas(master, width=self.width, height=self.height)
        self.canvas.grid(row=0, column=0, columnspan=10)

        #the canvas id of the background rectangle
        self.backgroundId = self.canvas.create_rectangle(0, 0, self.width, self.height, fill='white')
        self.canvas.tag_bind(self.backgroundId, '<ButtonPress-1>', self.__createNode)

        #a map of node canvas IDs to the Node objects
        self.nodeMap = {}
        #the origin Node
        self.origin = None
        #contains modifiers for the behavior of the next click
        self.clickFlag = 'none'

    #creates a Node from a mouse click event
    def __createNode(self, event):
        node = Node(self.canvas, self, event.x, event.y)
        self.nodeMap[node.itemId] = node

    #destroys a Node
    def destroyNode(self, node):
        if node == self.origin:
            self.origin = None
        self.canvas.delete(node.itemId)
        del self.nodeMap[node.itemId]

    #get Node at the given position
    def getNodeAt(self, x, y, fromNode):
        items = self.canvas.find_overlapping(x, y, x, y)
        safetyNode = None
        for item in items:
            othNode = self.nodeMap.get(item)
            if othNode:
                safetyNode = othNode
                if not ((fromNode in othNode.neighbors) or (othNode in fromNode.neighbors)):
                    return othNode
        return safetyNode

    #sets the origin Node
    def setOrigin(self, origin):
        if self.origin:
            self.canvas.itemconfig(self.origin.itemId, fill='blue')
        self.canvas.itemconfig(origin.itemId, fill='green')
        self.origin = origin
        self.clickFlag = 'none'

    #sets the goal Node
    def setGoal(self, goal):
        goal.isGoal = not goal.isGoal
        if goal.isGoal:
            self.canvas.itemconfig(goal.itemId, fill='red')
        else:
            self.canvas.itemconfig(goal.itemId, fill='blue')
        self.clickFlag = 'none'

#Represents a character in the game that has both a main die and an ally die
class Character:
    def __init__(self, name, mainDice, allyDice):
        #the name of the character
        self.name = name
        #a list of the possible rolls for the main dice
        self.mainDice = mainDice
        #a list of the possible rolls for the ally dice
        self.allyDice = allyDice

#The main GUI class
class ChooseDice:
    def __init__(self, master):
        #the main tkInter frame
        self.frame = Frame(master)
        #the levelCreator frame
        self.levelCreate = LevelCreator(self.frame)
        self.frame.grid(row=0, column=0)

        #the button to set the origin Node
        self.setOriginButton = Button(
            self.frame, text='Set next node clicked to origin', fg='red', command=self.handleSetOrigin
        )
        self.setOriginButton.grid(row=1, column=0, columnspan=2)

        #the button to set the Goal
        self.setGoalButton = Button(
            self.frame, text='Toggle next clicked node goal state', fg='red', command=self.handleSetGoal
        )
        self.setGoalButton.grid(row=2, column=0, columnspan=2)

        #Label showing the number of turns
        self.turnsLabelStringVar = StringVar()
        self.turnsLabelResult = Label(self.frame, textvariable=self.turnsLabelStringVar)
        self.turnsLabelResult.grid(row=1, column=2)
        self.turnsLabelStringVar.set("# of turns:")

        #Slider allowing input of the number of turns to solve for
        self.turnsInputResult = Scale(self.frame, from_=1, to=30, orient=HORIZONTAL)
        self.turnsInputResult.grid(row=1, column=3, rowspan=1, columnspan=1)

        #the button that starts the solve
        self.solveButton = Button(
            self.frame, text='Solve', fg='red', command=self.solve
        )
        self.solveButton.grid(row=1, column=4, columnspan=5)

        #the label that holds the result of the solve
        self.solveResultStringVar = StringVar()
        self.solveResult = Label(self.frame, textvariable=self.solveResultStringVar)
        self.solveResult.grid(row=3, column=2, columnspan=5)
        self.solveResultStringVar.set("")

        #the button to add a new character
        self.addButton = Button(
            self.frame, text='Add character', fg='red', command=self.add
        )
        self.addButton.grid(row=1, column=9, columnspan=2)

        #the button to remove the last added character
        self.removeButton = Button(
            self.frame, text='Remove character', fg='red', command=self.remove
        )
        self.removeButton.grid(row=2, column=9, columnspan=2)

        #holds the drop down menus to select each character
        self.characterMenus = []

        #holds the names of all the characters
        self.characterNames = []

        allyDice = [1,2]

        #list of all the possible characters
        self.characterList = sorted([
            Character('Donkey Kong', [0,0,0,0,10,10], allyDice),
            Character('Bowser', [0,0,1,8,9,10], allyDice),
            Character('Boo', [0,0,5,5,7,7], allyDice),
            Character('Wario', [0,0,6,6,6,6], allyDice),
            Character('Peach', [0,2,4,4,4,6], allyDice),
            Character('Daisy', [3,3,3,3,4,4], allyDice),
            Character('Dry Bones', [1,1,1,6,6,6], allyDice),
            Character('Pom Pom', [0,3,3,3,3,8], allyDice),
            Character('Mario', [1,3,3,3,5,6], allyDice),
            Character('Luigi', [1,1,1,5,6,7], allyDice),
            Character('Waluigi', [0,1,3,5,5,7], allyDice),
            Character('Goomba', [0,0,3,4,5,6], allyDice),
            Character('Bowser Jr.', [1,1,1,4,4,9], allyDice),
            Character('Rosalina', [0,0,2,3,4,8], allyDice),
            Character('Diddy Kong', [0,0,0,7,7,7], allyDice),
            Character('Monty Mole', [0,2,3,4,5,6], allyDice),
            Character('Shy Guy', [0,4,4,4,4,4], allyDice),
            Character('Yoshi', [0,1,3,3,5,7], allyDice),
            Character('Hammer Bro', [0,1,1,5,5,5], allyDice),
            Character('Koopa', [1,1,2,3,3,10], allyDice)
        ], key=lambda character: character.name)
        self.charactersMap = {}
        for character in self.characterList:
            self.charactersMap[character.name] = character
        self.add()

    #produces the best course of action to reach the goal node from the origin node
    def solve(self):
        origin = self.levelCreate.origin
        if not origin:
            return

        diceDistributions = self.__genDistributions()
        itCount = self.turnsInputResult.get()

        for _, node in self.levelCreate.nodeMap.items():
            fillVal = 1 if node.isGoal else 0
            node.expected = [fillVal]*(itCount+1)
            node.dice = [None]*(itCount+1)
            node.bestRollChoices = [None]*(itCount+1)
        for i in range(1, itCount+1):
            for _, node in self.levelCreate.nodeMap.items():
                maxExpected = 0
                bestDice = None
                bestRollChoices = None
                for diceInd, dist in enumerate(diceDistributions):
                    rollExpected = [float("-inf") for _ in dist]
                    rollChoices = [() for _ in dist]
                    nodeStack = [(node, 0, ())]
                    while nodeStack:
                        nextNode, distance, curChoices = nodeStack.pop()
                        candidate = nextNode.expected[i-1]
                        if dist[distance] and candidate > rollExpected[distance]:
                            rollExpected[distance] = candidate
                            rollChoices[distance] = curChoices
                        if distance != len(dist)-1:
                            dirNeighbors = self.__neighborsToDirection(nextNode)
                            for neighbor, dirStr in dirNeighbors.items():
                                newChoices = curChoices
                                if dirStr:
                                    newChoices += (dirStr,)
                                nodeStack.append((neighbor, distance+1, newChoices))
                    expectedValue = 0
                    totalDensity = 0
                    for ind, dens in enumerate(dist):
                        safeExpected = rollExpected[ind]
                        if safeExpected == float("-inf"):
                            safeExpected = 0
                        expectedValue += safeExpected * dens
                        totalDensity += dens
                    expectedValue /= totalDensity
                    if expectedValue > maxExpected:
                        maxExpected = expectedValue
                        bestDice = diceInd
                        bestRollChoices = rollChoices
                if node.isGoal:
                    maxExpected += 1
                node.expected[i] = maxExpected
                node.dice[i] = bestDice
                node.bestRollChoices[i] = bestRollChoices
        characterInd = origin.dice[itCount]
        if characterInd is None:
            characterInd = 0
        bestCharacterStr = self.characterNames[characterInd].get()
        expectedValueStr = str(origin.expected[itCount])

        resultStr = "Best character: " + bestCharacterStr + " with " + expectedValueStr + " goal squares after " + str(itCount) + " turns"
        if origin.bestRollChoices[-1]:
            for roll, choices in enumerate(origin.bestRollChoices[-1]):
                if choices:
                    resultStr += "\nOn " + str(roll) + " roll: " + choices[0]
                    for choice in choices[1:]:
                        resultStr += ", " + choice
        self.solveResultStringVar.set(resultStr)

    #generates the distributions of possible rolls for each possible character choice
    def __genDistributions(self):
        out = []
        selectedChars = [self.charactersMap.get(nameVar.get()) for nameVar in self.characterNames]
        for charInd, character in enumerate(selectedChars):
            allies = selectedChars[charInd+1:]+selectedChars[:charInd]
            dice = [[0,0]] + [character.mainDice] + [ally.allyDice for ally in allies]
            maxRoll = 0
            for d in dice:
                maxRoll += d[-1]
            curDist = [0]*(maxRoll+1)
            indStack = [0]
            curSum = 0
            while indStack[0] == 0:
                while len(indStack) < len(dice):
                    curSum += dice[len(indStack)][0]
                    indStack.append(0)
                curDist[curSum] += 1
                curSum -= dice[len(indStack) - 1][indStack[-1]]
                indStack[-1] += 1
                while indStack[-1] == len(dice[len(indStack) - 1]):
                    indStack.pop()
                    curSum -= dice[len(indStack) - 1][indStack[-1]]
                    indStack[-1] += 1
                curSum += dice[len(indStack) - 1][indStack[-1]]
            out.append(curDist)
        return out

    #returns English descriptions of the relative positions of each neighbor to the passed-in node
    def __neighborsToDirection(self, node):
        canvas = self.levelCreate.canvas
        dirNeighbors = {}

        if len(node.neighbors) == 1:
            for neighbor in node.neighbors:
                dirNeighbors[neighbor] = ""
        elif not node.parents:
            for neighbor in node.neighbors:
                line, _ = node.neighbors[neighbor]
                lineCoords = canvas.coords(line.lineId)
                rotatedDir = math.atan2(lineCoords[2]-lineCoords[0], lineCoords[1]-lineCoords[3])
                dirNeighbors[neighbor] = str(int(rotatedDir*180/math.pi))+" degrees clockwise from North"
        else:
            leftNeighbors = []

            for neighbor in node.neighbors:
                accum = [0,0]
                for parent, (line, _) in node.parents.items():
                    lineCoords = canvas.coords(line.lineId)
                    accum[0] += lineCoords[2]-lineCoords[0]
                    accum[1] += lineCoords[1]-lineCoords[3]
                fromDir = math.atan2(*accum)
                line, _ = node.neighbors[neighbor]
                lineCoords = canvas.coords(line.lineId)
                toDir = math.atan2(lineCoords[2]-lineCoords[0], lineCoords[1]-lineCoords[3])
                rotatedDir = (toDir-fromDir)%(2*math.pi)
                if rotatedDir > math.pi:
                    rotatedDir -= 2*math.pi
                leftNeighbors.append((rotatedDir, neighbor))
            leftNeighbors.sort(key=lambda neigh: neigh[0])

            if len(leftNeighbors) == 2:
                dirNeighbors[leftNeighbors[0][1]] = "left"
                dirNeighbors[leftNeighbors[1][1]] = "right"
            else:
                for ind, (_, neighbor) in enumerate(leftNeighbors):
                    dirNeighbors[neighbor] = str(ind+1)+self.__ordinal(ind+1)+" from left"

        return dirNeighbors

    #produces the English ordinal suffix for the passed in number
    def __ordinal(self, num):
        mod = num%10
        if mod == 1 and num != 11:
            return "st"
        if mod == 2 and num != 12:
            return "nd"
        if mod == 3 and num != 13:
            return "rd"
        return "th"

    #handler for clicking the set origin button
    def handleSetOrigin(self):
        self.levelCreate.clickFlag = 'setOrigin'

    #handler for clicking the set goal button
    def handleSetGoal(self):
        self.levelCreate.clickFlag = 'setGoal'

    #handler for clicking the add character button
    def add(self):
        if len(self.characterMenus) < 5:
            dice = StringVar(self.frame)
            dice.set('Mario')

            menu = OptionMenu(self.frame, dice, *sorted([name for name in self.charactersMap.keys()]))
            menu.grid(row=2, column=2+len(self.characterMenus))
            self.characterMenus.append(menu)
            self.characterNames.append(dice)

    #handler for clicking the remove character button
    def remove(self):
        if len(self.characterMenus) > 1:
            self.characterMenus.pop().destroy()
            self.characterNames.pop()

if __name__ == "__main__":
    root = Tk(className='Choose dice')
    app = ChooseDice(root)
    root.mainloop()