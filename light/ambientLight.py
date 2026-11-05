from light.light import Light


# Contribuição uniforme de iluminação: não depende de posição nem de direção
class AmbientLight(Light):

    def __init__(self, color=[1, 1, 1]):
        super().__init__(Light.AMBIENT)
        self.color = color
