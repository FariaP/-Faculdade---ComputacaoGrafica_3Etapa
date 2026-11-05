from OpenGL.GL import *


# Funções estáticas para compilar shaders e ligar programas de GPU
class OpenGLUtils(object):

    @staticmethod
    def initializeShader(shaderCode, shaderType):
        # especifica a versão do GLSL utilizada
        shaderCode = "#version 330\n" + shaderCode

        # cria um objeto shader vazio e devolve sua referência
        shaderRef = glCreateShader(shaderType)
        glShaderSource(shaderRef, shaderCode)
        glCompileShader(shaderRef)

        # verifica se a compilação foi bem-sucedida
        compileSuccess = glGetShaderiv(shaderRef, GL_COMPILE_STATUS)
        if not compileSuccess:
            errorMessage = glGetShaderInfoLog(shaderRef)
            glDeleteShader(shaderRef)
            errorMessage = "\n" + errorMessage.decode("utf-8")
            raise Exception(errorMessage)

        return shaderRef

    @staticmethod
    def initializeProgram(vertexShaderCode, fragmentShaderCode):
        vertexShaderRef = OpenGLUtils.initializeShader(vertexShaderCode, GL_VERTEX_SHADER)
        fragmentShaderRef = OpenGLUtils.initializeShader(fragmentShaderCode, GL_FRAGMENT_SHADER)

        programRef = glCreateProgram()
        glAttachShader(programRef, vertexShaderRef)
        glAttachShader(programRef, fragmentShaderRef)

        # fixa o atributo de posição na location 0 em todos os programas;
        # assim o VAO de cada malha também funciona com o DepthMaterial
        # durante a passada de sombra (Shadow Mapping)
        glBindAttribLocation(programRef, 0, "vertexPosition")

        glLinkProgram(programRef)

        linkSuccess = glGetProgramiv(programRef, GL_LINK_STATUS)
        if not linkSuccess:
            errorMessage = glGetProgramInfoLog(programRef)
            glDeleteProgram(programRef)
            errorMessage = "\n" + errorMessage.decode("utf-8")
            raise Exception(errorMessage)

        return programRef
