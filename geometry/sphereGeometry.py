from math import sin, cos, pi

from geometry.parametricGeometry import ParametricGeometry


# Elipsoide definido parametricamente (u: longitude, v: latitude)
class EllipsoidGeometry(ParametricGeometry):

    def __init__(self, width=1, height=1, depth=1, radiusSegments=32, heightSegments=16):

        def S(u, v):
            return [width / 2 * sin(u) * cos(v),
                    height / 2 * sin(v),
                    depth / 2 * cos(u) * cos(v)]

        super().__init__(0, 2 * pi, radiusSegments, -pi / 2, pi / 2, heightSegments, S)


# Esfera: elipsoide com as três dimensões iguais
class SphereGeometry(EllipsoidGeometry):

    def __init__(self, radius=1, radiusSegments=32, heightSegments=16):
        super().__init__(2 * radius, 2 * radius, 2 * radius, radiusSegments, heightSegments)
