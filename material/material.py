from OpenGL.GL import *

from core.openGLUtils import OpenGLUtils
from core.uniform import Uniform


# Classe base dos materiais: programa de GPU + uniforms + configurações de desenho
class Material(object):

    def __init__(self, vertexShaderCode, fragmentShaderCode):
        self.programRef = OpenGLUtils.initializeProgram(vertexShaderCode, fragmentShaderCode)

        # uniforms comuns a todos os materiais (preenchidos pelo Renderer)
        self.uniforms = {}
        self.uniforms["modelMatrix"] = Uniform("mat4", None)
        self.uniforms["viewMatrix"] = Uniform("mat4", None)
        self.uniforms["projectionMatrix"] = Uniform("mat4", None)

        # configurações de renderização (OpenGL)
        self.settings = {}
        self.settings["drawStyle"] = GL_TRIANGLES

    def addUniform(self, dataType, variableName, data):
        self.uniforms[variableName] = Uniform(dataType, data)

    # obtém a localização de todas as variáveis uniform no programa
    def locateUniforms(self):
        for variableName, uniformObject in self.uniforms.items():
            uniformObject.locateVariable(self.programRef, variableName)

    # implementado pelas classes filhas
    def updateRenderSettings(self):
        pass

    # altera uniforms ou configurações a partir de um dicionário
    def setProperties(self, properties):
        for name, data in properties.items():
            if name in self.uniforms.keys():
                self.uniforms[name].data = data
            elif name in self.settings.keys():
                self.settings[name] = data
            else:
                raise Exception("Material has no property named: " + name)
