import random
import time
from collections import defaultdict
from collections import namedtuple
import math
from abc import ABC, abstractmethod 

#board = [
#        ["W", "W", "W", "W", "W", "X", "X", "X", "X"],
#        ["W", "W", "W", "W", "W", "W", "X", "X", "X"],
#        ["E", "E", "W", "W", "W", "E", "E", "X", "X"],
#        ["E", "E", "E", "E", "E", "E", "E", "E", "X"],
#        ["E", "E", "E", "E", "E", "E", "E", "E", "E"],
#        ["X", "E", "E", "E", "E", "E", "E", "E", "E"],
#        ["X", "X", "E", "E", "B", "B", "B", "E", "E"],
#        ["X", "X", "X", "B", "B", "B", "B", "B", "B"],
#        ["X", "X", "X", "X", "B", "B", "B", "B", "B"]]

moves = {
        "NW":[-1, -1],
        "NE":[-1,  0],
        "E" :[ 0,  1],
        "SW":[ 1,  0],
        "SE":[ 1,  1],
        "W" :[ 0, -1]}     

#current_player = "W"



class MCTS_V2:
    def __init__(self, coef_exploration=1):
        self.Q = defaultdict(int) #les "wins" de chaque node
        self.N = defaultdict(int) #les visites de chaque node
        self.children =dict() #les enfants de chaque node
        self.coef_exploration = coef_exploration

    def choose(self, node):
        #choisit le meilleur node, continuation de la game                
        if node.is_terminal():
            raise RuntimeError(f"choose called on terminal {node}")

        if node not in self.children:
            return node.randomPlay(node.turn)

        def score(n):
            if self.N[n] == 0:
                return float("-inf") 
            return self.Q[n] + self.N[n]
        return max(self.children[node], key = score)

    def do_rollout(self, node):
        #on recherche une node en plus
        path = self._select(node) 
        leaf = path[-1]
        self._expand(leaf)        
        reward = self._simulate(leaf)        
        self._backpropagate(path, reward)

    def _select(self, node):
        #Cherche des nodes de nodes inexploré
        
        path = []
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                #Pas exploré ou terminal
                return path
            unexplored = self.children[node] - self.children.keys()

            if unexplored:
                n = unexplored.pop()
                path.append(n)
                return path
            node = self._uct_select(node)  # On cherche 1 plus loin

    def _expand(self, node):
        #Update le children dict avec les enfants du node
        if node in self.children:
            return #deja dedans
        self.children[node] = node.legal_plays(node.turn)
        

    def _simulate(self, node):
        #simule le gain ou pas
        
        invert_winner = True
        while True:
            if node.is_terminal():                
                winner = node.reward()
                return 1 - reward if invert_winner else reward
            node = node.randomPlay(node.turn)
            invert_winner = not invert_winner

    def _backpropagate(self, path, winner):
        #on remonte winner
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += winner
            winner = 1 - winner # 1 pour moi, 0 pour mon enemie

    def _uct_select(self, node):
        #UCB1 methode équilibre exploration/exploitation
        
        #Tout les enfants node devraient etre explorées
        assert all(n in self.children for n in self.children[node])

        log_N_vertex = math.log(self.N[node])

        def uct(n):
            return self.Q[n] / self.N[n] + self.coef_exploration * math.sqrt(log_N_vertex /self.N[n])

        return max(self.children[node], key=uct)

class Node(ABC):
    #la representation d'un état (un node)

    @abstractmethod
    def legal_plays(self, current_player):
        return set()

    @abstractmethod
    def randomPlay(self, current_player):
        return None

    @abstractmethod
    def is_terminal(self):
        return True

    @abstractmethod
    def winner(self):
        return 0

    #@abstractmethod
    #def __hash__(self):
    #    "Nodes must be hashable"
    #    return 123456789

    #@abstractmethod
    #def __eq__(node1, node2):
    #    "Nodes must be comparable"
    #    return True

_TTTB = namedtuple("Board", "tup turn winner terminal")

class Board(_TTTB, Node):    

    def tup_to_list(self, tup):
        board = [list(i) for i in tup]
        return board
    def list_to_tup(self, list):
        tup = (tuple(i) for i in list)
        return tup

    #def next_state(self, marblesArray, moveName, player):
    #    self.action(marblesArray, moveName, player, True)
    #    if player == "W":
    #        current_player = "B"
    #    else:
    #        current_player = "W"
    #    return (player, board, (marblesArray,moveName))

    def displayBoard(self):
        """
            Shows the Abalone board.
        """
        
        self.board = self.tup_to_list(self.tup)
        
        result = "\n\t [ CURRENT BOARD ]\n\n"
        for index,row in enumerate(self.board):
            if index == 0 or index == 8:
                result += "        "
            elif index == 1 or index == 7:
                result += "      "
            elif index == 2 or index == 6:
                result += "    "
            elif index == 3 or index == 5:
                result += "  "
            elif index == 5:
                result += ""
            for case in row:
                if case == "X":
                    pass
                elif case == "E":
                    result += " .  "
                else:
                    result += f" {case}  "
            result += "\n"
    
        print(result)

    def existingDirection(self, moveName):
        """
            Checks if the direction exists.
        """
        if moves.get(moveName) is None:
            return False
        return True

    def aligned(self, vector01, vector02):
        """
            Check if 2 vectors are aligned or not.
        """
        sum = [vector01[0] + vector02[0], vector01[1] + vector02[1]]
        product = [2*i for i in vector01]
        if product == sum or sum == [0, 0]:
            return True
    
        return False

    def colored(self, marblesArray, color):
        """
        ! FIX BUGS WITH COLOR    
            Checks if all marbles have the right color.
        """
        self.board = self.tup_to_list(self.tup) 
        for marble in marblesArray:
            if self.board[marble[0]][marble[1]] != 'W' and self.board[marble[0]][marble[1]] != 'B':
                # print("no marble here", marblesArray, marble, board[marble[0]][marble[1]])
                return "caseWithoutMarbleError"
            else:
                if self.board[marble[0]][marble[1]] != color:
                    # print("wrong color marble")
                    return "wrongColorError"

        return True

    def chain(self, marblesArray, move=None):
        """
            Checks if all marbles are aligned.
        """
        if len(marblesArray) > 3:
            return "lengthChainError"
    
        if len(marblesArray) == 1:
            return move

        marblesArray.sort()
        if move is not None:
            if marblesArray[0] == [marblesArray[1][0] + move[0], marblesArray[1][1] + move[1]]:
                return self.chain(marblesArray[1:], move=move)

        for currentMove in moves.values():
            if marblesArray[0] == [marblesArray[1][0] + currentMove[0], marblesArray[1][1] + currentMove[1]]:
                return self.chain(marblesArray[1:], move=currentMove)
    
        return "marblesChainError"

    def lineMove(self, marblesArray, moveName, opponent=False):
        """
            - Checks the chain\n
            - Checks lhe list (more than one marble ?)\n
            - Checks the alignment between the move and the chain\n
                - Finds the chain's last marble\n
                - Tries to find the next color\n
                    - Next color is out of range, returns an error\n
                    - Next color == 'X' (out of limit), returns an error\n
                    - Next color == actual color ('W' == 'W'), return an error\n
                    - Next color == 'E' (empty), you can move your chain\n
                    - Next color == opposing color, looks at the opponent chain and checks if the box behind the string is empty or out of board
        """
        self.board =self.tup_to_list(self.tup)
        vectorMove = moves[moveName]
        vectorChain = self.chain(marblesArray)
        lastMarble = marblesArray[0]

        if vectorChain == "lengthChainError" or vectorChain == "marblesChainError":
            return False, "chainError", marblesArray, moveName
    
        if vectorChain == None and opponent is False:
            return "soloMarbleInfo", marblesArray, moveName

        if (self.aligned(vectorMove, vectorChain)):
            if vectorMove == [-1, -1]:
                lastMarble =  min(marblesArray)
            elif vectorMove == [1, 1]:
                lastMarble = max(marblesArray)
            elif vectorMove == [1, 0]:
                for marble in marblesArray[1:]:
                    if marble[0] > lastMarble[0]:
                        lastMarble = marble
            elif vectorMove == [-1, 0]:
                for marble in marblesArray[1:]:
                    if marble[0] < lastMarble[0]:
                        lastMarble = marble
            elif vectorMove == [0, 1]:
                for marble in marblesArray[1:]:
                    if marble[1] > lastMarble[1]:
                        lastMarble = marble
            elif vectorMove == [0, -1]:
                for marble in marblesArray[1:]:
                    if marble[1] < lastMarble[1]:
                        lastMarble = marble
    
            if len(marblesArray) == 3 and (lastMarble[0] == 0 or lastMarble[1] == 0 or lastMarble[0] == 8 or lastMarble[1] == 8):
                return False, "outOfLimitError", marblesArray, moveName

            marblesArray.sort()
            if len(marblesArray) == 2:
                if (marblesArray[0][0] == 0 or marblesArray[0][1] == 0) and (moveName == "NE" or moveName == "NW"):
                    return False, "outOfLimitError"
                elif (marblesArray[-1][0] == 8 or marblesArray[-1][1] == 8) and (moveName == "SE" or moveName == "SW"):
                    return False, "outOfLimitError"


            currentValue = self.board[lastMarble[0]][lastMarble[1]]
            try:
                nextValue = self.board[lastMarble[0] + vectorMove[0]][lastMarble[1] + vectorMove[1]] 
            except:
                return False, "allyOutOfBoardError", marblesArray, moveName

            if nextValue == 'X':
                return False, "outLimitError", marblesArray, moveName
            elif nextValue == currentValue:
                return False, "sameValueError", marblesArray, moveName
            elif nextValue == 'E':
                marblesMoved = []
                for marble in marblesArray:
                    marblesMoved.append([marble[0] + vectorMove[0], marble[1] + vectorMove[1]])
                return True, marblesArray, marblesMoved
            else:
                try: # ! test [CHECKED]
                    lastOpponentMarbleValue = self.board[lastMarble[0] + len(marblesArray) * vectorMove[0]][lastMarble[1] + len(marblesArray) * vectorMove[1]]
                except:
                    try:
                        lastOpponentMarbleValue = self.board[lastMarble[0] + (len(marblesArray) - 1) * vectorMove[0]][lastMarble[1] + (len(marblesArray) - 1) * vectorMove[1]]
                    except:
                        return False, "outOfRange"
                    
                if lastOpponentMarbleValue != 'E' and lastOpponentMarbleValue == 'X':
                    return False, "NonEmptyError", marblesArray, moveName
                else:
                    marblesMoved = []
                    opponentMarbles = []
                    opponentMarblesMoved = []
                
                    for marble in marblesArray:
                        marblesMoved.append([marble[0] + vectorMove[0], marble[1] + vectorMove[1]])

                    for i in range(1, len(marblesArray)):
                        opponentValue = self.board[lastMarble[0] + i * vectorMove[0]][lastMarble[1] + i * vectorMove[1]]
                        if(opponentValue == 'E'):
                            break
                        opponentMarbles.append([lastMarble[0] + i * vectorMove[0], lastMarble[1] + i * vectorMove[1]])

                    if len(opponentMarbles) == 1:
                        self.soloMove(opponentMarbles, moveName, opponent=True)
                    else:
                        self.lineMove(opponentMarbles, moveName, opponent=True)

                    return True, marblesArray, marblesMoved, opponentMarbles, opponentMarblesMoved
                
        return False, "nonAlignedError", marblesArray, moveName

    def arrowMove(self, marblesArray, moveName, opponent=False):
        """
            - Checks the list only one marble ?)\n
            - Iterates the list\n
                - Next box == actual color ('B' == 'B'), returns error\n
                - Next box  == 'X' (out of limit), returns error\n
                - Next box == 'E' (empty), you can move your marble there\n
                - Next box == opposing color, checks if there is an empty box behind its position\n
            \n
            For each marbles, if the next box is 'E' or the opposing color (with an empty box behind), you can move your chain !
        """

        self.board = self.tup_to_list(self.tup)
        updatedMarbles = []
        if len(marblesArray) == 1:
            return "singleMarbleInfo", marblesArray, moveName

        for marble in marblesArray:
            if ((moveName.__contains__('S') and marble[0] != 8) or (moveName.__contains__('N') and marble[0] != 0)) and ((moveName.__contains__('W') and marble[1] != 0) or (moveName.__contains__('E') and marble[1] != 8)): 
                nextMarbleValue = self.board[marble[0] + moves[moveName][0]][marble[1] + moves[moveName][1]]
                currentMarbleValue = self.board[marble[0]][marble[1]]
                if nextMarbleValue == currentMarbleValue:
                    return False, "allyPresenceError", marblesArray, moveName
                elif nextMarbleValue == 'X':
                    return False, "outLimitError", marblesArray, moveName
                elif nextMarbleValue == 'E':
                    pass
                else:
                    try:
                        if board[marble[0] + 2 * moves[moveName][0]][marble[1] + 2 * moves[moveName][1]] == nextMarbleValue:
                            return False, "opponentMoveError", marblesArray, moveName
                    except:
                        return False, "outOfRange"

                updatedMarbles.append([marble[0] + moves[moveName][0], marble[1] + moves[moveName][1]])
    
        if len(updatedMarbles) != 0:
            return True, marblesArray, updatedMarbles
    
        return False, "notAnArrowMoveError"

    def soloMove(self, marblesArray, moveName, opponent=False):
        """
            - Checks the # of marbles in list\n
            - Checks the next box\n
                - Next box == 'X' (out of limit), returns an error\n
                - Next box == actual color ('W' == 'W'), returns an error\n
                - Next box == 'E' (empty), you can move your marble there\n
                - Next box == opposing color, returns an error (you have to move at least 2 allies to push your opponent)\n
            \n
            So if the next box is 'E', you can move your marble and update your board !
        """
        self.board = self.tup_to_list(self.tup)
        if len(marblesArray) == 1:
            currentValue = self.board[marblesArray[0][0]][marblesArray[0][1]]
            try:
                nextValue = self.board[marblesArray[0][0] + moves[moveName][0]][marblesArray[0][1] + moves[moveName][1]]
            except:
                nextValue = self.board[marblesArray[0][0]][marblesArray[0][1]]

            if nextValue == 'X':
                return False, "outLimitError"
            elif nextValue == currentValue:
                return False, "allyPresenceError"
            elif nextValue == 'E':
                pass
            else:
                return False, "opponentMoveError"

            marbleMoved = [[marblesArray[0][0] + moves[moveName][0], marblesArray[0][1] + moves[moveName][1]]]
            return True, marblesArray, marbleMoved
    
        return False, "notAsingleMarbleError"

    def updateBoard(self, oldPositions, newPositions):
        """
            Adds changes into the last board.
        """
        self.board = self.tup_to_list(self.tup)

        color = self.board[oldPositions[0][0]][oldPositions[0][1]]

        for marble in oldPositions:
            self.board[marble[0]][marble[1]] = 'E'
    
        for marble in newPositions:
            self.board[marble[0]][marble[1]] = f"{color}"

    def action(self, marblesArray, moveName, color, update=False):
        """
            - Checks the marble's color\n
            - Checks the direction existence\n
            - Checks the marbles alignment\n
            \t- Tries making a lineMove\n
            \t- If lineMove returns an error, tries making an arrowMove\n
            \t- If arrowMove returns an error, tries making a soloMove\n
            - If lineMove, arrowMove and soloMove return errors, the program returns False
        """
        self.board = self.tup_to_list(self.tup)
        if self.colored(marblesArray, color) is not True:
            # print(f"color error : '{color}'")
            return False

        if self.existingDirection(moveName) is False:
            # print(f"direction error : '{moveName}'")
            return False

        if self.chain(marblesArray) != "lengthChainError" and self.chain(marblesArray) != "marblesChainError":
        
            lm = self.lineMove(marblesArray, moveName)
            am = self.arrowMove(marblesArray, moveName)
            sm = self.soloMove(marblesArray, moveName)
            if lm[0] is not True:
                if am[0] is not True:
                    if sm[0] is not True:
                        # print(f"lineMove  : {lm}")
                        # print(f"arrowMove : {am}")
                        # print(f"soloMove  : {sm}")
                        return False
                    else:
                        # print("solo move")
                        self.updateBoard(sm[1], sm[2]) if update == True else None
                else:
                    # print("arrow move")
                    self.updateBoard(am[1], am[2]) if update == True else None
            else:
                # print("line move")
                self.updateBoard(lm[3], lm[4]) if (len(lm) == 4) and update == True else None
                self.updateBoard(lm[1], lm[2]) if update == True else None
    
            return moveName
    
        return False

    def possibleChainsFromPoint(self, lengthChain, referenceMarble, currentMarble=None, move=None, chain=[], chainsList=[], possibleDirections=list(moves.values())):    
        self.board = self.tup_to_list(self.tup)
        if currentMarble is None:
            currentMarble = referenceMarble
    
        if len(chain) == 0:
            chain.append(currentMarble)
    
        chain.sort()

        if lengthChain == 1:
            chainsList.append(chain)
            return chainsList
        elif lengthChain == len(chain):
            chainsList.append(chain)
            possibleDirections.remove(move)
            return self.possibleChainsFromPoint(lengthChain, referenceMarble, None, None, [], chainsList, possibleDirections)

        color = self.board[referenceMarble[0]][referenceMarble[1]]

        if move is None:
            for myMove in possibleDirections:
                nextMarble = [currentMarble[0] + myMove[0], currentMarble[1] + myMove[1]]
                previousMarble = [currentMarble[0] - myMove[0], currentMarble[1] - myMove[1]]
            
                if ((previousMarble[0] != -1 and previousMarble[0] != 9) and (previousMarble[1] != -1 and previousMarble[1] != 9)) and ((nextMarble[0] != -1 and nextMarble[0] != 9) and (nextMarble[1] != -1 and nextMarble[1] != 9)):
                    nextMarbleColor = self.board[nextMarble[0]][nextMarble[1]]
                    previousMarbleColor = self.board[previousMarble[0]][previousMarble[1]]
                    if previousMarbleColor == color and nextMarbleColor == color:
                        doubleNeighbourChain = [previousMarble, currentMarble, nextMarble]
                        doubleNeighbourChain.sort()
                        if chainsList.__contains__(doubleNeighbourChain) is not True and lengthChain == 3:
                            chainsList.append(doubleNeighbourChain)
                            return self.possibleChainsFromPoint(lengthChain, referenceMarble, None, myMove, [], chainsList, possibleDirections)
                        return self.possibleChainsFromPoint(lengthChain, referenceMarble, None, myMove, chain, chainsList, possibleDirections)

                if nextMarble[0] != -1 and nextMarble[0] != 9 and nextMarble[1] != -1 and nextMarble[1] != 9:
                    nextMarbleColor = self.board[nextMarble[0]][nextMarble[1]]  
                    if nextMarbleColor == color:
                        return self.possibleChainsFromPoint(lengthChain, referenceMarble, currentMarble, myMove, chain, chainsList, possibleDirections)
                else:
                    possibleDirections.remove(myMove)
                    return self.possibleChainsFromPoint(lengthChain, referenceMarble, None, None, [], chainsList, possibleDirections)
            if len(chainsList) > 0:
                chainsList.sort()
                return chainsList

            return "notMoveFoundError"
        else:
            nextMarble = [currentMarble[0] + move[0], currentMarble[1] + move[1]]
            if (nextMarble[0] != -1 and nextMarble[0] != 9) and (nextMarble[1] != -1 and nextMarble[1] != 9):
                nextMarbleColor = self.board[nextMarble[0]][nextMarble[1]]

                if nextMarbleColor == color:
                    chain.append(nextMarble)
                    return self.possibleChainsFromPoint(lengthChain, referenceMarble, nextMarble, move, chain, chainsList, possibleDirections)
            
            previousMarble = [referenceMarble[0] - move[0], referenceMarble[1] - move[1]]
            if (previousMarble[0] != -1 and previousMarble[0] != 9) and (previousMarble[1] != -1 and previousMarble[1] != 9):
                previousMarbleColor = self.board[previousMarble[0]][previousMarble[1]]

                if previousMarbleColor == color:
                    chain.append(previousMarble)
                    chain.sort()
                    if chainsList.__contains__(chain) is not True and len(chain) == lengthChain:
                        chainsList.append(chain)
                        return self.possibleChainsFromPoint(lengthChain, referenceMarble, previousMarble, move, [], chainsList, possibleDirections)

            possibleDirections.remove(move)
            return self.possibleChainsFromPoint(lengthChain, referenceMarble, None, None, [], chainsList, possibleDirections)

    def randomPlay(self, color):
        """
            Choose one random chain with one random move in the board.\n
            The method returns :
                - the color
                - the length of the chain
                - the marble
                - the chain built from this marble
                - the move
        """
        self.board = self.tup_to_list(self.tup)
        randomLength = random.choice((1,2,3))
        chosenBoxes = []
        myMoves = list(moves.keys())

        for i,row in enumerate(self.board):
            for j,value in enumerate(row):
                if value == color:
                    chosenBoxes.append([i,j])
    
        randomMarble = random.choice(chosenBoxes)
        chains = self.possibleChainsFromPoint(randomLength, randomMarble, None, None, [], [], list(moves.values()))
        randomMove = random.choice(myMoves)
    
        possibleChains = self.possibleChainsFromPoint(randomLength, randomMarble, None, None, [], [], list(moves.values()))
    
        while possibleChains == "notMoveFoundError":
            if len(chosenBoxes) > 1:
                chosenBoxes.remove(randomMarble)
                randomMarble = random.choice(chosenBoxes)
                possibleChains = self.possibleChainsFromPoint(randomLength, randomMarble, None, None, [], [], list(moves.values()))
            else:
                # print("no marbles")
                return False
    
        randomChain = random.choice(possibleChains)
        a = self.action(randomChain, randomMove, color, False)

        while a is False:
            if myMoves != []:
                randomMove = random.choice(myMoves)
                myMoves.remove(randomMove)
            else:
                if len(chosenBoxes) > 1:
                    chosenBoxes.remove(randomMarble)
                    randomMarble = random.choice(chosenBoxes)
                    possibleChains = self.possibleChainsFromPoint(randomLength, randomMarble, None, None, [], [], list(moves.values()))
                    while possibleChains == "notMoveFoundError":
                        if len(chosenBoxes) > 1:
                            chosenBoxes.remove(randomMarble)
                            randomMarble = random.choice(chosenBoxes)
                            possibleChains = self.possibleChainsFromPoint(randomLength, randomMarble, None, None, [], [], list(moves.values()))
                        else:
                            return False
                    randomChain = random.choice(possibleChains)
                elif len(chosenBoxes) == 1:
                    possibleChain =  self.possibleChainsFromPoint(randomLength, chosenBoxes[0], None, None, [], [], list(moves.values()))
                    chosenBoxes.remove(randomMarble)
                else:
                    return False
            a = self.action(randomChain, randomMove, color, True)
    
        return color, randomChain, a
        
    def opposingMarblesOut(self, yourColor):
        counter = 0
        opposingColor = ''
        self.board = self.tup_to_list(self.tup)
        # ! COMMENT FAIRE CETTE CONDITION TERNAIRE ?
        # opposingColor = 'W' if(yourColor == 'B') else opposingColor = 'B'

        if yourColor == 'B':
            opposingColor = 'W'
        else:
            opposingColor = 'B'

        for row in self.board:
            for box in row:
                if box == opposingColor:
                    counter += 1
    
        return 14 - counter

    def legal_plays(self, player):
        self.board = self.tup_to_list(self.tup)

        allMoves = []      
        chosenBoxes = []
        myMoves = list(moves.keys())
        lengthChains = 2
        
        if self.terminal:  # If the game is finished then no moves can be made
            return set()
    
        for i,row in enumerate(self.board):
            for j,value in enumerate(row):
                if value == player:
                    chosenBoxes.append([i,j])                    

        for i in range(lengthChains):
            for j in chosenBoxes:
                possibleChains = self.possibleChainsFromPoint(i, j, None, None, [], [], possibleDirections=list(moves.values())) 
               
        for i in possibleChains:
            for j in myMoves:
                if self.action(i, j, player, False) != False:                    
                    allMoves.append((i,j))
        return {self.find_children(i) for i in allMoves}
    
    def find_children(self, moveA):
        self.board = self.tup_to_list(self.tup)
        self.action(moveA[0], moveA[1], self.turn, True)
        newTup = self.list_to_tup(self.board)     
        winner = self.winner()

        if self.turn == "W":
            turn2 = "B"
        elif self.turn == "B":
            turn2 = "W"        
        is_terminal = winner is not None
        return Board(newTup, turn2, winner, is_terminal)

    def find_random_child(self):
        if game.terminal:
            return None  # If the game is finished then no moves can be made
        self.board = self.tup_to_list(self.tup)
        self.randomPlay(self.turn)
        newTup = self.list_to_tup(self.board)     
        winner = self.winner()
        if self.turn == "W":
            turn2 = "B"
        elif self.turn == "B":
            turn2 = "W"        
        is_terminal = winner is not None
        return Board(newTup, turn2, winner, is_terminal)

    def is_terminal(self):              
        return self.terminal

    def winner(self):
        scoreWhite = self.opposingMarblesOut('B')
        scoreBlack = self.opposingMarblesOut('W')
        
        if scoreBlack == 6 and self.turn == "W":
            return True
        elif scoreBlack == 6 and self.turn == "B":
            return False
        elif scoreWhite == 6 and self.turn == "B":
            return True
        elif scoreWhite == 6 and self.turn == "W":
            return False

        return None

    def reward(self):
        if not self.terminal:
            raise RuntimeError("reward called on nonterminal board")
        if self.winner is True:
            # It's your turn and you've already won. Should be impossible.
            raise RuntimeError("reward called on unreachable board")
        if self.winner is False:
            return 0  # Your opponent has just won. Bad.
        if self.winner is None:
            return 0.5  # Board is a tie
        # The winner is neither True, False, nor None
        raise RuntimeError("board has unknown winner type ")
        

def play_game(a,b,c,d):
    tree = MCTS_V2()
    game = new_abalone_board(a,b,c,d)
    print(game.displayBoard())

    if game.terminal:
        return 
    for _ in range(50):
        tree.do_rollout(game)            
    game = tree.choose(game)  
    
    print(game.displayBoard())
    if game.terminal:
        return

def new_abalone_board(a,b,c,d):
    return Board(tup =a, turn=b, winner=c, terminal=d)


if __name__ == '__main__':
    #from Abalone_V2 import Board
    #t = Board()
    #scorewhite = t.opposingMarblesOut('B')
    #scoreblack = t.opposingMarblesOut('W')
    #color = random.choice(('W', 'B'))
    
    #while scoreblack < 6 and scorewhite < 6:
    #    scorewhite = t.opposingMarblesOut('B')
    #    scoreblack = t.opposingMarblesOut('W')

    #    if color == 'B':
    #        color = 'W'
    #    elif color == 'W':
    #        color = 'B'

    #    t.randomPlay(color)
    #t.displayBoard(board)
    #print(scoreblack, scorewhite)
    #if scoreblack == 6:
    #    winner = "White"
    #else:
    #    winner = "Black"

    #print(f"the winner is : {winner}")


    #test = Board()
    #test.displayBoard(board)
    #test.randomPlay("W")
    #test.displayBoard(board)

    
    #simu = MonteCarloTreeSearch(board, current_player="W")
    #simu.get_play()

    #from Abalone_V2 import MCTS_V2, Node, Board
    
    res = play_game((
        ("W", "W", "W", "W", "W", "X", "X", "X", "X"),
        ("W", "W", "W", "W", "W", "W", "X", "X", "X"),
        ("E", "E", "W", "W", "W", "E", "E", "X", "X"),
        ("E", "E", "E", "E", "E", "E", "E", "E", "X"),
        ("E", "E", "E", "E", "E", "E", "E", "E", "E"),
        ("X", "E", "E", "E", "E", "E", "E", "E", "E"),
        ("X", "X", "E", "E", "B", "B", "B", "E", "E"),
        ("X", "X", "X", "B", "B", "B", "B", "B", "B"),
        ("X", "X", "X", "X", "B", "B", "B", "B", "B")), "W", None, False  )
    print(res)
 