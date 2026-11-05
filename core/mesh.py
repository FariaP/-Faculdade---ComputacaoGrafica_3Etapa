from OpenGL.GL import *

from core.object3D import Object3D


# Objeto visível: combina uma geometria (vértices) com um material (shaders)
class Mesh(Object3D):

    def __init__(self, geometry, material):
        super().__init__()
        self.geometry = geometry
        self.material = material

        # permite ocultar o objeto sem removê-lo da cena
        self.visible = True

        # indica se a malha é desenhada no mapa de sombras (projeta sombra)
        self.castShadow = True

        # VAO: guarda as associações entre buffers e atributos do shader
        self.vaoRef = glGenVertexArrays(1)
        glBindVertexArray(self.vaoRef)
        for variableName, attributeObject in geometry.attributes.items():
            attributeObject.associateVariable(material.programRef, variableName)
        # desvincula o VAO
        glBindVertexArray(0)
