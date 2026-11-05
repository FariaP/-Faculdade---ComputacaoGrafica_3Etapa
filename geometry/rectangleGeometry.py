from geometry.geometry import Geometry


# Retângulo no plano XY, formado por dois triângulos; normal (0, 0, 1)
class RectangleGeometry(Geometry):

    def __init__(self, width=1, height=1, position=[0, 0], alignment=[0.5, 0.5]):
        super().__init__()

        x, y = position
        a, b = alignment
        P0 = [x + (-a) * width,    y + (-b) * height,    0]
        P1 = [x + (1 - a) * width, y + (-b) * height,    0]
        P2 = [x + (-a) * width,    y + (1 - b) * height, 0]
        P3 = [x + (1 - a) * width, y + (1 - b) * height, 0]

        T0, T1, T2, T3 = [0, 0], [1, 0], [0, 1], [1, 1]

        positionData = [P0, P1, P3, P0, P3, P2]
        uvData = [T0, T1, T3, T0, T3, T2]

        # todos os vértices compartilham a mesma normal (superfície plana)
        normal = [0, 0, 1]
        normalData = [normal] * 6

        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec2", "vertexUV", uvData)
        self.addAttribute("vec3", "vertexNormal", normalData)
        self.addAttribute("vec3", "faceNormal", normalData)
        self.countVertices()
