from core.group import Group
from core.matrix import Matrix


# Pivô de uma articulação (ombro, cotovelo, roda, dobradiça da tampa...).
#
# Uma caixa gira em torno do próprio centro. Para que uma peça gire em torno
# da junta, o pivô (um Group vazio) é colocado NA JUNTA e a peça é adicionada
# a ele deslocada. A matriz local do pivô é recalculada a cada mudança:
#
#     transform = T(posição da junta) @ R(eixo, ângulo)
#
# Assim, os filhos giram em torno da junta e continuam acompanhando o pai.
class Articulacao(Group):

    def __init__(self, posicao=[0, 0, 0], eixo="z", angulo=0.0):
        super().__init__()
        self.posicao = list(posicao)
        self.eixo = eixo
        self.angulo = angulo
        self.atualizarTransformacao()

    def atualizarTransformacao(self):
        if self.eixo == "x":
            rotacao = Matrix.makeRotationX(self.angulo)
        elif self.eixo == "y":
            rotacao = Matrix.makeRotationY(self.angulo)
        else:
            rotacao = Matrix.makeRotationZ(self.angulo)
        self.transform = Matrix.makeTranslation(*self.posicao) @ rotacao

    # define o ângulo absoluto (radianos)
    def setAngulo(self, angulo):
        self.angulo = angulo
        self.atualizarTransformacao()

    # soma um incremento ao ângulo atual (radianos)
    def girar(self, incremento):
        self.setAngulo(self.angulo + incremento)
