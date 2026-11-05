from core.object3D import Object3D


# Classe base com os atributos comuns a todos os tipos de luz
class Light(Object3D):

    AMBIENT = 1
    DIRECTIONAL = 2
    POINT = 3

    def __init__(self, lightType=0):
        super().__init__()
        # identifica o tipo de luz (0 = luz vazia, não contribui)
        self.lightType = lightType
        # cor RGB da luz
        self.color = [1, 1, 1]
        # coeficientes de atenuação (constante, linear, quadrático)
        self.attenuation = [1, 0, 0]
