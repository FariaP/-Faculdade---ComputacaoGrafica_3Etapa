from math import pi, sin, cos, atan2, sqrt

from core.group import Group
from core.matrix import Matrix
from core.mesh import Mesh
from geometry.boxGeometry import BoxGeometry
from geometry.cylinderGeometry import CylinderGeometry
from geometry.sphereGeometry import SphereGeometry
from material.phongMaterial import PhongMaterial
from models.articulacao import Articulacao


# Robô de serviço construído por composição de primitivas.
#
# Sistema local: frente voltada para +X, Y para cima, origem no chão.
#
# Hierarquia:
#   Robo (translação no plano XZ + rotação em Y = direção)
#    ├── base (disco) e rodas[i]           Articulacao em Z (giro das rodas)
#    └── tronco
#         ├── corpo, painel do peito, pescoço
#         ├── pivoCabeca                   Articulacao em Y (virar a cabeça)
#         │     └── cabeça, visor, olhos, antena, sinalizador
#         └── ombros[lado]                 Articulacao em Z (levantar o braço)
#               └── braço
#                    └── cotovelos[lado]   Articulacao em Z (dobrar o antebraço)
#                          └── antebraço
#                               └── maos[lado]   (garra que segura a encomenda)
#
# Como os braços são filhos do tronco, acompanham todo o deslocamento e a
# rotação do robô sem perder a posição relativa.
class Robo(Group):

    COMPRIMENTO_BRACO = 0.60
    COMPRIMENTO_ANTEBRACO = 0.55
    RAIO_RODA = 0.18

    def __init__(self):
        super().__init__()

        # estado da animação
        self.x = 0.0
        self.z = 0.0
        self.yaw = 0.0          # rotação em torno de Y (0 = frente para +X)

        self.matCorpo = PhongMaterial(properties={"baseColor": [0.98, 0.72, 0.10], "shininess": 40.0}, useShadow=True)
        self.matEscuro = PhongMaterial(properties={"baseColor": [0.20, 0.21, 0.24], "specularStrength": 0.5}, useShadow=True)
        self.matJunta = PhongMaterial(properties={"baseColor": [0.60, 0.62, 0.66], "shininess": 64.0}, useShadow=True)
        self.matVisor = PhongMaterial(properties={"baseColor": [0.05, 0.06, 0.08], "shininess": 96.0, "specularStrength": 1.5}, useShadow=True)
        # materiais exclusivos: a cor muda durante a animação
        self.matOlhos = PhongMaterial(properties={"baseColor": [0.3, 1.2, 1.4]}, useShadow=False)
        self.matSinalizador = PhongMaterial(properties={"baseColor": [1.4, 0.45, 0.05]}, useShadow=False)

        self.construirBase()
        self.construirTronco()
        self.construirCabeca()
        self.construirBracos()

        self.atualizarTransformacao()

    def peca(self, pai, geometria, posicao, material):
        mesh = Mesh(geometria, material)
        mesh.setPosition(posicao)
        pai.add(mesh)
        return mesh

    def construirBase(self):
        # base cilíndrica com duas rodas laterais
        self.peca(self, CylinderGeometry(radius=0.5, height=0.28, radialSegments=32, heightSegments=1),
                  [0, 0.26, 0], self.matEscuro)
        self.peca(self, CylinderGeometry(radius=0.52, height=0.06, radialSegments=32, heightSegments=1),
                  [0, 0.40, 0], self.matCorpo)

        geoRoda = CylinderGeometry(radius=self.RAIO_RODA, height=0.12, radialSegments=20, heightSegments=1)
        geoRoda.applyMatrix(Matrix.makeRotationX(pi / 2))
        geoRaio = BoxGeometry(0.30, 0.05, 0.13)

        self.rodas = []
        for lado in [1.0, -1.0]:
            roda = Articulacao([0, self.RAIO_RODA, lado * 0.52], eixo="z")
            roda.add(Mesh(geoRoda, self.matEscuro))
            roda.add(Mesh(geoRaio, self.matCorpo))
            self.add(roda)
            self.rodas.append(roda)

    def construirTronco(self):
        self.tronco = Group()
        self.tronco.setPosition([0, 0.40, 0])
        self.add(self.tronco)

        # cintura e corpo
        self.peca(self.tronco, CylinderGeometry(radius=0.2, height=0.22, radialSegments=20, heightSegments=1),
                  [0, 0.11, 0], self.matJunta)
        self.peca(self.tronco, BoxGeometry(0.70, 0.95, 0.90), [0, 0.675, 0], self.matCorpo)
        # painel do peito com luzes
        self.peca(self.tronco, BoxGeometry(0.04, 0.40, 0.55), [0.36, 0.72, 0], self.matEscuro)
        self.peca(self.tronco, BoxGeometry(0.02, 0.06, 0.35), [0.385, 0.80, 0], self.matOlhos)
        self.peca(self.tronco, BoxGeometry(0.02, 0.06, 0.20), [0.385, 0.66, 0], self.matSinalizador)
        # pescoço
        self.peca(self.tronco, CylinderGeometry(radius=0.1, height=0.14, radialSegments=16, heightSegments=1),
                  [0, 1.20, 0], self.matJunta)

    def construirCabeca(self):
        self.pivoCabeca = Articulacao([0, 1.26, 0], eixo="y")
        self.tronco.add(self.pivoCabeca)

        self.peca(self.pivoCabeca, BoxGeometry(0.50, 0.40, 0.55), [0, 0.20, 0], self.matCorpo)
        self.peca(self.pivoCabeca, BoxGeometry(0.04, 0.17, 0.44), [0.25, 0.22, 0], self.matVisor)
        geoOlho = SphereGeometry(radius=0.055, radiusSegments=12, heightSegments=8)
        self.peca(self.pivoCabeca, geoOlho, [0.27, 0.22, 0.11], self.matOlhos)
        self.peca(self.pivoCabeca, geoOlho, [0.27, 0.22, -0.11], self.matOlhos)
        # antena
        self.peca(self.pivoCabeca, CylinderGeometry(radius=0.02, height=0.25, radialSegments=8, heightSegments=1),
                  [0, 0.52, 0], self.matJunta)
        # sinalizador luminoso (pulsa por ESCALA durante o trabalho)
        self.sinalizador = self.peca(self.pivoCabeca, SphereGeometry(radius=0.06, radiusSegments=12, heightSegments=8),
                                     [0, 0.66, 0], self.matSinalizador)
        self.sinalizador.castShadow = False

    def construirBracos(self):
        geoJuntaOmbro = SphereGeometry(radius=0.13, radiusSegments=16, heightSegments=10)
        geoJuntaCotovelo = SphereGeometry(radius=0.10, radiusSegments=16, heightSegments=10)
        geoBraco = BoxGeometry(0.18, self.COMPRIMENTO_BRACO, 0.18)
        geoAntebraco = BoxGeometry(0.16, self.COMPRIMENTO_ANTEBRACO, 0.16)
        geoGarra = BoxGeometry(0.20, 0.24, 0.05)
        geoPunho = BoxGeometry(0.12, 0.06, 0.14)

        self.ombros = []
        self.cotovelos = []
        self.maos = []
        for lado in [1.0, -1.0]:
            # ombro: na lateral superior do corpo
            ombro = Articulacao([0, 1.10, lado * 0.55], eixo="z")
            self.tronco.add(ombro)
            self.peca(ombro, geoJuntaOmbro, [0, 0, 0], self.matJunta)
            self.peca(ombro, geoBraco, [0, -self.COMPRIMENTO_BRACO / 2, 0], self.matEscuro)

            # cotovelo: no fim do braço
            cotovelo = Articulacao([0, -self.COMPRIMENTO_BRACO, 0], eixo="z")
            ombro.add(cotovelo)
            self.peca(cotovelo, geoJuntaCotovelo, [0, 0, 0], self.matJunta)
            self.peca(cotovelo, geoAntebraco, [0, -self.COMPRIMENTO_ANTEBRACO / 2, 0], self.matCorpo)

            # mão: no fim do antebraço; a garra fica voltada para dentro
            mao = Group()
            mao.setPosition([0, -self.COMPRIMENTO_ANTEBRACO, 0])
            cotovelo.add(mao)
            self.peca(mao, geoPunho, [0, -0.02, 0], self.matJunta)
            self.peca(mao, geoGarra, [0, -0.13, -lado * 0.055], self.matJunta)

            self.ombros.append(ombro)
            self.cotovelos.append(cotovelo)
            self.maos.append(mao)

    # ------------------------------------------------------------------
    # Transformações usadas pela animação
    # ------------------------------------------------------------------

    # matriz local do robô: translação no chão seguida da rotação em Y
    def atualizarTransformacao(self):
        self.transform = Matrix.makeTranslation(self.x, 0, self.z) @ Matrix.makeRotationY(self.yaw)

    def setPosicao(self, x, z, yaw=None):
        self.x, self.z = x, z
        if yaw is not None:
            self.yaw = yaw
        self.atualizarTransformacao()

    # pose dos dois braços (ângulos em radianos);
    # ombro > 0 levanta o braço para a frente, cotovelo > 0 dobra o antebraço para cima
    def setPoseBracos(self, anguloOmbro, anguloCotovelo):
        for ombro in self.ombros:
            ombro.setAngulo(anguloOmbro)
        for cotovelo in self.cotovelos:
            cotovelo.setAngulo(anguloCotovelo)

    def getPoseBracos(self):
        return self.ombros[0].angulo, self.cotovelos[0].angulo

    def setAnguloCabeca(self, angulo):
        self.pivoCabeca.setAngulo(angulo)

    def setCorOlhos(self, cor):
        self.matOlhos.uniforms["baseColor"].data = cor

    # pulso do sinalizador: ESCALA uniforme aplicada à matriz local
    def pulsarSinalizador(self, tempo, ativo):
        fator = 1.0 + 0.45 * abs(sin(tempo * 6.0)) if ativo else 1.0
        self.sinalizador.transform = Matrix.makeTranslation(0, 0.66, 0) @ Matrix.makeScale(fator)

    # direção (yaw) que aponta a frente do robô (+X local) para (dx, dz)
    @staticmethod
    def yawPara(dx, dz):
        return atan2(-dz, dx)

    # gira em direção ao ângulo alvo pelo menor caminho; True quando alinhado
    def girarPara(self, yawAlvo, deltaTime, velocidadeAngular=2.4):
        diferenca = (yawAlvo - self.yaw + pi) % (2 * pi) - pi
        passo = velocidadeAngular * deltaTime
        if abs(diferenca) <= passo:
            self.yaw = yawAlvo
            self.atualizarTransformacao()
            return True
        self.yaw += passo if diferenca > 0 else -passo
        # as rodas giram em sentidos opostos ao virar no lugar
        self.rodas[0].girar(-passo * 0.5)
        self.rodas[1].girar(passo * 0.5)
        self.atualizarTransformacao()
        return False

    # desloca o robô até (alvoX, alvoZ): primeiro vira, depois anda.
    # re=True: anda de ré (mantém a frente voltada para o lado oposto).
    # A velocidade diminui perto do destino (parada suave). True ao chegar.
    def moverPara(self, alvoX, alvoZ, deltaTime, velocidadeMaxima=1.6, re=False):
        dx = alvoX - self.x
        dz = alvoZ - self.z
        distancia = sqrt(dx * dx + dz * dz)
        if distancia < 0.002:
            self.setPosicao(alvoX, alvoZ)
            return True

        yawAlvo = self.yawPara(-dx, -dz) if re else self.yawPara(dx, dz)
        if not self.girarPara(yawAlvo, deltaTime):
            return False

        velocidade = min(velocidadeMaxima, 0.25 + 1.8 * distancia)
        passo = min(velocidade * deltaTime, distancia)
        self.x += dx / distancia * passo
        self.z += dz / distancia * passo

        # giro das rodas proporcional à distância percorrida
        sentido = 1.0 if re else -1.0
        for roda in self.rodas:
            roda.girar(sentido * passo / self.RAIO_RODA)

        self.atualizarTransformacao()
        return False

    # posição/yaw iniciais e braços em repouso
    def reiniciar(self, x, z, yaw):
        self.setPosicao(x, z, yaw)
        self.setPoseBracos(0.0, 0.0)
        self.setAnguloCabeca(0.0)
        for roda in self.rodas:
            roda.setAngulo(0.0)
