import numpy

from core.matrix import Matrix


# Nó do grafo de cena: possui uma transformação local, um pai e filhos
class Object3D(object):

    def __init__(self):
        # matriz de transformação local (relativa ao pai)
        self.transform = Matrix.makeIdentity()
        self.parent = None
        self.children = []

    def add(self, child):
        self.children.append(child)
        child.parent = self

    def remove(self, child):
        self.children.remove(child)
        child.parent = None

    # matriz de mundo = matriz do pai (acumulada) @ matriz local
    def getWorldMatrix(self):
        if self.parent is None:
            return self.transform
        else:
            return self.parent.getWorldMatrix() @ self.transform

    # lista com este nó e todos os seus descendentes
    def getDescendantList(self):
        descendants = []
        nodesToProcess = [self]
        while len(nodesToProcess) > 0:
            node = nodesToProcess.pop(0)
            descendants.append(node)
            nodesToProcess = node.children + nodesToProcess
        return descendants

    # aplica uma transformação local (à direita) ou global (à esquerda)
    def applyMatrix(self, matrix, localCoord=True):
        if localCoord:
            self.transform = self.transform @ matrix
        else:
            self.transform = matrix @ self.transform

    def translate(self, x, y, z, localCoord=True):
        m = Matrix.makeTranslation(x, y, z)
        self.applyMatrix(m, localCoord)

    def rotateX(self, angle, localCoord=True):
        m = Matrix.makeRotationX(angle)
        self.applyMatrix(m, localCoord)

    def rotateY(self, angle, localCoord=True):
        m = Matrix.makeRotationY(angle)
        self.applyMatrix(m, localCoord)

    def rotateZ(self, angle, localCoord=True):
        m = Matrix.makeRotationZ(angle)
        self.applyMatrix(m, localCoord)

    def scale(self, s, localCoord=True):
        m = Matrix.makeScale(s)
        self.applyMatrix(m, localCoord)

    # posição relativa ao pai (coluna de translação da matriz local)
    def getPosition(self):
        return [self.transform[0, 3],
                self.transform[1, 3],
                self.transform[2, 3]]

    # posição no mundo (coluna de translação da matriz de mundo)
    def getWorldPosition(self):
        worldTransform = self.getWorldMatrix()
        return [worldTransform[0, 3],
                worldTransform[1, 3],
                worldTransform[2, 3]]

    def setPosition(self, position):
        self.transform[0, 3] = position[0]
        self.transform[1, 3] = position[1]
        self.transform[2, 3] = position[2]

    def lookAt(self, targetPosition):
        self.transform = Matrix.makeLookAt(self.getWorldPosition(), targetPosition)

    # parte 3x3 de rotação da matriz local
    def getRotationMatrix(self):
        return numpy.array([self.transform[0][0:3],
                            self.transform[1][0:3],
                            self.transform[2][0:3]])

    # direção para a qual o objeto aponta (eixo local -Z)
    def getDirection(self):
        forward = numpy.array([0, 0, -1])
        return list(self.getRotationMatrix() @ forward)

    # orienta o objeto para apontar na direção informada
    def setDirection(self, direction):
        position = self.getPosition()
        targetPosition = [position[0] + direction[0],
                          position[1] + direction[1],
                          position[2] + direction[2]]
        self.lookAt(targetPosition)
