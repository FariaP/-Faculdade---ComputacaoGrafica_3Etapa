import pygame


# Gerencia os eventos de teclado e de fechamento da janela
class Input(object):

    def __init__(self):
        # indica se o usuário fechou a janela
        self.quit = False

        # teclas pressionadas neste quadro (discretas)
        self.keyDownList = []
        # teclas mantidas pressionadas (contínuas)
        self.keyPressedList = []
        # teclas soltas neste quadro (discretas)
        self.keyUpList = []

    def update(self):
        # as listas discretas valem apenas por um quadro
        self.keyDownList = []
        self.keyUpList = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True

            if event.type == pygame.KEYDOWN:
                keyName = pygame.key.name(event.key)
                self.keyDownList.append(keyName)
                if keyName not in self.keyPressedList:
                    self.keyPressedList.append(keyName)

            if event.type == pygame.KEYUP:
                keyName = pygame.key.name(event.key)
                if keyName in self.keyPressedList:
                    self.keyPressedList.remove(keyName)
                self.keyUpList.append(keyName)

    def isKeyDown(self, keyCode):
        return keyCode in self.keyDownList

    def isKeyPressed(self, keyCode):
        return keyCode in self.keyPressedList

    def isKeyUp(self, keyCode):
        return keyCode in self.keyUpList
