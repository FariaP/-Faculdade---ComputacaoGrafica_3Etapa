import pygame
from OpenGL.GL import *

from core.mesh import Mesh
from light.light import Light
from light.shadow import Shadow


# Percorre o grafo de cena e desenha cada malha
class Renderer(object):

    def __init__(self, clearColor=[0, 0, 0]):
        glEnable(GL_DEPTH_TEST)
        # antisserrilhamento
        glEnable(GL_MULTISAMPLE)

        self.clearColor = clearColor
        glClearColor(clearColor[0], clearColor[1], clearColor[2], 1)

        self.windowSize = pygame.display.get_surface().get_size()

        # sombras desligadas até que enableShadows seja chamado
        self.shadowsEnabled = False

    def render(self, scene, camera, clearColor=True, clearDepth=True, renderTarget=None):
        # filtra as malhas presentes no grafo de cena
        descendantList = scene.getDescendantList()
        meshFilter = lambda x: isinstance(x, Mesh)
        meshList = list(filter(meshFilter, descendantList))

        # ------------------------------------------------------------
        # 1ª passada (Shadow Mapping): renderiza a cena do ponto de vista
        # da luz, gravando a profundidade de cada fragmento na textura
        # ------------------------------------------------------------
        if self.shadowsEnabled:
            glBindFramebuffer(GL_FRAMEBUFFER, self.shadowObject.renderTarget.framebufferRef)
            glViewport(0, 0, self.shadowObject.renderTarget.width,
                       self.shadowObject.renderTarget.height)
            # branco = profundidade máxima (nenhum objeto)
            glClearColor(1, 1, 1, 1)
            glClear(GL_COLOR_BUFFER_BIT)
            glClear(GL_DEPTH_BUFFER_BIT)
            glDisable(GL_BLEND)

            glUseProgram(self.shadowObject.material.programRef)
            self.shadowObject.updateInternal()
            # matrizes de visão e projeção da luz: iguais para todas as malhas
            self.shadowObject.material.uniforms["viewMatrix"].uploadData()
            self.shadowObject.material.uniforms["projectionMatrix"].uploadData()

            for mesh in meshList:
                if not mesh.visible:
                    continue
                # apenas triângulos projetam sombra
                if mesh.material.settings["drawStyle"] != GL_TRIANGLES:
                    continue
                # objetos marcados para não projetar sombra
                if not mesh.castShadow:
                    continue

                # vertexPosition está na location 0 em todos os programas,
                # portanto o VAO da malha pode ser reutilizado aqui
                glBindVertexArray(mesh.vaoRef)
                self.shadowObject.material.uniforms["modelMatrix"].data = mesh.getWorldMatrix()
                self.shadowObject.material.uniforms["modelMatrix"].uploadData()
                glDrawArrays(GL_TRIANGLES, 0, mesh.geometry.vertexCount)

            # restaura a cor de fundo da cena
            glClearColor(self.clearColor[0], self.clearColor[1], self.clearColor[2], 1)

        # ------------------------------------------------------------
        # 2ª passada: renderização normal, a partir da câmera
        # ------------------------------------------------------------
        if renderTarget is None:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glViewport(0, 0, self.windowSize[0], self.windowSize[1])
        else:
            glBindFramebuffer(GL_FRAMEBUFFER, renderTarget.framebufferRef)
            glViewport(0, 0, renderTarget.width, renderTarget.height)

        if clearColor:
            glClear(GL_COLOR_BUFFER_BIT)
        if clearDepth:
            glClear(GL_DEPTH_BUFFER_BIT)

        # transparência
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        camera.updateViewMatrix()

        # as luzes também fazem parte do grafo de cena;
        # os shaders aceitam até 4 luzes (light0 ... light3)
        lightFilter = lambda x: isinstance(x, Light)
        lightList = list(filter(lightFilter, descendantList))
        while len(lightList) < 4:
            lightList.append(Light())

        # materiais cujos uniforms já foram enviados neste quadro.
        # Os valores de uniforms ficam guardados no programa de GPU; por isso,
        # quando várias malhas compartilham o mesmo material, basta enviar
        # uma vez os dados comuns (câmera, luzes, sombra, cor) e, para cada
        # malha, apenas a matriz de modelo e a textura.
        preparedMaterials = set()

        for mesh in meshList:
            if not mesh.visible:
                continue

            glUseProgram(mesh.material.programRef)
            glBindVertexArray(mesh.vaoRef)

            # matriz de modelo: própria de cada malha
            mesh.material.uniforms["modelMatrix"].data = mesh.getWorldMatrix()

            if id(mesh.material) in preparedMaterials:
                mesh.material.uniforms["modelMatrix"].uploadData()
                # a associação textura/unidade é um estado global do OpenGL
                # e pode ter sido alterada por outro material
                for variableName, uniformObject in mesh.material.uniforms.items():
                    if uniformObject.dataType == "sampler2D":
                        uniformObject.uploadData()
                mesh.material.updateRenderSettings()
                glDrawArrays(mesh.material.settings["drawStyle"], 0, mesh.geometry.vertexCount)
                continue
            preparedMaterials.add(id(mesh.material))

            # matrizes de visão e projeção
            mesh.material.uniforms["viewMatrix"].data = camera.viewMatrix
            mesh.material.uniforms["projectionMatrix"].data = camera.projectionMatrix

            # materiais com iluminação recebem os dados das luzes
            if "light0" in mesh.material.uniforms.keys():
                for lightNumber in range(4):
                    lightName = "light" + str(lightNumber)
                    lightObject = lightList[lightNumber]
                    mesh.material.uniforms[lightName].data = lightObject

            # posição da câmera (componente especular de Phong)
            if "viewPosition" in mesh.material.uniforms.keys():
                mesh.material.uniforms["viewPosition"].data = camera.getWorldPosition()

            # dados do mapa de sombras
            if self.shadowsEnabled and "shadow0" in mesh.material.uniforms.keys():
                mesh.material.uniforms["shadow0"].data = self.shadowObject

            for variableName, uniformObject in mesh.material.uniforms.items():
                uniformObject.uploadData()

            mesh.material.updateRenderSettings()

            glDrawArrays(mesh.material.settings["drawStyle"], 0, mesh.geometry.vertexCount)

    # ativa o Shadow Mapping para uma luz direcional
    def enableShadows(self, shadowLight, strength=0.5, resolution=[512, 512],
                      cameraBounds=[-5, 5, -5, 5, 0, 20], bias=0.01):
        self.shadowsEnabled = True
        self.shadowObject = Shadow(shadowLight, strength=strength, resolution=resolution,
                                   cameraBounds=cameraBounds, bias=bias)
