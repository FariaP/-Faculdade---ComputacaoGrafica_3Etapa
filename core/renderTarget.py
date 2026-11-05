import pygame
from OpenGL.GL import *

from core.texture import Texture


# Framebuffer fora da tela: a cena é renderizada em uma textura
# (usado para gerar o mapa de profundidade do Shadow Mapping)
class RenderTarget(object):

    def __init__(self, resolution=[512, 512], texture=None, properties={}):
        self.width, self.height = resolution

        if texture is not None:
            self.texture = texture
        else:
            self.texture = Texture(None, {
                "magFilter": GL_LINEAR,
                "minFilter": GL_LINEAR,
                "wrap": GL_CLAMP_TO_EDGE,
            })
            self.texture.setProperties(properties)
            self.texture.surface = pygame.Surface(resolution)
            self.texture.uploadData()

        # cria o framebuffer e usa a textura como buffer de cor
        self.framebufferRef = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebufferRef)
        glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, self.texture.textureRef, 0)

        # buffer de profundidade, necessário para o teste de profundidade
        depthBufferRef = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, depthBufferRef)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, self.width, self.height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depthBufferRef)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("Framebuffer status error")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
