from math import sin, cos, pi

from geometry.geometry import Geometry


# Polígono regular no plano XY, formado por triângulos que partem do centro
class PolygonGeometry(Geometry):

    def __init__(self, sides=3, radius=1):
        super().__init__()

        A = 2 * pi / sides
        positionData = []
        uvData = []
        normalData = []
        normal = [0, 0, 1]

        for n in range(sides):
            positionData.append([0, 0, 0])
            positionData.append([radius * cos(n * A), radius * sin(n * A), 0])
            positionData.append([radius * cos((n + 1) * A), radius * sin((n + 1) * A), 0])

            uvData.append([0.5, 0.5])
            uvData.append([cos(n * A) * 0.5 + 0.5, sin(n * A) * 0.5 + 0.5])
            uvData.append([cos((n + 1) * A) * 0.5 + 0.5, sin((n + 1) * A) * 0.5 + 0.5])

            normalData += [normal, normal, normal]

        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec2", "vertexUV", uvData)
        self.addAttribute("vec3", "vertexNormal", normalData)
        self.addAttribute("vec3", "faceNormal", normalData)
        self.countVertices()
