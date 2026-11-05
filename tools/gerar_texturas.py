"""
Gera as imagens de textura usadas na cena (assets/textures/).

Todas as imagens são PROCEDURAIS: criadas por este script a partir de ruído
aleatório e desenhos simples com numpy + pygame. Por isso não há imagens de
terceiros no projeto, e a origem de cada textura fica documentada aqui.

Execução (a partir da pasta raiz do projeto):
    python tools/gerar_texturas.py
"""
import os

import numpy
import pygame

PASTA_SAIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "assets", "textures")

rng = numpy.random.default_rng(13)


def ruidoPeriodico(tamanho, escala):
    """Ruído suave e repetível (tileable): ruído branco borrado com deslocamentos
    circulares (numpy.roll), de modo que as bordas se encaixem ao repetir."""
    r = rng.random((tamanho, tamanho))
    for _ in range(3):
        acumulado = numpy.zeros_like(r)
        for dx in range(-escala, escala + 1):
            acumulado += numpy.roll(r, dx, axis=0)
        r = acumulado / (2 * escala + 1)
        acumulado = numpy.zeros_like(r)
        for dy in range(-escala, escala + 1):
            acumulado += numpy.roll(r, dy, axis=1)
        r = acumulado / (2 * escala + 1)
    r = (r - r.min()) / (r.max() - r.min())
    return r


def salvar(rgb, nome):
    rgb = numpy.clip(rgb, 0, 255).astype(numpy.uint8)
    # pygame.surfarray usa a ordem (x, y); numpy usa (linha, coluna)
    superficie = pygame.surfarray.make_surface(rgb.transpose(1, 0, 2))
    caminho = os.path.join(PASTA_SAIDA, nome)
    pygame.image.save(superficie, caminho)
    print("gerada:", caminho)


def concreto(tamanho=512):
    """Piso de concreto: manchas em várias escalas + juntas de dilatação nas bordas."""
    base = (0.50 * ruidoPeriodico(tamanho, 24) +
            0.30 * ruidoPeriodico(tamanho, 6) +
            0.20 * rng.random((tamanho, tamanho)))
    cinza = 150 + 55 * (base - 0.5)

    # pequenas manchas escuras
    manchas = ruidoPeriodico(tamanho, 3)
    cinza -= 25 * numpy.clip(manchas - 0.75, 0, 1) / 0.25

    # juntas entre as placas (linhas escuras na borda da imagem)
    for i in range(3):
        cinza[i, :] -= 45 - 12 * i
        cinza[:, i] -= 45 - 12 * i

    rgb = numpy.stack([cinza * 0.98, cinza * 0.99, cinza * 1.02], axis=2)
    salvar(rgb, "concreto.png")


def metal(tamanho=256):
    """Chapa metálica corrugada (frisos verticais) com riscos de escovado."""
    x = numpy.arange(tamanho)
    frisos = 0.5 + 0.5 * numpy.sin(x / tamanho * 2 * numpy.pi * 8)
    frisos = numpy.tile(frisos, (tamanho, 1))
    escovado = numpy.repeat(rng.random((1, tamanho)), tamanho, axis=0)
    ruido = ruidoPeriodico(tamanho, 8)
    valor = 175 + 55 * (frisos - 0.5) + 18 * (escovado - 0.5) + 25 * (ruido - 0.5)
    rgb = numpy.stack([valor, valor, valor * 1.03], axis=2)
    salvar(rgb, "metal.png")


def caixa(tamanho=256):
    """Papelão com fita adesiva central e uma seta "este lado para cima"."""
    ruido = 0.6 * ruidoPeriodico(tamanho, 4) + 0.4 * rng.random((tamanho, tamanho))
    r = 185 + 30 * (ruido - 0.5)
    g = 140 + 25 * (ruido - 0.5)
    b = 90 + 20 * (ruido - 0.5)
    rgb = numpy.stack([r, g, b], axis=2)

    # fita adesiva (faixa vertical clara)
    inicio, fim = int(tamanho * 0.42), int(tamanho * 0.58)
    rgb[:, inicio:fim, 0] = 215
    rgb[:, inicio:fim, 1] = 190
    rgb[:, inicio:fim, 2] = 140

    # borda escura
    rgb[:4, :, :] *= 0.7
    rgb[-4:, :, :] *= 0.7
    rgb[:, :4, :] *= 0.7
    rgb[:, -4:, :] *= 0.7

    superficie = pygame.surfarray.make_surface(numpy.clip(rgb, 0, 255).astype(numpy.uint8).transpose(1, 0, 2))
    cor = (70, 45, 25)
    s = tamanho
    # seta para cima no canto inferior esquerdo
    pygame.draw.polygon(superficie, cor, [(s * 0.17, s * 0.62), (s * 0.27, s * 0.50), (s * 0.37, s * 0.62)])
    pygame.draw.rect(superficie, cor, (s * 0.24, s * 0.62, s * 0.06, s * 0.16))
    # símbolo de "frágil" (taça simplificada) no canto direito
    pygame.draw.polygon(superficie, cor, [(s * 0.66, s * 0.50), (s * 0.82, s * 0.50), (s * 0.74, s * 0.64)])
    pygame.draw.rect(superficie, cor, (s * 0.73, s * 0.64, s * 0.02, s * 0.10))
    pygame.draw.rect(superficie, cor, (s * 0.69, s * 0.74, s * 0.10, s * 0.02))
    caminho = os.path.join(PASTA_SAIDA, "caixa.png")
    pygame.image.save(superficie, caminho)
    print("gerada:", caminho)


def listras(tamanho=256):
    """Faixa de sinalização industrial: listras diagonais amarelas e pretas."""
    y, x = numpy.mgrid[0:tamanho, 0:tamanho]
    faixa = ((x + y) // (tamanho // 4)) % 2
    ruido = ruidoPeriodico(tamanho, 3)
    r = numpy.where(faixa == 0, 240, 35) - 20 * ruido
    g = numpy.where(faixa == 0, 190, 35) - 20 * ruido
    b = numpy.where(faixa == 0, 20, 35) - 10 * ruido
    salvar(numpy.stack([r, g, b], axis=2), "listras.png")


if __name__ == "__main__":
    os.makedirs(PASTA_SAIDA, exist_ok=True)
    concreto()
    metal()
    caixa()
    listras()
