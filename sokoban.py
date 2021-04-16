import curses
import sys


kill = False #interrupteur d'arrêt
reset = False #interrupteur de remise à zero
listeImmo = [] #entités non mobiles
listeBox = [] #entités mobiles
playa = "" #objet du joueur

def errorMessage(stdscr, message):
    global kill
    kill = True
    stdscr.addstr(0, 0, "message")
    stdscr.getch()

def whatsHere(posX,posY):
    #vérifie il y à quoi à cette position
    global reset
    try:
        obj = listeImmo[posY][posX]
        if listeBox[posY][posX] != "":
            obj = listeBox[posY][posX]
    except:
        reset = True
    else:
        return obj


class Entity:
    def __init__(self, posX, posY, symbol):
        self.symbol = symbol
        self.posX = posX
        self.posY = posY

class Player(Entity):
    def __init__(self,posX,posY):
        Entity.__init__(self,posX,posY,"P")
        
    def haut(self):
        goingTo = whatsHere(self.posX,self.posY-1)
        if goingTo == "":
            self.posY -= 1
        elif goingTo.symbol == "O":
            self.posY -= 1
        elif goingTo.symbol == "X":
            goingTo.haut()
            if whatsHere(self.posX,self.posY-1) == "":
                self.posY -= 1
    
    def bas(self):
        goingTo = whatsHere(self.posX,self.posY+1)
        if goingTo == "":
            self.posY += 1
        elif goingTo.symbol == "O":
            self.posY += 1
        elif goingTo.symbol == "X":
            goingTo.bas()
            if whatsHere(self.posX,self.posY+1) == "":
                self.posY += 1

    def gauche(self):
        goingTo = whatsHere(self.posX-1,self.posY)
        if goingTo == "":
            self.posX -= 1
        elif goingTo.symbol == "O":
            self.posX -= 1
        elif goingTo.symbol == "X":
            goingTo.gauche()
            if whatsHere(self.posX-1,self.posY) == "":
                self.posX -= 1
    
    def droite(self):
        goingTo = whatsHere(self.posX+1,self.posY)
        if goingTo == "":
            self.posX += 1
        elif goingTo.symbol == "O":
            self.posX += 1
        elif goingTo.symbol == "X":
            goingTo.droite()
            if whatsHere(self.posX+1,self.posY) == "":
                self.posX += 1

class Target(Entity):
    def __init__(self,posX,posY):
        Entity.__init__(self,posX,posY,"O")
        self.enabled = False
    
    def changeState(self,state):
        self.enabled = state

class Box(Entity):
    def __init__(self,posX,posY):
        Entity.__init__(self,posX,posY,"X")
    
    def haut(self):
        global listeBox
        goingTo = whatsHere(self.posX,self.posY-1)
        listeBox[self.posY][self.posX] = ""
        if goingTo == "":
            self.posY -= 1
            goingFrom = whatsHere(self.posX,self.posY+1)
            if goingFrom != "" and goingFrom.symbol == "O":
                goingFrom.changeState(False)
        elif goingTo.symbol == "O":
            self.posY -= 1
            goingTo.changeState(True)
            goingFrom = whatsHere(self.posX,self.posY+1)
            if goingFrom != "" and goingFrom.symbol == "O":
                goingFrom.changeState(False)
        
        listeBox[self.posY][self.posX] = self
    
    def bas(self):
        global listeBox
        goingTo = whatsHere(self.posX,self.posY+1)
        listeBox[self.posY][self.posX] = ""
        if goingTo == "":
            self.posY += 1
            goingFrom = whatsHere(self.posX,self.posY-1)
            if goingFrom != "" and goingFrom.symbol == "O":
                goingFrom.changeState(False)
        elif goingTo.symbol == "O":
            self.posY += 1
            goingFrom = whatsHere(self.posX,self.posY-1)
            if goingFrom != "" and goingFrom.symbol == "O":
                goingFrom.changeState(False)
        listeBox[self.posY][self.posX] = self

    def gauche(self):
        global listeBox
        goingTo = whatsHere(self.posX-1,self.posY)
        listeBox[self.posY][self.posX] = ""
        if goingTo == "":
            self.posX -= 1
            goingFrom = whatsHere(self.posX+1,self.posY)
            if goingFrom != "" and goingFrom.symbol == "O":
                goingFrom.changeState(False)
        elif goingTo.symbol == "O":
            self.posX -= 1
            goingFrom = whatsHere(self.posX+1,self.posY)
            if goingFrom != "" and goingFrom.symbol == "O":
                goingFrom.changeState(False)
        listeBox[self.posY][self.posX] = self
    
    def droite(self):
        global listeBox
        goingTo = whatsHere(self.posX+1,self.posY)
        listeBox[self.posY][self.posX] = ""
        if goingTo == "":
            self.posX += 1
            goingFrom = whatsHere(self.posX-1,self.posY)
            if goingFrom != "" and goingFrom.symbol == "O":
                goingFrom.changeState(False)
        elif goingTo.symbol == "O":
            self.posX += 1
            goingFrom = whatsHere(self.posX-1,self.posY)
            if goingFrom != "" and goingFrom.symbol == "O":
                goingFrom.changeState(False)
        listeBox[self.posY][self.posX] = self
        
class Wall(Entity):
    def __init__(self,posX,posY):
        Entity.__init__(self,posX,posY,"#")

def affichage(stdscr):
    global listeImmo
    global listeBox
    stdscr.clear()
    y = 0
    while y < len(listeImmo):
        x = 0
        while x < len(listeImmo[0]):
            stdscr.addstr(y, x, " ")
            if(listeImmo[y][x] != ""):
                stdscr.addstr(y, x, listeImmo[y][x].symbol)
            if(listeBox[y][x] != ""):
                stdscr.addstr(y, x, listeBox[y][x].symbol)
            
            x += 1
        y += 1
    stdscr.addstr(playa.posY, playa.posX, playa.symbol)

def initGame(stdscr):
    global listeImmo
    global listeBox
    global playa
    with open(sys.argv[1], 'r') as file:
        counter_y = 0
        compteO = 0
        compteX = 0
        for line in file:
            counter_x = 0
            listeImmo.append([])
            listeBox.append([])
            for char in line.strip():
                if char == " ":
                    listeImmo[counter_y].append("")
                    listeBox[counter_y].append("")
                elif char == "#":
                    listeImmo[counter_y].append(Wall(counter_x,counter_y))
                    listeBox[counter_y].append("")
                elif char == "O":
                    listeImmo[counter_y].append(Target(counter_x,counter_y))
                    listeBox[counter_y].append("")
                    compteO += 1
                elif char == "X":
                    listeImmo[counter_y].append("")
                    listeBox[counter_y].append(Box(counter_x,counter_y))
                    compteX += 1
                elif char == "P":
                    listeImmo[counter_y].append("")
                    listeBox[counter_y].append("")
                    try:
                        playerToken
                    except NameError:
                        playerToken = Player(counter_x,counter_y)
                    else:
                        errorMessage(stdscr, "Erreur : trop de joueurs")
                else:
                    errorMessage(stdscr, "Erreur : caractères inconnus")
                counter_x += 1
                if kill:
                    break
            counter_y += 1
            if kill:
                break
        if (compteO != compteX) and not kill:
            errorMessage(stdscr, "Erreur : nombre de boîtes et d'emplacements différents")
        if not kill:
            try:
                playerToken
            except NameError:
                errorMessage(stdscr, "Erreur : pas de joueur!")
            else:
                playa = playerToken

def main(stdscr):
    curses.curs_set(0)
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    global kill
    global reset
    #initialiser le jeu à partir de la carte fournie
    initGame(stdscr)
    while not kill:
        #afficher l'état actuel du jeu
        affichage(stdscr)
        #attendre l'input du joueur
        entry = stdscr.getch()
        #effectuer l'action associée
        if entry == curses.KEY_UP:
            playa.haut()
        if entry == curses.KEY_DOWN:
            playa.bas()
        if entry == curses.KEY_LEFT:
            playa.gauche()
        if entry == curses.KEY_RIGHT:
            playa.droite()
        if entry == "q":
            kill = True
        if entry == curses.KEY_EXIT:
            kill = True
        if entry == ' ':
            reset = True
        
        if reset:
            reset = False
            initGame(stdscr)
    curses.endwin()


if __name__ == "__main__":

    curses.wrapper(main)