from math import pi, sqrt, radians

from numpy.linalg import inv


# ----------------------------------------------------------------------
# Funções auxiliares
# ----------------------------------------------------------------------

# suavização "ease in / ease out": começa e termina com velocidade zero
def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def interpolar(a, b, t):
    return a + (b - a) * t


# troca o pai de um objeto SEM alterar sua posição no mundo:
#   mundo = matrizMundoNovoPai @ local   =>   local = inv(matrizMundoNovoPai) @ mundo
def trocarPai(objeto, novoPai):
    matrizMundo = objeto.getWorldMatrix()
    if objeto.parent is not None:
        objeto.parent.remove(objeto)
    novoPai.add(objeto)
    objeto.transform = inv(novoPai.getWorldMatrix()) @ matrizMundo


# ----------------------------------------------------------------------
# Estados da operação (nome exibido, etapa do roteiro)
# ----------------------------------------------------------------------
INICIO = ("Início da operação", 1)
CAMINHAO_DESLOCANDO = ("Caminhão a caminho da área de atendimento", 2)
CAMINHAO_FREANDO = ("Caminhão reduzindo a velocidade", 2)
CAMINHAO_ESTACIONADO = ("Caminhão estacionado - robô identifica a chegada", 3)
ROBO_INDO_ATE_CAMINHAO = ("Robô se desloca até a traseira do caminhão", 3)
TAMPA_ABRINDO = ("Abertura da tampa traseira", 4)
ROBO_APROXIMANDO = ("Robô se aproxima da carroceria", 5)
BRACO_ALCANCANDO = ("Braço alcança a encomenda", 5)
PEGANDO_ENCOMENDA = ("Robô segura a encomenda", 5)
BRACO_ERGUENDO = ("Braço ergue a encomenda", 5)
ROBO_RECUANDO = ("Robô recua com a encomenda", 5)
BRACO_RECOLHENDO = ("Braço recolhe a encomenda", 6)
TAMPA_FECHANDO = ("Fechamento da tampa traseira", 6)
CAMINHAO_PARTINDO = ("Caminhão parte - robô volta à base", 6)
ROBO_DEPOSITANDO = ("Robô se posiciona na mesa", 6)
SOLTANDO_ENCOMENDA = ("Robô deposita a encomenda e volta ao repouso", 6)
FIM = ("Operação concluída", 6)


# Coordena o caminhão e o robô por uma máquina de estados.
#
# Cada estado só termina quando sua ação é concluída, e o próximo estado
# depende disso (ex.: o robô só sai da base depois que o caminhão PARA;
# a tampa só abre depois que o robô CHEGA; o braço só se move depois que a
# tampa está ABERTA; a tampa só fecha depois que o robô RECUA...).
#
# Todos os movimentos usam o delta time (segundos), nunca o número de quadros.
class Interacao(object):

    # ---- trajeto do caminhão (eixo X) ----
    X_INICIO = -13.0
    X_ESTACIONAMENTO = 3.0
    X_FIM = 12.5
    VELOCIDADE_MAXIMA = 4.5     # unidades / s
    DISTANCIA_FRENAGEM = 5.0    # começa a frear a 5 unidades da vaga
    # desaceleração constante que leva de VELOCIDADE_MAXIMA a zero na DISTANCIA_FRENAGEM
    DESACELERACAO = VELOCIDADE_MAXIMA ** 2 / (2 * DISTANCIA_FRENAGEM)

    # ---- posições do robô (plano XZ) ----
    BASE_ROBO = (-3.5, 6.0)
    ESPERA_ROBO = (X_ESTACIONAMENTO - 6.5, 0.0)       # longe do arco da tampa
    ATENDIMENTO_ROBO = (X_ESTACIONAMENTO - 4.51, 0.0) # mãos alinhadas com a encomenda
    MESA = (-4.6, 6.0)

    # ---- poses do braço (ombro, cotovelo) em radianos ----
    # ombro + cotovelo = 90° mantém o antebraço na horizontal (caixa nivelada)
    POSE_REPOUSO = (0.0, 0.0)
    POSE_ALCANCE = (radians(75), radians(15))
    POSE_ERGUIDA = (radians(88), radians(2))
    POSE_CARREGANDO = (radians(35), radians(55))

    ANGULO_TAMPA_ABERTA = radians(-100)

    # ---- cores (valores > 1 dão aspecto luminoso) ----
    VERDE = [0.2, 1.4, 0.3]
    AMARELO = [1.5, 1.1, 0.1]
    VERMELHO = [1.5, 0.15, 0.1]
    OLHOS_ESPERA = [0.3, 1.2, 1.4]
    OLHOS_TRABALHO = [0.3, 1.5, 0.4]

    def __init__(self, caminhao, robo, cenario):
        self.caminhao = caminhao
        self.robo = robo
        self.cenario = cenario
        self.reiniciar()

    def reiniciar(self):
        self.tempoAnimacao = 0.0
        self.caminhao.setPosicaoX(self.X_INICIO)
        self.caminhao.velocidade = 0.0
        for roda in self.caminhao.rodas:
            roda.setAngulo(0.0)
        self.caminhao.setAnguloTampa(0.0)
        self.caminhao.recarregar()

        # o robô começa na base, olhando para a faixa do caminhão (-Z)
        self.robo.reiniciar(self.BASE_ROBO[0], self.BASE_ROBO[1], self.robo.yawPara(0, -1))
        self.robo.setCorOlhos(self.OLHOS_ESPERA)
        self.cenario.setCorSinal(self.VERDE)

        self.robo_chegou_base = False
        self.mudarEstado(INICIO)

    def mudarEstado(self, estado):
        self.estado = estado
        # tempo decorrido no estado atual
        self.tempoEstado = 0.0
        # pose dos braços no início do estado (interpolação parte daqui)
        self.poseInicial = self.robo.getPoseBracos()
        print("[Etapa %d] %s" % (estado[1], estado[0]))

    # interpola os braços da pose inicial do estado até "poseFinal"; True ao terminar
    def animarBracos(self, poseFinal, duracao):
        t = smoothstep(self.tempoEstado / duracao)
        self.robo.setPoseBracos(interpolar(self.poseInicial[0], poseFinal[0], t),
                                interpolar(self.poseInicial[1], poseFinal[1], t))
        return self.tempoEstado >= duracao

    # anima a tampa entre dois ângulos; True ao terminar
    def animarTampa(self, inicio, fim, duracao):
        t = smoothstep(self.tempoEstado / duracao)
        self.caminhao.setAnguloTampa(interpolar(inicio, fim, t))
        return self.tempoEstado >= duracao

    # ------------------------------------------------------------------
    # Atualização por quadro (deltaTime em segundos)
    # ------------------------------------------------------------------
    def update(self, deltaTime):
        self.tempoAnimacao += deltaTime
        self.tempoEstado += deltaTime
        estado = self.estado

        # ETAPA 1: cena parada por um instante; robô aguarda na base
        if estado == INICIO:
            if self.tempoEstado >= 1.5:
                self.mudarEstado(CAMINHAO_DESLOCANDO)

        # ETAPA 2: o caminhão acelera até a velocidade de cruzeiro
        elif estado == CAMINHAO_DESLOCANDO:
            c = self.caminhao
            c.velocidade = min(self.VELOCIDADE_MAXIMA, c.velocidade + 3.0 * deltaTime)
            restante = self.X_ESTACIONAMENTO - c.x
            c.avancar(min(c.velocidade * deltaTime, restante))
            if self.X_ESTACIONAMENTO - c.x <= self.DISTANCIA_FRENAGEM:
                self.cenario.setCorSinal(self.AMARELO)
                self.mudarEstado(CAMINHAO_FREANDO)

        # ETAPA 2: frenagem com desaceleração constante: v = sqrt(2·a·d)
        elif estado == CAMINHAO_FREANDO:
            c = self.caminhao
            restante = self.X_ESTACIONAMENTO - c.x
            c.velocidade = max(0.15, sqrt(2 * self.DESACELERACAO * max(restante, 0.0)))
            passo = min(c.velocidade * deltaTime, restante)
            c.avancar(passo)
            if self.X_ESTACIONAMENTO - c.x < 0.001:
                c.avancar(self.X_ESTACIONAMENTO - c.x)
                c.velocidade = 0.0
                self.cenario.setCorSinal(self.VERMELHO)
                self.mudarEstado(CAMINHAO_ESTACIONADO)

        # ETAPA 3: o robô "percebe" o caminhão parado: vira a cabeça para ele
        elif estado == CAMINHAO_ESTACIONADO:
            # ângulo da cabeça (relativo ao corpo) apontando para a traseira do caminhão
            alvoX = self.caminhao.x + self.caminhao.TRASEIRA_X
            dx, dz = alvoX - self.robo.x, 0.0 - self.robo.z
            anguloAlvo = self.robo.yawPara(dx, dz) - self.robo.yaw
            self.robo.setAnguloCabeca(anguloAlvo * smoothstep(self.tempoEstado / 0.8))
            self.robo.setCorOlhos(self.OLHOS_TRABALHO)
            if self.tempoEstado >= 1.2:
                self.anguloCabecaInicial = self.robo.pivoCabeca.angulo
                self.mudarEstado(ROBO_INDO_ATE_CAMINHAO)

        # ETAPA 3: o robô vai da base até o ponto de espera atrás do caminhão
        elif estado == ROBO_INDO_ATE_CAMINHAO:
            self.robo.setAnguloCabeca(self.anguloCabecaInicial * (1 - smoothstep(self.tempoEstado / 0.6)))
            chegou = self.robo.moverPara(*self.ESPERA_ROBO, deltaTime)
            if chegou and self.robo.girarPara(0.0, deltaTime):
                self.mudarEstado(TAMPA_ABRINDO)

        # ETAPA 4: com o caminhão parado e o robô posicionado, a tampa abre
        elif estado == TAMPA_ABRINDO:
            if self.animarTampa(0.0, self.ANGULO_TAMPA_ABERTA, 2.5):
                self.mudarEstado(ROBO_APROXIMANDO)

        # ETAPA 5: tampa aberta -> o robô se aproxima da carroceria
        elif estado == ROBO_APROXIMANDO:
            if self.robo.moverPara(*self.ATENDIMENTO_ROBO, deltaTime, velocidadeMaxima=0.9):
                self.mudarEstado(BRACO_ALCANCANDO)

        # ETAPA 5: só agora o braço se move até a encomenda
        elif estado == BRACO_ALCANCANDO:
            if self.animarBracos(self.POSE_ALCANCE, 1.8):
                self.mudarEstado(PEGANDO_ENCOMENDA)

        # ETAPA 5: a encomenda deixa de ser filha do caminhão e passa a ser
        # filha da mão do robô (mantendo a posição no mundo)
        elif estado == PEGANDO_ENCOMENDA:
            if self.tempoEstado >= 0.4:
                trocarPai(self.caminhao.encomenda, self.robo.maos[0])
                self.mudarEstado(BRACO_ERGUENDO)

        elif estado == BRACO_ERGUENDO:
            if self.animarBracos(self.POSE_ERGUIDA, 0.8):
                self.mudarEstado(ROBO_RECUANDO)

        # ETAPA 5: o robô recua de ré, levando a encomenda
        elif estado == ROBO_RECUANDO:
            if self.robo.moverPara(*self.ESPERA_ROBO, deltaTime, velocidadeMaxima=0.9, re=True):
                self.mudarEstado(BRACO_RECOLHENDO)

        # ETAPA 6: braço traz a encomenda para junto do corpo
        elif estado == BRACO_RECOLHENDO:
            if self.animarBracos(self.POSE_CARREGANDO, 1.0):
                self.mudarEstado(TAMPA_FECHANDO)

        # ETAPA 6: o robô saiu da área da tampa -> a tampa fecha
        elif estado == TAMPA_FECHANDO:
            if self.animarTampa(self.ANGULO_TAMPA_ABERTA, 0.0, 2.5):
                self.cenario.setCorSinal(self.VERDE)
                self.robo_chegou_base = False
                self.mudarEstado(CAMINHAO_PARTINDO)

        # ETAPA 6: tampa fechada -> o caminhão parte e o robô volta para a base
        elif estado == CAMINHAO_PARTINDO:
            c = self.caminhao
            if c.x < self.X_FIM:
                c.velocidade = min(self.VELOCIDADE_MAXIMA, c.velocidade + 2.0 * deltaTime)
                c.avancar(min(c.velocidade * deltaTime, self.X_FIM - c.x))
            if not self.robo_chegou_base:
                self.robo_chegou_base = self.robo.moverPara(*self.BASE_ROBO, deltaTime)
            if c.x >= self.X_FIM and self.robo_chegou_base:
                c.velocidade = 0.0
                self.mudarEstado(ROBO_DEPOSITANDO)

        # ETAPA 6: o robô vira para a mesa
        elif estado == ROBO_DEPOSITANDO:
            if self.robo.girarPara(pi, deltaTime):
                self.mudarEstado(SOLTANDO_ENCOMENDA)

        # ETAPA 6: a encomenda passa a pertencer ao cenário (sobre a mesa)
        # e os braços voltam ao repouso
        elif estado == SOLTANDO_ENCOMENDA:
            if self.caminhao.encomenda.parent is self.robo.maos[0]:
                trocarPai(self.caminhao.encomenda, self.cenario)
                self.robo.setCorOlhos(self.OLHOS_ESPERA)
            if self.animarBracos(self.POSE_REPOUSO, 1.2):
                self.mudarEstado(FIM)

        # fim: aguarda e reinicia o ciclo
        elif estado == FIM:
            if self.tempoEstado >= 3.0:
                self.reiniciar()

        # o sinalizador do robô pulsa enquanto ele trabalha
        trabalhando = self.estado not in (INICIO, CAMINHAO_DESLOCANDO, CAMINHAO_FREANDO, FIM)
        self.robo.pulsarSinalizador(self.tempoAnimacao, trabalhando)
