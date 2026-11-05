import os

from core.group import Group
from core.matrix import Matrix
from core.mesh import Mesh
from core.texture import Texture
from geometry.boxGeometry import BoxGeometry
from geometry.cylinderGeometry import CylinderGeometry
from geometry.sphereGeometry import SphereGeometry
from material.lambertMaterial import LambertMaterial
from material.phongMaterial import PhongMaterial

PASTA_TEXTURAS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              "assets", "textures")


# Plataforma fixa de recebimento e distribuição.
#
# Vista de cima (X para a direita, Z para baixo):
#
#   z=-9  ┌────────────────────── painel ao fundo ──────────────────────┐
#         │  pilha de caixas                       semáforo              │
#   z= 0  │ ═ início ══ faixa do caminhão ═[atendimento][ estacionamento ]═ fim
#         │                                 ║  (trajeto do robô)          │
#   z=+6  │              mesa ◄ [base do robô]                           │
#   z=+9  └──────────────────────────────────────────────────────────────┘
#        x=-17                                                         x=+17
class Cenario(Group):

    LARGURA = 34.0      # eixo X
    PROFUNDIDADE = 19.0 # eixo Z

    def __init__(self, xEstacionamento, posicaoBaseRobo, posicaoMesa):
        super().__init__()

        concreto = Texture(os.path.join(PASTA_TEXTURAS, "concreto.png"))
        listras = Texture(os.path.join(PASTA_TEXTURAS, "listras.png"))
        metal = Texture(os.path.join(PASTA_TEXTURAS, "metal.png"))
        papelao = Texture(os.path.join(PASTA_TEXTURAS, "caixa.png"))

        # piso: Lambert (fosco) com textura de concreto repetida
        self.matPiso = LambertMaterial(texture=concreto,
                                       properties={"repeatUV": [8.0, 4.5], "baseColor": [0.95, 0.95, 0.95]},
                                       useShadow=True)
        self.matBordaPlataforma = LambertMaterial(properties={"baseColor": [0.32, 0.34, 0.38]}, useShadow=True)
        self.matFaixaBranca = LambertMaterial(properties={"baseColor": [0.95, 0.95, 0.92]}, useShadow=True)
        self.matFaixaAmarela = LambertMaterial(properties={"baseColor": [1.0, 0.78, 0.10]}, useShadow=True)
        self.matAtendimento = LambertMaterial(texture=listras, properties={"repeatUV": [6.0, 1.0]}, useShadow=True)
        self.matAreaAtendimento = LambertMaterial(properties={"baseColor": [0.30, 0.55, 0.85]}, useShadow=True)
        self.matBaseRobo = LambertMaterial(properties={"baseColor": [0.20, 0.42, 0.75]}, useShadow=True)
        self.matPilar = PhongMaterial(properties={"baseColor": [0.28, 0.30, 0.34]}, useShadow=True)
        self.matTopoPilar = PhongMaterial(properties={"baseColor": [1.0, 0.75, 0.1]}, useShadow=True)
        self.matPainel = PhongMaterial(texture=metal, properties={"baseColor": [0.55, 0.62, 0.72], "repeatUV": [6.0, 1.0],
                                                                  "specularStrength": 0.4}, useShadow=True)
        self.matMesa = PhongMaterial(properties={"baseColor": [0.35, 0.37, 0.42]}, useShadow=True)
        self.matCaixa = PhongMaterial(texture=papelao, properties={"specularStrength": 0.1}, useShadow=True)
        self.matPalete = LambertMaterial(properties={"baseColor": [0.62, 0.45, 0.25]}, useShadow=True)
        # lâmpada do semáforo: cor alterada pela animação
        self.matLampada = PhongMaterial(properties={"baseColor": [0.2, 1.3, 0.3]}, useShadow=False)

        # geometrias estáticas agrupadas por material (ver "peca")
        self.geometriasPorMaterial = {}

        self.construirPlataforma()
        self.construirFaixas(xEstacionamento, posicaoBaseRobo)
        self.construirDecoracao(posicaoMesa)
        self.construirSemaforo(xEstacionamento)

        # uma única malha por material: menos chamadas de desenho por quadro
        for material, geometria in self.geometriasPorMaterial.values():
            self.add(Mesh(geometria, material))

    # Adiciona uma peça ESTÁTICA do cenário. Como o cenário nunca se move,
    # os vértices são transformados uma única vez (Geometry.applyMatrix) e
    # unidos aos das outras peças de mesmo material (Geometry.merge).
    # "matriz" permite combinar translação e escala; o padrão é só translação.
    def peca(self, geometria, posicao, material, matriz=None):
        if matriz is None:
            matriz = Matrix.makeTranslation(*posicao)
        geometria.applyMatrix(matriz)
        chave = id(material)
        if chave in self.geometriasPorMaterial:
            self.geometriasPorMaterial[chave][1].merge(geometria)
        else:
            self.geometriasPorMaterial[chave] = (material, geometria)

    def construirPlataforma(self):
        # placa principal: o topo fica em y = 0
        self.peca(BoxGeometry(self.LARGURA, 0.4, self.PROFUNDIDADE), [0, -0.2, 0], self.matPiso)
        # rodapé escuro, um pouco maior, dando acabamento à plataforma
        self.peca(BoxGeometry(self.LARGURA + 0.6, 0.3, self.PROFUNDIDADE + 0.6), [0, -0.45, 0], self.matBordaPlataforma)

    def construirFaixas(self, xEstacionamento, posicaoBaseRobo):
        y = 0.01       # marcações ligeiramente acima do piso
        h = 0.02

        # faixa tracejada no centro do trajeto do caminhão
        x = -15.5
        while x < 15.5:
            self.peca(BoxGeometry(1.2, h, 0.15), [x + 0.6, y, 0], self.matFaixaBranca)
            x += 2.2

        # bordas laterais do trajeto
        for z in [2.4, -2.4]:
            self.peca(BoxGeometry(self.LARGURA - 1.0, h, 0.12), [0, y, z], self.matFaixaBranca)

        # área de estacionamento: retângulo amarelo onde o caminhão para
        x0, x1 = xEstacionamento - 3.95, xEstacionamento + 3.95
        cx = (x0 + x1) / 2
        for z in [1.55, -1.55]:
            self.peca(BoxGeometry(x1 - x0, h + 0.002, 0.18), [cx, y + 0.001, z], self.matFaixaAmarela)
        self.peca(BoxGeometry(0.18, h + 0.002, 3.28), [x1, y + 0.001, 0], self.matFaixaAmarela)
        # linha de parada (texturizada com listras)
        self.peca(BoxGeometry(0.5, h + 0.004, 3.3), [x1 + 0.4, y + 0.002, 0], self.matAtendimento)

        # área de atendimento: atrás do caminhão estacionado
        ax0, ax1 = xEstacionamento - 7.4, x0 - 0.1
        acx = (ax0 + ax1) / 2
        self.peca(BoxGeometry(ax1 - ax0, h, 3.1), [acx, y - 0.004, 0], self.matAreaAtendimento)
        for z in [1.65, -1.65]:
            self.peca(BoxGeometry(ax1 - ax0, h + 0.004, 0.3), [acx, y + 0.002, z], self.matAtendimento)

        # base do robô (disco) e trajeto até a área de atendimento
        bx, bz = posicaoBaseRobo
        self.peca(CylinderGeometry(radius=1.0, height=h, radialSegments=40, heightSegments=1), [bx, y, bz], self.matBaseRobo)
        self.peca(CylinderGeometry(radius=0.75, height=h + 0.004, radialSegments=40, heightSegments=1),
                  [bx, y + 0.002, bz], self.matPiso)
        z = bz - 1.4
        while z > 2.0:
            self.peca(BoxGeometry(0.15, h, 0.5), [bx, y, z], self.matBaseRobo)
            z -= 0.9

    def construirDecoracao(self, posicaoMesa):
        meiaL = self.LARGURA / 2 - 0.6
        meiaP = self.PROFUNDIDADE / 2 - 0.6

        # pilares nos quatro cantos
        for px in [-meiaL, meiaL]:
            for pz in [-meiaP, meiaP]:
                self.peca(CylinderGeometry(radius=0.35, height=4.0, radialSegments=24, heightSegments=1),
                          [px, 2.0, pz], self.matPilar)
                self.peca(CylinderGeometry(radius=0.42, height=0.25, radialSegments=24, heightSegments=1),
                          [px, 4.1, pz], self.matTopoPilar)

        # painel baixo ao fundo (identidade industrial)
        self.peca(BoxGeometry(self.LARGURA - 3.0, 2.2, 0.25), [0, 1.1, -meiaP - 0.1], self.matPainel)
        self.peca(BoxGeometry(self.LARGURA - 3.0, 0.15, 0.3), [0, 2.25, -meiaP - 0.1], self.matTopoPilar)

        # mesa de recebimento ao lado da base do robô (topo em y = 0,73)
        mx, mz = posicaoMesa
        self.peca(BoxGeometry(1.0, 0.08, 1.4), [mx, 0.69, mz], self.matMesa)
        for dx in [-0.42, 0.42]:
            for dz in [-0.62, 0.62]:
                self.peca(BoxGeometry(0.08, 0.65, 0.08), [mx + dx, 0.325, mz + dz], self.matMesa)

        # palete com pilha de caixas entregues anteriormente.
        # As caixas partem de um cubo unitário, dimensionado por ESCALA
        # (matriz = translação @ escala).
        self.peca(BoxGeometry(2.0, 0.18, 1.6), [mx - 0.5, 0.09, mz + 2.1], self.matPalete)
        for (dx, dy, dz, s) in [(-1.0, 0.18, -0.35, 0.8), (-0.05, 0.18, -0.35, 0.8),
                                (-0.55, 0.18, 0.4, 0.7), (-0.5, 0.98, -0.3, 0.65)]:
            matriz = Matrix.makeTranslation(mx + dx, dy + s / 2, mz + 2.1 + dz) @ Matrix.makeScale(s)
            self.peca(BoxGeometry(1, 1, 1), None, self.matCaixa, matriz)

        # pilha de caixas no fundo, perto do painel
        for (x, y, z, s) in [(-11, 0, -7.2, 1.0), (-9.9, 0, -7.4, 0.9), (-10.5, 1.0, -7.3, 0.8),
                             (9.5, 0, -7.3, 1.1)]:
            matriz = Matrix.makeTranslation(x, y + s / 2, z) @ Matrix.makeScale(s)
            self.peca(BoxGeometry(1, 1, 1), None, self.matCaixa, matriz)

    def construirSemaforo(self, xEstacionamento):
        # sinal ao lado da vaga: verde = livre, amarelo = aproximação, vermelho = atendimento
        sx, sz = xEstacionamento + 4.8, -3.0
        self.peca(CylinderGeometry(radius=0.09, height=3.0, radialSegments=12, heightSegments=1),
                  [sx, 1.5, sz], self.matPilar)
        self.peca(BoxGeometry(0.4, 0.6, 0.4), [sx, 3.2, sz], self.matPilar)
        # a lâmpada é uma malha separada: sua cor muda durante a animação
        lampada = Mesh(SphereGeometry(radius=0.16, radiusSegments=16, heightSegments=10), self.matLampada)
        lampada.setPosition([sx - 0.15, 3.2, sz + 0.15])
        lampada.castShadow = False
        self.add(lampada)

    def setCorSinal(self, cor):
        self.matLampada.uniforms["baseColor"].data = cor
