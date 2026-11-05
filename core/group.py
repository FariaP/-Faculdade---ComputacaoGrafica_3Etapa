from core.object3D import Object3D


# Nó sem geometria, usado para agrupar objetos e como pivô de articulações
class Group(Object3D):

    def __init__(self):
        super().__init__()
