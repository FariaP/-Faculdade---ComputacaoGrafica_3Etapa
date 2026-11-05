import numpy
from OpenGL.GL import *


# Armazena dados de vértices em um buffer da GPU (VBO)
class Attribute(object):

    def __init__(self, dataType, data):
        # tipo: int | float | vec2 | vec3 | vec4
        self.dataType = dataType
        # lista com os dados de cada vértice
        self.data = data
        # referência do buffer na GPU
        self.bufferRef = glGenBuffers(1)
        self.uploadData()

    # envia os dados para a GPU
    def uploadData(self):
        data = numpy.array(self.data).astype(numpy.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.bufferRef)
        glBufferData(GL_ARRAY_BUFFER, data.ravel(), GL_STATIC_DRAW)

    # associa o buffer a uma variável "in" do vertex shader
    def associateVariable(self, programRef, variableName):
        variableRef = glGetAttribLocation(programRef, variableName)

        # a variável não existe (ou não é usada) no programa
        if variableRef == -1:
            return

        glBindBuffer(GL_ARRAY_BUFFER, self.bufferRef)

        if self.dataType == "int":
            glVertexAttribPointer(variableRef, 1, GL_INT, False, 0, None)
        elif self.dataType == "float":
            glVertexAttribPointer(variableRef, 1, GL_FLOAT, False, 0, None)
        elif self.dataType == "vec2":
            glVertexAttribPointer(variableRef, 2, GL_FLOAT, False, 0, None)
        elif self.dataType == "vec3":
            glVertexAttribPointer(variableRef, 3, GL_FLOAT, False, 0, None)
        elif self.dataType == "vec4":
            glVertexAttribPointer(variableRef, 4, GL_FLOAT, False, 0, None)
        else:
            raise Exception("Attribute " + variableName + " has unknown type " + self.dataType)

        glEnableVertexAttribArray(variableRef)
