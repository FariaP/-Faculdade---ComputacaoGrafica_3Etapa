# Robô de Serviço & Caminhão de Entrega — Computação Gráfica

Aplicação 3D em **Python + Pygame + OpenGL (3.3 core)**, construída sobre o framework
do livro *Developing Graphics Frameworks with Python and OpenGL* (Stemkoski & Pascale, 2022),
na qual um caminhão de entrega e um robô de serviço realizam uma operação coordenada de
recebimento de mercadoria.

---

## 1. Integrantes

|            Nome            | Matrícula |

| Pedro Henrique Faria Silva | 232-000281 |
| Raphael Antônio Ferreira   | 241-006886 |

## 2. Temas

- **Tema 1 – Robô de serviço:** desloca-se pelo ambiente, movimenta braços articulados e
  recebe uma encomenda, coordenando-se com o caminhão.
- **Tema 13 – Caminhão de entrega:** desloca-se com rodas girando, para em uma vaga definida e
  abre/fecha a tampa traseira em coordenação com o robô.

## 3. Descrição da cena

Plataforma retangular fixa (34 × 19 unidades), com estética minimalista:

| Elemento | Construção |
|---|---|
| Piso | `BoxGeometry` com **textura de concreto** repetida (`repeatUV`) |
| Faixa do caminhão | traço central branco e bordas laterais |
| Área de estacionamento | retângulo amarelo + linha de parada com listras de sinalização |
| Área de atendimento | retângulo azul atrás da vaga, com bordas listradas |
| Base do robô | disco azul na lateral, com trajeto tracejado até a área de atendimento |
| Decoração | 4 pilares (cilindros), painel metálico ao fundo, mesa de recebimento, palete e pilhas de caixas |
| Semáforo | verde = livre, amarelo = aproximação, vermelho = atendimento |

O caminhão inicia na extremidade esquerda (x = −13), estaciona em x = 3 e parte para a direita.
O robô fica na lateral (base em x = −3,5; z = 6).

## 4. Sequência de interação

Implementada como **máquina de estados** em `animation/interacao.py`. Cada estado só termina
quando a sua ação é concluída, e o próximo estado depende disso. O nome da etapa atual aparece
no título da janela e no console.

| Etapa | Estado | O que acontece | Depende de |

| 1 | `INICIO` | cena parada; robô aguarda na base | — |
| 2 | `CAMINHAO_DESLOCANDO` | caminhão acelera até 4,5 u/s; rodas giram | início |
| 2 | `CAMINHAO_FREANDO` | desaceleração constante (v = √(2·a·d)); semáforo amarelo | distância à vaga |
| 3 | `CAMINHAO_ESTACIONADO` | caminhão para; semáforo vermelho; **robô vira a cabeça para o caminhão** e os olhos mudam de cor | caminhão parado |
| 3 | `ROBO_INDO_ATE_CAMINHAO` | robô vai da base até o ponto de espera atrás do caminhão | caminhão parado |
| 4 | `TAMPA_ABRINDO` | tampa gira 100° em torno da dobradiça superior | robô posicionado |
| 5 | `ROBO_APROXIMANDO` | robô avança até a carroceria | tampa aberta |
| 5 | `BRACO_ALCANCANDO` | ombros e cotovelos levam as mãos até a encomenda | robô na carroceria |
| 5 | `PEGANDO_ENCOMENDA` | a caixa troca de pai: do caminhão para a mão do robô | braço estendido |
| 5 | `BRACO_ERGUENDO` / `ROBO_RECUANDO` | ergue a caixa e recua de ré | caixa presa |
| 6 | `BRACO_RECOLHENDO` | traz a caixa junto ao corpo | robô fora do arco da tampa |
| 6 | `TAMPA_FECHANDO` | tampa fecha | robô afastado |
| 6 | `CAMINHAO_PARTINDO` | caminhão parte; robô volta à base ao mesmo tempo | tampa fechada |
| 6 | `ROBO_DEPOSITANDO` / `SOLTANDO_ENCOMENDA` | robô vira para a mesa, solta a caixa (que passa a pertencer ao cenário) e volta ao repouso | robô na base |
| — | `FIM` | após 3 s o ciclo reinicia | — |

## 5. Instalação

Requisitos: Python 3.10 ou superior e placa de vídeo com OpenGL 3.3.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

> Usamos o `pygame-ce` porque o `pygame` original não tem pacote para o Python 3.14.
> A API é a mesma (`import pygame`).

## 6. Execução

```bash
python main.py              # limite de 60 FPS
python main.py --fps 20     # teste de independência de FPS: as durações não mudam
```

As texturas já estão em `assets/textures/`. Para gerá-las novamente:
`python tools/gerar_texturas.py`.

## 7. Controles

| Tecla | Ação |
| W / S | câmera para frente / para trás |
| A / D | câmera para a esquerda / direita |
| R / F | câmera sobe / desce |
| Q / E | girar a câmera para a esquerda / direita |
| T / G | olhar para cima / para baixo |
| 1 / 2 / 3 / 4 | vistas prontas: geral, lateral do atendimento, traseira do caminhão, superior |
| **P** | **pausar** a animação (a cena continua sendo desenhada e a câmera continua livre) |
| **C** | **continuar** a animação |
| N | reiniciar a operação |
| ESC | sair |

## 8. Estrutura do projeto

```text
ComputacaoGrafica_3Etapa/
├── main.py                    # aplicação: cena, luzes, sombras, câmera, pausa
├── core/                      # framework (livro): Base, Input, Attribute, Uniform, Matrix,
│                              #   Object3D, Scene, Group, Camera, Mesh, Renderer, Texture, RenderTarget
├── geometry/                  # Geometry, Rectangle, Box, Polygon, Parametric, Sphere/Ellipsoid,
│                              #   Cylindrical, Cylinder, Cone
├── material/                  # Material, LambertMaterial, PhongMaterial, DepthMaterial
├── light/                     # Light, AmbientLight, DirectionalLight, PointLight, Shadow
├── extras/movementRig.py      # câmera controlada pelo teclado
├── models/
│   ├── articulacao.py         # pivô genérico de articulação
│   ├── caminhao.py            # modelo hierárquico do caminhão
│   └── robo.py                # modelo hierárquico do robô
├── environment/cenario.py     # plataforma fixa
├── animation/interacao.py     # máquina de estados da interação
├── tools/gerar_texturas.py    # gerador das texturas procedurais
└── assets/textures/           # concreto.png, metal.png, caixa.png, listras.png
```

> Os shaders GLSL ficam embutidos nas classes de material (em strings), como no livro;
> por isso não existe uma pasta `shaders/` separada.

## 9. recurso gráfico

| Requisito | Arquivo → classe / função |
|---|---|
| Modelagem do robô | `models/robo.py` → `Robo.construirBase/Tronco/Cabeca/Bracos` |
| Modelagem do caminhão | `models/caminhao.py` → `Caminhao.construirChassiECabine/Carroceria/Rodas/Tampa/Carga` |
| Primitivas | `geometry/boxGeometry.py`, `cylinderGeometry.py`, `sphereGeometry.py`, `coneGeometry.py`, `parametricGeometry.py` |
| Translação / rotação / escala | `core/matrix.py` → `Matrix.makeTranslation/makeRotationX/Y/Z/makeScale`; uso: `Robo.atualizarTransformacao`, `Articulacao.atualizarTransformacao`, `Robo.pulsarSinalizador` (escala animada), `Cenario.construirDecoracao` (caixas por escala) |
| Hierarquia (grafo de cena) | `core/object3D.py` → `Object3D.add`, `getWorldMatrix`; pivôs em `models/articulacao.py` |
| Troca de pai preservando a posição | `animation/interacao.py` → `trocarPai` |
| Animação por delta time | `core/base.py` → `Base.run` (`deltaTime`); `Interacao.update(deltaTime)`; `Caminhao.avancar`; `Robo.moverPara/girarPara` |
| Rotação das rodas | `Caminhao.avancar` (ângulo = distância / raio) e `Robo.moverPara` |
| Tampa articulada | `Caminhao.construirTampa` (`pivoTampa`), `Caminhao.setAnguloTampa`, `Interacao.animarTampa` |
| Braços articulados | `Robo.construirBracos` (`ombros`, `cotovelos`, `maos`), `Robo.setPoseBracos`, `Interacao.animarBracos` |
| Câmera em perspectiva | `core/camera.py` → `Camera` (`Matrix.makePerspective`); `main.py` → `Main.initialize`, `posicionarCamera`, `vistaCamera` |
| Controle da câmera | `extras/movementRig.py` → `MovementRig.update` |
| Pausar / retomar | `main.py` → `Main.update` (teclas P e C; `self.pausado`) |
| Texturas | `core/texture.py` → `Texture.uploadData`; uniforms `textureSampler` e `repeatUV` nos materiais; UVs em `BoxGeometry` e `ParametricGeometry` |
| Iluminação direcional e ambiente | `light/directionalLight.py`, `light/ambientLight.py`; função GLSL `lightCalc` em `material/lambertMaterial.py` e `phongMaterial.py` |
| Materiais sensíveis à luz | `LambertMaterial` (piso, faixas), `PhongMaterial` (robô, caminhão, decoração) |
| Vetores normais | `vertexNormal` e `faceNormal` nas geometrias; matriz das normais (`transpose(inverse(mat3(modelMatrix)))`) no vertex shader |
| **Shadow Mapping** | `light/shadow.py` → `Shadow`; `material/depthMaterial.py`; `core/renderTarget.py`; `core/renderer.py` → `Renderer.render` (1ª passada) e `enableShadows`; teste de sombra no fragment shader dos materiais |

## 10. Explicação técnica

### 10.1 Shaders, atributos e uniforms

- **Atributos de vértice** (`in` no vertex shader, `core/attribute.py`): `vertexPosition` (vec3),
  `vertexUV` (vec2) e `vertexNormal` (vec3). Ficam em VBOs, e a associação é gravada no VAO
  de cada `Mesh`.
- **Uniforms** (`core/uniform.py`):
  - matrizes `modelMatrix`, `viewMatrix` e `projectionMatrix`;
  - `baseColor`, `useTexture`, `textureSampler` e `repeatUV`;
  - `light0`…`light3` (struct `Light`: tipo, cor, direção, posição, atenuação);
  - `viewPosition`, `specularStrength` e `shininess` (Phong);
  - `useShadow` e `shadow0` (struct `Shadow`: direção da luz, matrizes da câmera da luz,
    mapa de profundidade, intensidade e bias).
- **Vertex shader:** calcula `gl_Position = P · V · M · posição`, a posição no mundo, a normal
  transformada e a posição do vértice no espaço da câmera da luz (`shadowPosition0`).
- **Fragment shader:** cor-base × textura × soma das luzes (ambiente + difusa + especular),
  multiplicada pelo fator de sombra.

### 10.2 Transformações e hierarquia

A matriz de mundo de cada nó é `getWorldMatrix() = matrizMundoDoPai @ transformLocal`.
Cada articulação é um **pivô** (`Articulacao`, um `Group` vazio) posicionado na junta, com
`transform = T(junta) @ R(eixo, ângulo)`. A peça é adicionada ao pivô **deslocada**, de modo que
gira em torno da junta e não do próprio centro.

- **Robô:** `Robo → tronco → ombro → braço → cotovelo → antebraço → mão`. Mover ou girar o robô
  leva os braços junto, sem perder a posição relativa.
- **Caminhão:** `Caminhao → pivoTampa → tampa` (dobradiça no topo da traseira) e
  `Caminhao → roda[i]` (giro em Z).
- **Caixa:** é filha do caminhão, depois da mão do robô e por fim do cenário. A cada troca,
  `trocarPai` calcula `local = inv(mundoNovoPai) @ mundoAtual`, e a caixa não "salta".

### 10.3 Animação

O `Base.run` mede o tempo de cada quadro (`deltaTime`, em segundos). Velocidades estão em
unidades por segundo e durações em segundos. Interpolações usam `smoothstep` (aceleração e
desaceleração suaves), e o `deltaTime` é limitado a 0,05 s para evitar saltos. A independência
de FPS foi testada: a 20 FPS e a 60 FPS as etapas começam nos mesmos instantes
(por exemplo, caminhão parado em 6,8 s e tampa abrindo em 13,0 s).

### 10.4 Shadow Mapping (seção 6.9 do livro)

1. **Passada de profundidade:** uma câmera **ortográfica** filha da `DirectionalLight` (mesma
   direção dos raios) renderiza a cena em um `RenderTarget` 2048×2048 com o `DepthMaterial`, que
   grava a profundidade de cada fragmento (`gl_FragCoord.z`).
2. **Passada normal:** no vertex shader, cada vértice também é projetado pela câmera da luz
   (`shadowPosition0`). No fragment shader, essa posição é levada para [0, 1] e comparada com a
   profundidade gravada no mapa. Se houver algo mais próximo da luz, o fragmento está em sombra
   e a cor é escurecida por `strength`.
3. O mapa é refeito **a cada quadro**, então a sombra acompanha o caminhão, as rodas, a tampa e
   o robô em movimento, sempre coerente com a direção da luz.

Ajustes acrescentados ao algoritmo do livro:
- a profundidade é codificada em **24 bits nos canais RGB** (o livro usa 8 bits), o que reduz
  o *shadow acne*;
- **bias proporcional à inclinação** da superfície em relação à luz;
- **PCF 3×3**: média de 9 comparações, que suaviza a borda da sombra.

## 11. Diferenças em relação ao framework do livro

Os arquivos do framework não foram fornecidos junto com o enunciado. Por isso as classes foram
reimplementadas seguindo o livro e os slides da disciplina (mesmos nomes de classes, métodos e
atributos, em camelCase). As alterações foram:

- `numpy.itemset` não existe no NumPy 2: `Object3D.setPosition` usa indexação direta.
- O uniform de textura chama-se `textureSampler`, porque um uniform chamado `texture` esconderia
  a função GLSL `texture()` no perfil core.
- `glBindAttribLocation(…, 0, "vertexPosition")`: garante que o VAO de cada malha funcione também
  com o `DepthMaterial` na passada de sombra.
- `Mesh.castShadow` permite que lâmpadas e o sinalizador não projetem sombra.
- `repeatUV` foi acrescentado aos materiais Lambert e Phong, para repetir a textura do piso.
- `Renderer.render` envia os uniforms comuns uma vez por material a cada quadro e restaura a cor
  de fundo após a passada de sombra.
- `OpenGL.ERROR_CHECKING = False` em `main.py`, por desempenho. Para depurar, troque para `True`.

## 12. Contribuições individuais

| Integrante | Contribuições |
|---|---|
| Pedro Henrique Faria Silva | _preencher_ |
| _Integrante 2_ | _preencher_ |

## 13. Fontes consultadas

- STEMKOSKI, L.; PASCALE, M. *Developing Graphics Frameworks with Python and OpenGL*. CRC Press, 2022
  (capítulos 2 a 6; seção 6.9 – Shadows).
- Slides da disciplina: *Computação Gráfica – Luz e Sombra* (Prof. Dr. Rodrigo Fernandes dos Santos, 2026).
- Documentação do Pygame-ce (https://pyga.me/docs/) e do PyOpenGL (https://pyopengl.sourceforge.net/).
- Especificação da GLSL 3.30 (Khronos Group).

### Origem das texturas

Todas as imagens em `assets/textures/` são **procedurais** e foram geradas pelo script
`tools/gerar_texturas.py` (autoria da dupla), com ruído aleatório (numpy) e desenhos simples
(pygame.draw). Nenhuma imagem de terceiros foi utilizada.

| Arquivo | Uso |
|---|---|
| `concreto.png` | piso da plataforma |
| `metal.png` | carroceria e tampa do caminhão, painel ao fundo |
| `caixa.png` | encomenda e caixas decorativas |
| `listras.png` | linha de parada, bordas da área de atendimento e faixa da tampa |

## 14. Declaração de uso de Inteligência Artificial

- **Ferramenta:** Claude Code (modelo Claude Opus 5.5, da Anthropic).
- **Finalidade:** análise dos slides e dos requisitos, proposta de arquitetura, geração do código
  inicial (framework reconstruído, modelos, cenário, máquina de estados, Shadow Mapping, gerador
  de texturas), diagnóstico de desempenho e redação deste README.
- **Trechos produzidos ou revisados com auxílio da IA:** todos os arquivos `.py` do projeto e
  este README, na versão inicial.
- **Revisão humana:** Foi revisada toda arquitetura do projeto, classes, parâmetros, fizemos testes manuais em cada etapa do processo pra identificar alguns erros que estava ocorrendo com cada elemento, tinha vez que o caminhão atrasava muito pra chegar no mesmo tempo que o robô ou vice e versa, na hora do robô pegar caixa tinha vez que não estava na direção correta e ele só esticava o braço mas acabava que não pegava em nada.
