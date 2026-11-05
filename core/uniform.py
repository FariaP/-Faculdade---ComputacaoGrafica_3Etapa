from OpenGL.GL import *


# Armazena um valor "uniform" (constante para todos os vértices de um desenho)
# e o envia para o programa de GPU
class Uniform(object):

    def __init__(self, dataType, data):
        # tipo: int | bool | float | vec2 | vec3 | vec4 | mat4 | sampler2D | Light | Shadow
        self.dataType = dataType
        self.data = data
        # referência (localização) da variável no programa
        self.variableRef = None

    # obtém a referência da variável uniform no programa
    def locateVariable(self, programRef, variableName):
        if self.dataType == "Light":
            # struct Light { lightType, color, direction, position, attenuation }
            self.variableRef = {}
            self.variableRef["lightType"] = glGetUniformLocation(programRef, variableName + ".lightType")
            self.variableRef["color"] = glGetUniformLocation(programRef, variableName + ".color")
            self.variableRef["direction"] = glGetUniformLocation(programRef, variableName + ".direction")
            self.variableRef["position"] = glGetUniformLocation(programRef, variableName + ".position")
            self.variableRef["attenuation"] = glGetUniformLocation(programRef, variableName + ".attenuation")
        elif self.dataType == "Shadow":
            # struct Shadow { lightDirection, projectionMatrix, viewMatrix,
            #                 depthTextureSampler, strength, bias }
            self.variableRef = {}
            self.variableRef["lightDirection"] = glGetUniformLocation(programRef, variableName + ".lightDirection")
            self.variableRef["projectionMatrix"] = glGetUniformLocation(programRef, variableName + ".projectionMatrix")
            self.variableRef["viewMatrix"] = glGetUniformLocation(programRef, variableName + ".viewMatrix")
            self.variableRef["depthTextureSampler"] = glGetUniformLocation(programRef, variableName + ".depthTextureSampler")
            self.variableRef["strength"] = glGetUniformLocation(programRef, variableName + ".strength")
            self.variableRef["bias"] = glGetUniformLocation(programRef, variableName + ".bias")
        else:
            self.variableRef = glGetUniformLocation(programRef, variableName)

    # envia o valor armazenado para a variável no programa em uso
    def uploadData(self):
        # a variável não existe no programa, ou ainda não recebeu valor
        if self.variableRef == -1 or self.data is None:
            return

        if self.dataType == "int":
            glUniform1i(self.variableRef, self.data)
        elif self.dataType == "bool":
            glUniform1i(self.variableRef, self.data)
        elif self.dataType == "float":
            glUniform1f(self.variableRef, self.data)
        elif self.dataType == "vec2":
            glUniform2f(self.variableRef, self.data[0], self.data[1])
        elif self.dataType == "vec3":
            glUniform3f(self.variableRef, self.data[0], self.data[1], self.data[2])
        elif self.dataType == "vec4":
            glUniform4f(self.variableRef, self.data[0], self.data[1], self.data[2], self.data[3])
        elif self.dataType == "mat4":
            # GL_TRUE: as matrizes numpy são armazenadas por linha
            glUniformMatrix4fv(self.variableRef, 1, GL_TRUE, self.data)
        elif self.dataType == "sampler2D":
            textureObjectRef, textureUnitRef = self.data
            # ativa a unidade de textura e associa o objeto de textura a ela
            glActiveTexture(GL_TEXTURE0 + textureUnitRef)
            glBindTexture(GL_TEXTURE_2D, textureObjectRef)
            # o sampler do shader lê da unidade informada
            glUniform1i(self.variableRef, textureUnitRef)
        elif self.dataType == "Light":
            glUniform1i(self.variableRef["lightType"], self.data.lightType)
            glUniform3f(self.variableRef["color"],
                        self.data.color[0], self.data.color[1], self.data.color[2])
            direction = self.data.getDirection()
            glUniform3f(self.variableRef["direction"], direction[0], direction[1], direction[2])
            position = self.data.getPosition()
            glUniform3f(self.variableRef["position"], position[0], position[1], position[2])
            glUniform3f(self.variableRef["attenuation"],
                        self.data.attenuation[0], self.data.attenuation[1], self.data.attenuation[2])
        elif self.dataType == "Shadow":
            direction = self.data.lightSource.getDirection()
            glUniform3f(self.variableRef["lightDirection"], direction[0], direction[1], direction[2])
            glUniformMatrix4fv(self.variableRef["projectionMatrix"], 1, GL_TRUE,
                               self.data.camera.projectionMatrix)
            glUniformMatrix4fv(self.variableRef["viewMatrix"], 1, GL_TRUE,
                               self.data.camera.viewMatrix)
            # o mapa de profundidade usa uma unidade de textura reservada (15)
            textureObjectRef = self.data.renderTarget.texture.textureRef
            textureUnitRef = 15
            glActiveTexture(GL_TEXTURE0 + textureUnitRef)
            glBindTexture(GL_TEXTURE_2D, textureObjectRef)
            glUniform1i(self.variableRef["depthTextureSampler"], textureUnitRef)
            glUniform1f(self.variableRef["strength"], self.data.strength)
            glUniform1f(self.variableRef["bias"], self.data.bias)
        else:
            raise Exception("Unknown Uniform data type: " + self.dataType)
