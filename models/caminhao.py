import os
from math import pi

from core.group import Group
from core.matrix import Matrix
from core.mesh import Mesh
from core.texture import Texture
from geometry.boxGeometry import BoxGeometry
from geometry.cylinderGeometry import CylinderGeometry
from material.phongMaterial import PhongMaterial
from models.articulacao import Articulacao

PASTA_TEXTURAS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "assets", "textures")


# Caminhão de entrega construído por composição de primitivas.
#
# Sistema local: frente voltada para +X, Y para cima, origem no chão sob o centro.
#
# Hierarquia:
#   Caminhao (translação no eixo X)
#    ├── chassi, cabine (+ para-brisa, faróis, para-choque...), carroceria
#    ├── rodas[i]       Articulacao (rotação em Z = giro da roda)
#    │     └── pneu, cubo, raios
#    ├── pivoTampa      Articulacao na dobradiça superior traseira (rotação em Z)
#    │     └── tampa traseira, puxador, faixa de sinalização
#    └── encomenda      caixa transportada (troca de pai para a mão do robô)
class Caminhao(Group):

    RAIO_RODA = 0.5

    # limites da carroceria no eixo X (local)
    TRASEIRA_X = -3.7
    FRENTE_CARGA_X = 1.9
    PISO_CARGA_Y = 1.07     # altura do piso interno da carroceria
    TETO_CARGA_Y = 3.40     # altura da dobradiça da tampa

    def __init__(self):
        super().__init__()

        # estado da animação
        self.x = 0.0            # posição no eixo X do mundo
        self.velocidade = 0.0   # unidades por segundo

        metal = Texture(os.path.join(PASTA_TEXTURAS, "metal.png"))
        listras = Texture(os.path.join(PASTA_TEXTURAS, "listras.png"))
        papelao = Texture(os.path.join(PASTA_TEXTURAS, "caixa.png"))

        # materiais compartilhados entre as peças (todos recebem sombra)
        self.matCabine = PhongMaterial(properties={"baseColor": [0.85, 0.18, 0.12], "shininess": 48.0}, useShadow=True)
        self.matCarroceria = PhongMaterial(texture=metal, properties={"baseColor": [0.92, 0.94, 0.97], "specularStrength": 0.6}, useShadow=True)
        self.matFaixa = PhongMaterial(properties={"baseColor": [0.95, 0.55, 0.08]}, useShadow=True)
        self.matEscuro = PhongMaterial(properties={"baseColor": [0.16, 0.16, 0.18], "specularStrength": 0.3}, useShadow=True)
        self.matVidro = PhongMaterial(properties={"baseColor": [0.15, 0.25, 0.38], "shininess": 96.0, "specularStrength": 1.5}, useShadow=True)
        self.matFarol = PhongMaterial(properties={"baseColor": [1.4, 1.35, 1.1]}, useShadow=True)
        self.matPneu = PhongMaterial(properties={"baseColor": [0.10, 0.10, 0.11], "specularStrength": 0.15}, useShadow=True)
        self.matCubo = PhongMaterial(properties={"baseColor": [0.75, 0.75, 0.78]}, useShadow=True)
        self.matRaio = PhongMaterial(properties={"baseColor": [0.95, 0.75, 0.10]}, useShadow=True)
        self.matListras = PhongMaterial(texture=listras, properties={"repeatUV": [4.0, 1.0]}, useShadow=True)
        self.matCaixa = PhongMaterial(texture=papelao, properties={"specularStrength": 0.1}, useShadow=True)

        self.construirChassiECabine()
        self.construirCarroceria()
        self.construirRodas()
        self.construirTampa()
        self.construirCarga()

        self.atualizarTransformacao()

    # cria uma peça em forma de caixa e a adiciona a um nó pai
    def peca(self, pai, tamanho, posicao, material):
        mesh = Mesh(BoxGeometry(*tamanho), material)
        mesh.setPosition(posicao)
        pai.add(mesh)
        return mesh

    def construirChassiECabine(self):
        # chassi (longarina) logo acima das rodas
        self.peca(self, [7.2, 0.30, 1.4], [0.0, 0.80, 0.0], self.matEscuro)

        # cabine (cab-over)
        self.peca(self, [1.65, 1.75, 2.2], [2.78, 1.825, 0.0], self.matCabine)
        # para-brisa
        self.peca(self, [0.04, 0.75, 1.9], [3.61, 2.25, 0.0], self.matVidro)
        # janelas laterais
        self.peca(self, [0.75, 0.6, 0.02], [3.0, 2.25, 1.105], self.matVidro)
        self.peca(self, [0.75, 0.6, 0.02], [3.0, 2.25, -1.105], self.matVidro)
        # grade, faróis e para-choque
        self.peca(self, [0.03, 0.40, 1.0], [3.615, 1.35, 0.0], self.matEscuro)
        self.peca(self, [0.04, 0.20, 0.36], [3.62, 1.30, 0.80], self.matFarol)
        self.peca(self, [0.04, 0.20, 0.36], [3.62, 1.30, -0.80], self.matFarol)
        self.peca(self, [0.22, 0.30, 2.3], [3.66, 0.80, 0.0], self.matEscuro)
        # retrovisores
        self.peca(self, [0.08, 0.35, 0.06], [3.45, 2.20, 1.25], self.matEscuro)
        self.peca(self, [0.08, 0.35, 0.06], [3.45, 2.20, -1.25], self.matEscuro)
        # faixa decorativa da cabine
        self.peca(self, [1.66, 0.12, 2.21], [2.78, 1.45, 0.0], self.matFaixa)

    def construirCarroceria(self):
        comprimento = self.FRENTE_CARGA_X - self.TRASEIRA_X
        centroX = (self.FRENTE_CARGA_X + self.TRASEIRA_X) / 2
        alturaParede = self.TETO_CARGA_Y - self.PISO_CARGA_Y
        centroY = (self.TETO_CARGA_Y + self.PISO_CARGA_Y) / 2

        # piso, teto, laterais e parede frontal; a traseira é a tampa articulada
        self.peca(self, [comprimento, 0.12, 2.3], [centroX, self.PISO_CARGA_Y - 0.06, 0.0], self.matEscuro)
        self.peca(self, [comprimento, 0.08, 2.3], [centroX, self.TETO_CARGA_Y + 0.04, 0.0], self.matCarroceria)
        self.peca(self, [comprimento, alturaParede, 0.08], [centroX, centroY, 1.11], self.matCarroceria)
        self.peca(self, [comprimento, alturaParede, 0.08], [centroX, centroY, -1.11], self.matCarroceria)
        self.peca(self, [0.08, alturaParede, 2.3], [self.FRENTE_CARGA_X - 0.04, centroY, 0.0], self.matCarroceria)

        # faixas laranja nas laterais (identidade visual)
        self.peca(self, [comprimento - 0.4, 0.25, 0.02], [centroX, 1.55, 1.16], self.matFaixa)
        self.peca(self, [comprimento - 0.4, 0.25, 0.02], [centroX, 1.55, -1.16], self.matFaixa)

        # moldura traseira (colunas e travessa superior)
        x = self.TRASEIRA_X + 0.05
        self.peca(self, [0.12, alturaParede + 0.1, 0.12], [x, centroY, 1.12], self.matEscuro)
        self.peca(self, [0.12, alturaParede + 0.1, 0.12], [x, centroY, -1.12], self.matEscuro)
        self.peca(self, [0.12, 0.12, 2.36], [x, self.TETO_CARGA_Y + 0.06, 0.0], self.matEscuro)

    def construirRodas(self):
        # geometrias compartilhadas: o cilindro do framework tem eixo Y,
        # então é girado 90° em X para ficar com o eixo em Z (eixo da roda)
        alinhar = Matrix.makeRotationX(pi / 2)
        geoPneu = CylinderGeometry(radius=self.RAIO_RODA, height=0.35, radialSegments=24, heightSegments=1)
        geoPneu.applyMatrix(alinhar)
        geoCubo = CylinderGeometry(radius=0.26, height=0.37, radialSegments=16, heightSegments=1)
        geoCubo.applyMatrix(alinhar)
        # raios em cruz: tornam a rotação da roda visível
        geoRaioA = BoxGeometry(0.46, 0.07, 0.39)
        geoRaioB = BoxGeometry(0.07, 0.46, 0.39)

        self.rodas = []
        for eixoX in [2.6, -1.9, -2.95]:
            for lado in [1.0, -1.0]:
                roda = Articulacao([eixoX, self.RAIO_RODA, lado * 1.0], eixo="z")
                roda.add(Mesh(geoPneu, self.matPneu))
                roda.add(Mesh(geoCubo, self.matCubo))
                roda.add(Mesh(geoRaioA, self.matRaio))
                roda.add(Mesh(geoRaioB, self.matRaio))
                self.add(roda)
                self.rodas.append(roda)

    def construirTampa(self):
        alturaTampa = self.TETO_CARGA_Y - self.PISO_CARGA_Y

        # pivô na dobradiça superior da traseira: a tampa gira em torno de Z,
        # levantando para trás (ângulo negativo)
        self.pivoTampa = Articulacao([self.TRASEIRA_X - 0.02, self.TETO_CARGA_Y, 0.0], eixo="z")
        self.add(self.pivoTampa)

        # a tampa pende para baixo a partir da dobradiça
        self.peca(self.pivoTampa, [0.07, alturaTampa, 2.2], [-0.035, -alturaTampa / 2, 0.0], self.matCarroceria)
        # puxador
        self.peca(self.pivoTampa, [0.06, 0.07, 0.8], [-0.10, -alturaTampa + 0.45, 0.0], self.matEscuro)
        # faixa de sinalização na borda inferior
        self.peca(self.pivoTampa, [0.02, 0.2, 2.2], [-0.08, -alturaTampa + 0.12, 0.0], self.matListras)
        # dobradiças
        self.peca(self.pivoTampa, [0.10, 0.10, 0.25], [-0.02, -0.03, 0.75], self.matEscuro)
        self.peca(self.pivoTampa, [0.10, 0.10, 0.25], [-0.02, -0.03, -0.75], self.matEscuro)

    def construirCarga(self):
        # encomenda que o robô vai retirar, perto da porta traseira
        self.encomenda = self.peca(self, [0.6, 0.55, 0.9], self.posicaoInicialEncomenda(), self.matCaixa)
        self.transformInicialEncomenda = self.encomenda.transform.copy()

        # outras caixas no fundo da carroceria (apenas decorativas)
        self.peca(self, [0.8, 0.7, 0.9], [0.9, self.PISO_CARGA_Y + 0.35, 0.5], self.matCaixa)
        self.peca(self, [0.8, 0.7, 0.9], [0.9, self.PISO_CARGA_Y + 0.35, -0.5], self.matCaixa)
        self.peca(self, [0.8, 0.6, 0.9], [0.9, self.PISO_CARGA_Y + 1.0, 0.0], self.matCaixa)
        self.peca(self, [0.7, 0.6, 0.8], [-0.2, self.PISO_CARGA_Y + 0.3, 0.55], self.matCaixa)

    # posição local da encomenda (0,15 de folga da porta)
    def posicaoInicialEncomenda(self):
        return [self.TRASEIRA_X + 0.15 + 0.3, self.PISO_CARGA_Y + 0.275, 0.0]

    # ------------------------------------------------------------------
    # Transformações usadas pela animação
    # ------------------------------------------------------------------
    def atualizarTransformacao(self):
        self.transform = Matrix.makeTranslation(self.x, 0, 0)

    def setPosicaoX(self, x):
        self.x = x
        self.atualizarTransformacao()

    # desloca o caminhão e gira as rodas de forma coerente (rolamento sem
    # deslizamento): ângulo = distância / raio. O sinal é negativo porque,
    # andando para +X, a roda gira no sentido horário visto de +Z.
    def avancar(self, distancia):
        self.setPosicaoX(self.x + distancia)
        for roda in self.rodas:
            roda.girar(-distancia / self.RAIO_RODA)

    # ângulo de abertura da tampa (0 = fechada; negativo = abrindo para cima)
    def setAnguloTampa(self, angulo):
        self.pivoTampa.setAngulo(angulo)

    # devolve a encomenda à posição original dentro da carroceria
    def recarregar(self):
        if self.encomenda.parent is not None:
            self.encomenda.parent.remove(self.encomenda)
        self.add(self.encomenda)
        self.encomenda.transform = self.transformInicialEncomenda.copy()
