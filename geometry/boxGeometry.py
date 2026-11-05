from geometry.geometry import Geometry


# Caixa (paralelepípedo) centrada na origem.
# Cada face repete sua normal nos 6 vértices dos seus 2 triângulos,
# preservando as arestas bem definidas.
class BoxGeometry(Geometry):

    def __init__(self, width=1, height=1, depth=1):
        super().__init__()

        w, h, d = width / 2, height / 2, depth / 2

        # os 8 cantos da caixa
        P0 = [-w, -h, -d]
        P1 = [w, -h, -d]
        P2 = [-w, h, -d]
        P3 = [w, h, -d]
        P4 = [-w, -h, d]
        P5 = [w, -h, d]
        P6 = [-w, h, d]
        P7 = [w, h, d]

        # 6 faces x 2 triângulos x 3 vértices (sentido anti-horário visto de fora)
        positionData = [P5, P1, P3, P5, P3, P7,    # direita  (+X)
                        P0, P4, P6, P0, P6, P2,    # esquerda (-X)
                        P6, P7, P3, P6, P3, P2,    # cima     (+Y)
                        P0, P1, P5, P0, P5, P4,    # baixo    (-Y)
                        P4, P5, P7, P4, P7, P6,    # frente   (+Z)
                        P1, P0, P2, P1, P2, P3]    # trás     (-Z)

        # coordenadas de textura: cada face recebe a imagem inteira
        T0, T1, T2, T3 = [0, 0], [1, 0], [0, 1], [1, 1]
        uvData = [T0, T1, T3, T0, T3, T2] * 6

        # normais das faces
        right = [1, 0, 0]
        left = [-1, 0, 0]
        top = [0, 1, 0]
        bottom = [0, -1, 0]
        front = [0, 0, 1]
        back = [0, 0, -1]
        normalData = ([right] * 6 + [left] * 6 + [top] * 6 +
                      [bottom] * 6 + [front] * 6 + [back] * 6)

        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec2", "vertexUV", uvData)
        self.addAttribute("vec3", "vertexNormal", normalData)
        self.addAttribute("vec3", "faceNormal", normalData)
        self.countVertices()
