import numpy

from core.attribute import Attribute


# Conjunto de atributos de vértice (posição, coordenadas UV, normais...)
class Geometry(object):

    def __init__(self):
        # dicionário: nome da variável no shader -> Attribute
        self.attributes = {}
        # quantidade de vértices
        self.vertexCount = None

    def addAttribute(self, dataType, variableName, data):
        self.attributes[variableName] = Attribute(dataType, data)

    def countVertices(self):
        # o número de vértices é o tamanho da lista de qualquer atributo
        attrib = list(self.attributes.values())[0]
        self.vertexCount = len(attrib.data)

    # transforma os vértices da própria geometria (útil para alinhar primitivas);
    # as normais recebem apenas a parte de rotação da matriz
    def applyMatrix(self, matrix, variableName="vertexPosition"):
        oldPositionData = self.attributes[variableName].data
        newPositionData = []
        for oldPos in oldPositionData:
            newPos = list(oldPos) + [1]
            newPos = matrix @ newPos
            newPositionData.append(list(newPos[0:3]))
        self.attributes[variableName].data = newPositionData
        self.attributes[variableName].uploadData()

        rotationMatrix = numpy.array([matrix[0][0:3],
                                      matrix[1][0:3],
                                      matrix[2][0:3]])

        for normalName in ["vertexNormal", "faceNormal"]:
            if normalName in self.attributes.keys():
                oldNormalData = self.attributes[normalName].data
                newNormalData = []
                for oldNormal in oldNormalData:
                    newNormal = rotationMatrix @ numpy.array(oldNormal)
                    newNormal = newNormal / numpy.linalg.norm(newNormal)
                    newNormalData.append(list(newNormal))
                self.attributes[normalName].data = newNormalData
                self.attributes[normalName].uploadData()

    # junta os vértices de outra geometria a esta (mesmos atributos)
    def merge(self, otherGeometry):
        for variableName, attributeObject in self.attributes.items():
            attributeObject.data += otherGeometry.attributes[variableName].data
            attributeObject.uploadData()
        self.countVertices()
