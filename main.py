"""
Trabalho de Computação Gráfica - Robô de serviço (Tema 1) + Caminhão de entrega (Tema 13)

Execução:
    python main.py            (limite padrão de 60 FPS)
    python main.py --fps 20   (teste: as animações têm a mesma duração em qualquer FPS)
"""
import argparse
from math import atan2, sqrt

# Desativa a verificação de erro automática do PyOpenGL (chama glGetError após
# CADA função e reduz muito o FPS). Deve ser feito antes de importar OpenGL.GL.
# Para depurar erros de OpenGL, troque para True.
import OpenGL
OpenGL.ERROR_CHECKING = False

import pygame

from animation.interacao import Interacao
from core.base import Base
from core.camera import Camera
from core.matrix import Matrix
from core.renderer import Renderer
from core.scene import Scene
from environment.cenario import Cenario
from extras.movementRig import MovementRig
from light.ambientLight import AmbientLight
from light.directionalLight import DirectionalLight
from models.caminhao import Caminhao
from models.robo import Robo

LARGURA_JANELA, ALTURA_JANELA = 1280, 720
TITULO = "Robô de Serviço & Caminhão de Entrega"


class Main(Base):

    def initialize(self):
        print("Inicializando a cena...")

        self.renderer = Renderer(clearColor=[0.62, 0.74, 0.86])
        self.scene = Scene()

        # ---------------- câmera em perspectiva ----------------
        self.camera = Camera(angleOfView=60, aspectRatio=LARGURA_JANELA / ALTURA_JANELA, near=0.1, far=200)
        self.rig = MovementRig(unitsPerSecond=6, degreesPerSecond=60)
        self.rig.add(self.camera)
        self.scene.add(self.rig)
        self.vistaCamera(1)

        # ---------------- iluminação ----------------
        # luz ambiente: evita regiões totalmente escuras
        self.scene.add(AmbientLight(color=[0.30, 0.30, 0.34]))

        # luz direcional (Sol): projeta as sombras
        self.sol = DirectionalLight(color=[0.85, 0.82, 0.75], direction=[-0.55, -1.0, -0.40])
        # posição usada apenas pela câmera de sombra (fica "antes" da cena, na direção da luz)
        self.sol.setPosition([0.55 * 25 + 1.0, 25.0, 0.40 * 25])
        self.scene.add(self.sol)

        # luz direcional de preenchimento (fraca, vinda do lado oposto)
        self.scene.add(DirectionalLight(color=[0.18, 0.20, 0.26], direction=[0.6, -0.5, 0.7]))

        # ---------------- Shadow Mapping ----------------
        # câmera ortográfica da luz cobre toda a plataforma
        self.renderer.enableShadows(self.sol, strength=0.65, resolution=[2048, 2048],
                                    cameraBounds=[-21, 21, -16, 16, 1, 60], bias=0.0015)

        # ---------------- modelos e cenário ----------------
        self.cenario = Cenario(xEstacionamento=Interacao.X_ESTACIONAMENTO,
                               posicaoBaseRobo=Interacao.BASE_ROBO,
                               posicaoMesa=Interacao.MESA)
        self.scene.add(self.cenario)

        self.caminhao = Caminhao()
        self.scene.add(self.caminhao)

        self.robo = Robo()
        self.scene.add(self.robo)

        # ---------------- sequência de animação ----------------
        self.interacao = Interacao(self.caminhao, self.robo, self.cenario)
        self.pausado = False
        self.legendaAtual = None
        self.tempoLegenda = 0.0

        print("Controles: W/A/S/D mover | R/F subir/descer | Q/E girar | T/G olhar cima/baixo")
        print("           P pausar | C continuar | N reiniciar | 1-4 vistas | ESC sair")

    # posiciona o rig da câmera em "posicao", olhando para "alvo"
    def posicionarCamera(self, posicao, alvo):
        dx = alvo[0] - posicao[0]
        dy = alvo[1] - posicao[1]
        dz = alvo[2] - posicao[2]
        # o rig gira em Y (horizontal) e o lookAttachment em X (vertical)
        yaw = atan2(-dx, -dz)
        pitch = atan2(dy, sqrt(dx * dx + dz * dz))
        self.rig.transform = Matrix.makeTranslation(*posicao) @ Matrix.makeRotationY(yaw)
        self.rig.lookAttachment.transform = Matrix.makeRotationX(pitch)

    def vistaCamera(self, numero):
        if numero == 1:      # visão geral
            self.posicionarCamera([4.0, 11.0, 19.0], [-0.5, 0.5, 0.0])
        elif numero == 2:    # lateral, próxima ao robô e à traseira do caminhão
            self.posicionarCamera([1.5, 4.2, 10.5], [-2.2, 1.2, 1.5])
        elif numero == 3:    # atrás do caminhão, de frente para a tampa
            self.posicionarCamera([-9.0, 4.0, 4.5], [-0.5, 1.6, 0.0])
        elif numero == 4:    # vista superior
            self.posicionarCamera([0.0, 26.0, 8.0], [0.0, 0.0, 0.0])

    def update(self):
        # delta time limitado: evita saltos se a janela travar (ex.: ao ser arrastada)
        deltaTime = min(self.deltaTime, 0.05)

        # ---------------- teclado ----------------
        if self.input.isKeyDown("escape"):
            self.running = False
        if self.input.isKeyDown("p"):
            self.pausado = True
        if self.input.isKeyDown("c"):
            self.pausado = False
        if self.input.isKeyDown("n"):
            self.interacao.reiniciar()
        for numero in range(1, 5):
            if self.input.isKeyDown(str(numero)):
                self.vistaCamera(numero)

        # a pausa congela apenas a animação; a câmera e a renderização continuam
        if not self.pausado:
            self.interacao.update(deltaTime)

        self.rig.update(self.input, deltaTime)

        self.renderer.render(self.scene, self.camera)

        self.atualizarLegenda(deltaTime)

    # título da janela: etapa atual, estado da pausa e FPS
    def atualizarLegenda(self, deltaTime):
        self.tempoLegenda += deltaTime
        nome, etapa = self.interacao.estado
        legenda = "%s  |  Etapa %d/6: %s%s" % (TITULO, etapa, nome, "  |  [PAUSADO - C para continuar]" if self.pausado else "")
        if legenda != self.legendaAtual or self.tempoLegenda > 0.5:
            self.legendaAtual = legenda
            self.tempoLegenda = 0.0
            pygame.display.set_caption("%s  |  %.0f FPS" % (legenda, self.clock.get_fps()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fps", type=int, default=60, help="limite de quadros por segundo")
    argumentos = parser.parse_args()

    Main(screenSize=[LARGURA_JANELA, ALTURA_JANELA], fps=argumentos.fps).run()
