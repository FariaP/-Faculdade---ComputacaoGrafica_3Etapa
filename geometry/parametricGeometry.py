import numpy

from geometry.geometry import Geometry


# Superfície definida por uma função S(u, v) -> (x, y, z).
# As normais de vértice são obtidas pelo produto vetorial de duas
# direções tangentes à superfície (n = u x v).
class ParametricGeometry(Geometry):

    def __init__(self, uStart, uEnd, uResolution, vStart, vEnd, vResolution, surfaceFunction):
        super().__init__()

        deltaU = (uEnd - uStart) / uResolution
        deltaV = (vEnd - vStart) / vResolution

        # normal de um triângulo a partir de três pontos
        def calcNormal(P0, P1, P2):
            v1 = numpy.array(P1) - numpy.array(P0)
            v2 = numpy.array(P2) - numpy.array(P0)
            normal = numpy.cross(v1, v2)
            length = numpy.linalg.norm(normal)
            if length < 1e-12:
                return None
            return normal / length

        # normal no ponto (u, v) por diferenças finitas
        def vertexNormal(u, v):
            h = 0.0001
            # nos polos (ex.: topo da esfera) a superfície degenera;
            # nesse caso a normal é calculada em um ponto vizinho
            for dv in [0, -h * 10, h * 10]:
                P0 = surfaceFunction(u, v + dv)
                P1 = surfaceFunction(u + h, v + dv)
                P2 = surfaceFunction(u, v + dv + h)
                normal = calcNormal(P0, P1, P2)
                if normal is not None:
                    return list(normal)
            return [0, 1, 0]

        positions = []
        uvs = []
        vertexNormals = []
        for uIndex in range(uResolution + 1):
            vArray = []
            uvArray = []
            nArray = []
            for vIndex in range(vResolution + 1):
                u = uStart + uIndex * deltaU
                v = vStart + vIndex * deltaV
                vArray.append(surfaceFunction(u, v))
                uvArray.append([uIndex / uResolution, vIndex / vResolution])
                nArray.append(vertexNormal(u, v))
            positions.append(vArray)
            uvs.append(uvArray)
            vertexNormals.append(nArray)

        positionData = []
        uvData = []
        vertexNormalData = []
        faceNormalData = []

        # cada quadrilátero da grade vira dois triângulos
        for xIndex in range(uResolution):
            for yIndex in range(vResolution):
                pA = positions[xIndex + 0][yIndex + 0]
                pB = positions[xIndex + 1][yIndex + 0]
                pD = positions[xIndex + 0][yIndex + 1]
                pC = positions[xIndex + 1][yIndex + 1]
                positionData += [pA.copy(), pB.copy(), pC.copy(), pA.copy(), pC.copy(), pD.copy()]

                uvA = uvs[xIndex + 0][yIndex + 0]
                uvB = uvs[xIndex + 1][yIndex + 0]
                uvD = uvs[xIndex + 0][yIndex + 1]
                uvC = uvs[xIndex + 1][yIndex + 1]
                uvData += [uvA, uvB, uvC, uvA, uvC, uvD]

                nA = vertexNormals[xIndex + 0][yIndex + 0]
                nB = vertexNormals[xIndex + 1][yIndex + 0]
                nD = vertexNormals[xIndex + 0][yIndex + 1]
                nC = vertexNormals[xIndex + 1][yIndex + 1]
                vertexNormalData += [nA, nB, nC, nA, nC, nD]

                fn0 = calcNormal(pA, pB, pC)
                fn1 = calcNormal(pA, pC, pD)
                # triângulos degenerados (polos) usam a normal de vértice
                fn0 = list(fn0) if fn0 is not None else nC
                fn1 = list(fn1) if fn1 is not None else nC
                faceNormalData += [fn0, fn0, fn0, fn1, fn1, fn1]

        self.addAttribute("vec3", "vertexPosition", positionData)
        self.addAttribute("vec2", "vertexUV", uvData)
        self.addAttribute("vec3", "vertexNormal", vertexNormalData)
        self.addAttribute("vec3", "faceNormal", faceNormalData)
        self.countVertices()
