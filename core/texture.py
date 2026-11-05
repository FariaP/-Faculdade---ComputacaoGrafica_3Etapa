import pygame
from OpenGL.GL import *


# Carrega uma imagem e a envia para a GPU como textura 2D
class Texture(object):

    def __init__(self, fileName=None, properties={}):
        # superfície do pygame que guarda os pixels da imagem
        self.surface = None

        # referência do objeto de textura na GPU
        self.textureRef = glGenTextures(1)

        # filtros e modo de repetição padrão
        self.properties = {
            "magFilter": GL_LINEAR,
            "minFilter": GL_LINEAR_MIPMAP_LINEAR,
            "wrap": GL_REPEAT,
        }
        self.setProperties(properties)

        if fileName is not None:
            self.loadImage(fileName)
            self.uploadData()

    def loadImage(self, fileName):
        self.surface = pygame.image.load(fileName)

    def setProperties(self, props):
        for name, data in props.items():
            if name in self.properties.keys():
                self.properties[name] = data
            else:
                raise Exception("Texture has no property with name: " + name)

    # envia os pixels para a GPU e configura filtros e repetição
    def uploadData(self):
        width = self.surface.get_width()
        height = self.surface.get_height()

        # converte para bytes RGBA, invertendo a imagem verticalmente
        # (no OpenGL a coordenada V = 0 fica na parte de baixo da imagem)
        toBytes = getattr(pygame.image, "tobytes", None) or pygame.image.tostring
        pixelData = toBytes(self.surface, "RGBA", True)

        glBindTexture(GL_TEXTURE_2D, self.textureRef)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, pixelData)
        glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, self.properties["magFilter"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, self.properties["minFilter"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, self.properties["wrap"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, self.properties["wrap"])
        # cor usada fora da textura quando wrap = GL_CLAMP_TO_BORDER
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [1, 1, 1, 1])
