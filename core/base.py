import sys

import pygame

from core.input import Input


# Classe base de toda aplicação: cria a janela, o contexto OpenGL e o laço principal
class Base(object):

    def __init__(self, screenSize=[512, 512], fps=60):
        pygame.init()
        displayFlags = pygame.DOUBLEBUF | pygame.OPENGL

        # antisserrilhamento (multisampling)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)

        # contexto OpenGL 3.3 core profile
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                        pygame.GL_CONTEXT_PROFILE_CORE)

        self.screen = pygame.display.set_mode(screenSize, displayFlags)
        pygame.display.set_caption("Graphics Window")

        self.running = True
        self.clock = pygame.time.Clock()
        self.input = Input()

        # limite de quadros por segundo (as animações NÃO dependem dele)
        self.fps = fps

        # tempo total decorrido e tempo do último quadro (delta time), em segundos
        self.time = 0
        self.deltaTime = 0

    # implementado pela aplicação
    def initialize(self):
        pass

    # implementado pela aplicação
    def update(self):
        pass

    def run(self):
        self.initialize()

        while self.running:
            self.input.update()
            if self.input.quit:
                self.running = False

            # delta time: segundos decorridos desde o quadro anterior
            self.deltaTime = self.clock.get_time() / 1000
            self.time += self.deltaTime

            self.update()

            pygame.display.flip()
            self.clock.tick(self.fps)

        pygame.quit()
        sys.exit()
