from OpenGL.GL import *

from core.camera import Camera
from core.renderTarget import RenderTarget
from material.depthMaterial import DepthMaterial


# Dados do Shadow Mapping (seção 6.9 do livro):
#  - uma câmera ortográfica presa à luz direcional (vê a cena "pela luz");
#  - um RenderTarget onde é gravado o mapa de profundidade;
#  - o DepthMaterial, que escreve a profundidade de cada fragmento.
class Shadow(object):

    def __init__(self, lightSource, strength=0.5, resolution=[512, 512],
                 cameraBounds=[-5, 5, -5, 5, 0, 20], bias=0.01):
        # luz direcional que projeta as sombras
        self.lightSource = lightSource

        # a câmera é filha da luz: herda sua posição e direção
        self.camera = Camera()
        left, right, bottom, top, near, far = cameraBounds
        self.camera.setOrthographic(left, right, bottom, top, near, far)
        self.lightSource.add(self.camera)

        # textura que armazena as profundidades vistas pela luz;
        # filtro NEAREST, pois a profundidade fica codificada em RGB
        self.renderTarget = RenderTarget(resolution, properties={
            "magFilter": GL_NEAREST,
            "minFilter": GL_NEAREST,
            "wrap": GL_CLAMP_TO_BORDER,
        })

        self.material = DepthMaterial()

        # quanto a sombra escurece a superfície (0 = nada, 1 = preto)
        self.strength = strength

        # tolerância para evitar "shadow acne" (auto-sombreamento incorreto)
        self.bias = bias

    # atualiza as matrizes da câmera da luz antes da passada de profundidade
    def updateInternal(self):
        self.camera.updateViewMatrix()
        self.material.uniforms["viewMatrix"].data = self.camera.viewMatrix
        self.material.uniforms["projectionMatrix"].data = self.camera.projectionMatrix
