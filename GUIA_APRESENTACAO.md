# Guia de Apresentação – Robô de Serviço e Caminhão de Entrega

Material de estudo para a apresentação (cerca de 10 minutos, em dupla). Resume o que foi
implementado, onde cada recurso está no código e como explicar cada conceito nas perguntas
individuais (30% da nota).

---

## 1. Visão geral em 30 segundos

Um caminhão entra na plataforma, freia e estaciona. O robô percebe a chegada (vira a cabeça),
vai até a traseira e espera; a tampa abre; o robô se aproxima, estende os braços e retira a
caixa; recua; a tampa fecha; o caminhão parte; o robô leva a caixa até a mesa. O ciclo dura
cerca de 37 s e reinicia.

Tecnologias: Python 3.14, pygame-ce (janela, teclado, tempo), PyOpenGL (OpenGL 3.3 core),
numpy (matrizes) e o framework do livro de Stemkoski & Pascale.

| Pasta | Papel |
|---|---|
| `core/` | framework: janela e laço (`Base`), teclado (`Input`), buffers (`Attribute`), uniforms (`Uniform`), matrizes (`Matrix`), grafo de cena (`Object3D`, `Group`, `Scene`), `Camera`, `Mesh`, `Renderer`, `Texture`, `RenderTarget` |
| `geometry/` | primitivas: caixa, retângulo, polígono, superfícies paramétricas (esfera, cilindro, cone) |
| `material/` | shaders GLSL: `LambertMaterial`, `PhongMaterial`, `DepthMaterial` (sombra) |
| `light/` | `Light`, `AmbientLight`, `DirectionalLight`, `PointLight`, `Shadow` |
| `extras/movementRig.py` | câmera controlada pelo teclado |
| `models/` | `Caminhao`, `Robo` e o pivô `Articulacao` |
| `environment/cenario.py` | plataforma fixa |
| `animation/interacao.py` | máquina de estados que coordena os dois personagens |
| `main.py` | monta a cena, luzes, sombra, câmera, pausa |

Os shaders não estão em arquivos `.glsl`: ficam em strings dentro das classes de material,
como no livro. Se perguntarem "onde estão os shaders?", a resposta é `material/lambertMaterial.py`,
`material/phongMaterial.py` e `material/depthMaterial.py`.

---

## 2. Divisão sugerida para a apresentação

É só uma sugestão: ajustem conforme o que cada um realmente fez e revisou, e registrem a
divisão final na seção "Contribuições individuais" do README. Os dois precisam saber explicar
a aplicação inteira.

| Parte | Pedro Henrique | Raphael Antônio |
|---|---|---|
| Framework e pipeline (atributos, uniforms, shaders) | ✔ | |
| Caminhão (modelagem, rodas, tampa) | ✔ | |
| Cenário e texturas | ✔ | |
| Shadow Mapping | ✔ | |
| Robô (modelagem, braços, hierarquia) | | ✔ |
| Máquina de estados e delta time | | ✔ |
| Câmera, controles e pausa | | ✔ |
| Iluminação (Lambert, Phong, normais) | | ✔ |

Roteiro de 10 minutos: 1 min cena e temas → 2 min modelos e hierarquia → 2 min animação e
interação (rodar ao vivo, usar P/C e as vistas 1–4) → 1,5 min câmera e texturas →
1,5 min iluminação → 2 min Shadow Mapping.

---

## 3. Pipeline de renderização: atributos, uniforms e shaders

**Atributos de vértice** (um valor por vértice, guardados em VBOs na GPU – `core/attribute.py`):

| Atributo | Tipo | Para que serve |
|---|---|---|
| `vertexPosition` | vec3 | posição do vértice no espaço local do objeto |
| `vertexUV` | vec2 | coordenada de textura (0 a 1) |
| `vertexNormal` | vec3 | direção perpendicular à superfície, usada na iluminação |
| `faceNormal` | vec3 | normal da face (dado da geometria, como nos slides) |

`Attribute.uploadData` envia a lista para a GPU (`glBufferData`) e
`Attribute.associateVariable` liga o buffer à variável `in` do shader (`glVertexAttribPointer`).
O `Mesh` grava essas ligações em um VAO, para não refazê-las a cada quadro.

**Uniforms** (um valor por desenho, igual para todos os vértices – `core/uniform.py`):

| Uniform | Tipo | Conteúdo |
|---|---|---|
| `modelMatrix` | mat4 | posição/rotação/escala do objeto no mundo |
| `viewMatrix` | mat4 | inversa da matriz da câmera |
| `projectionMatrix` | mat4 | projeção em perspectiva |
| `baseColor` | vec3 | cor do material |
| `useTexture`, `textureSampler`, `repeatUV` | bool, sampler2D, vec2 | textura e quantas vezes ela repete |
| `light0` … `light3` | struct Light | tipo, cor, direção, posição, atenuação |
| `viewPosition`, `specularStrength`, `shininess` | vec3, float, float | brilho especular (Phong) |
| `useShadow`, `shadow0` | bool, struct Shadow | dados do Shadow Mapping |

**Vertex shader** (roda uma vez por vértice):
`gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0)`;
também calcula a posição no mundo, a normal transformada e a posição vista pela luz.

**Fragment shader** (roda uma vez por pixel): cor-base × textura × soma das luzes
(função `lightCalc`) × fator de sombra.

**Renderer** (`core/renderer.py`, `Renderer.render`): percorre o grafo de cena, filtra os
`Mesh` e as luzes e, para cada malha, ativa o programa (`glUseProgram`), o VAO, envia os uniforms
e desenha (`glDrawArrays`). Antes disso faz a passada de sombra (seção 9).

---

## 4. Transformações e hierarquia

**As três transformações** (`core/matrix.py`, matrizes 4×4 homogêneas):

| Transformação | Função | Onde aparece na cena |
|---|---|---|
| Translação | `Matrix.makeTranslation` | deslocamento do caminhão e do robô, posição de cada peça |
| Rotação | `makeRotationX/Y/Z` | rodas (Z), tampa (Z), ombros e cotovelos (Z), cabeça e direção do robô (Y) |
| Escala | `makeScale` | sinalizador do robô pulsando (`Robo.pulsarSinalizador`), caixas decorativas do cenário (cubo unitário escalado) |

**Grafo de cena**: cada `Object3D` tem uma matriz local (`transform`), um pai e filhos.
A matriz de mundo é `getWorldMatrix() = matriz de mundo do pai @ matriz local`. Por isso, ao
mover o robô, braços, cabeça e caixa vão junto.

**Pivô de articulação** (`models/articulacao.py`): uma caixa gira em torno do próprio centro.
Para girar em torno da junta, cria-se um `Group` vazio na junta e coloca-se a peça dentro dele,
deslocada. A matriz do pivô é `T(posição da junta) @ R(eixo, ângulo)`.

```text
Robo  (T(x,0,z) @ Ry(yaw))
├── base, rodas[0..1]         (Articulacao, giro em Z)
└── tronco
    ├── corpo, painel, pescoço
    ├── pivoCabeca            (Articulacao, giro em Y)
    │   └── cabeça, visor, olhos, antena, sinalizador
    └── ombros[0..1]          (Articulacao, giro em Z)
        └── braço
            └── cotovelos[0..1]   (Articulacao, giro em Z)
                └── antebraço
                    └── maos[0..1]   ← a caixa vira filha daqui

Caminhao  (T(x,0,0))
├── chassi, cabine, carroceria (piso, teto, laterais, frente)
├── rodas[0..5]               (Articulacao, giro em Z)
├── pivoTampa                 (Articulacao na dobradiça de cima, giro em Z)
│   └── tampa, puxador, faixa listrada
└── encomenda                 (caixa)
```

**Ordem importa**: `T @ R` gira primeiro e depois desloca (o objeto gira no lugar). `R @ T`
deslocaria e depois giraria em torno da origem (o objeto "orbitaria").

**Troca de pai sem "pular"** (`animation/interacao.py`, função `trocarPai`): a caixa sai do
caminhão, vai para a mão do robô e depois para o cenário. Para manter a posição no mundo:
`local novo = inversa(mundo do novo pai) @ mundo atual da caixa`.

---

## 5. Animação e interação

**Delta time** (`core/base.py`, `Base.run`): a cada quadro, `deltaTime = clock.get_time() / 1000`
(segundos desde o quadro anterior). Toda velocidade é "por segundo" e é multiplicada por
`deltaTime`. Assim, a 20 ou a 60 FPS o caminhão anda a mesma distância por segundo. Testado:
nas duas taxas o caminhão para em 6,8 s e a tampa abre em 13,0 s. O `deltaTime` é limitado a
0,05 s em `main.py` para evitar saltos se a janela travar.

**Rodas**: rolamento sem deslizar: `ângulo = distância / raio` (`Caminhao.avancar`). Se o
caminhão para, as rodas param.

**Frenagem**: desaceleração constante; a velocidade segue `v = √(2·a·d)`, em que `d` é a
distância até a vaga (`CAMINHAO_FREANDO`).

**Movimentos suaves**: braços e tampa usam `smoothstep(t) = 3t² − 2t³`, que começa e termina
com velocidade zero.

**Máquina de estados** (`Interacao.update`): o próximo estado só começa quando a ação do
anterior termina. É isso que prova a dependência entre os personagens.

| Etapa | Estado | Gatilho para avançar |
|---|---|---|
| 1 | `INICIO` | 1,5 s |
| 2 | `CAMINHAO_DESLOCANDO` | faltam 5 unidades para a vaga |
| 2 | `CAMINHAO_FREANDO` | caminhão parou na vaga |
| 3 | `CAMINHAO_ESTACIONADO` | robô virou a cabeça para o caminhão |
| 3 | `ROBO_INDO_ATE_CAMINHAO` | robô chegou ao ponto de espera |
| 4 | `TAMPA_ABRINDO` | tampa a −100° |
| 5 | `ROBO_APROXIMANDO` | robô junto à carroceria |
| 5 | `BRACO_ALCANCANDO` | mãos na caixa |
| 5 | `PEGANDO_ENCOMENDA` | caixa passa a ser filha da mão |
| 5 | `BRACO_ERGUENDO` → `ROBO_RECUANDO` | robô fora do arco da tampa |
| 6 | `BRACO_RECOLHENDO` → `TAMPA_FECHANDO` | tampa fechada |
| 6 | `CAMINHAO_PARTINDO` | caminhão no fim e robô na base |
| 6 | `ROBO_DEPOSITANDO` → `SOLTANDO_ENCOMENDA` | caixa na mesa, braços em repouso |
| – | `FIM` | 3 s, reinicia |

Detalhe de projeto: o robô espera longe da traseira enquanto a tampa abre, porque a tampa
gira para trás e bateria na cabeça dele. Só depois avança.

---

## 6. Câmera, controles e pausa

- **Perspectiva**: `Camera(angleOfView=60, aspectRatio=1280/720, near=0.1, far=200)` usa
  `Matrix.makePerspective`. Objetos distantes ficam menores.
- **Matriz de visão**: `Camera.updateViewMatrix` = inversa da matriz de mundo da câmera
  (mover a câmera para a direita equivale a mover o mundo para a esquerda).
- **MovementRig** (`extras/movementRig.py`): o rig gira em Y (olhar para os lados) e um filho,
  `lookAttachment`, gira em X (olhar para cima/baixo). Separar os dois evita inclinar o horizonte.
- **Teclas**: W/S/A/D movem, R/F sobem e descem, Q/E giram, T/G olham para cima e para baixo,
  1–4 são vistas prontas (`Main.vistaCamera`), N reinicia, ESC sai.
- **Pausa** (`Main.update`): P define `pausado = True` e C volta para `False`. Pausado, só
  `interacao.update` deixa de ser chamado; a câmera e a renderização continuam funcionando.

---

## 7. Texturas

- `Texture` (`core/texture.py`) carrega a imagem com pygame, inverte na vertical (no OpenGL
  V = 0 é embaixo) e envia com `glTexImage2D`; gera mipmaps e define filtros e `GL_REPEAT`.
- O uniform `textureSampler` liga a textura a uma **unidade de textura** (`glActiveTexture`).
- **Coordenadas UV**: cada face da `BoxGeometry` recebe UVs de (0,0) a (1,1); nas paramétricas,
  `u` e `v` viram as coordenadas. `repeatUV` multiplica as UVs para repetir a imagem
  (piso: 8 × 4,5).
- Imagens: `concreto.png` (piso), `metal.png` (carroceria, tampa, painel), `caixa.png`
  (caixas), `listras.png` (faixas de sinalização). Todas geradas pelo script
  `tools/gerar_texturas.py` (ruído com numpy + desenhos com pygame): origem própria, sem
  imagens de terceiros.

---

## 8. Iluminação, materiais e normais

- **Luzes na cena** (`main.py`): `AmbientLight` (luz uniforme, evita preto total), uma
  `DirectionalLight` "sol" (raios paralelos, projeta as sombras) e uma direcional fraca de
  preenchimento vinda do lado oposto.
- **Lambert** (piso, faixas): ambiente + difusa. Difusa = `max(dot(normal, −direçãoDaLuz), 0)`:
  quanto mais a face encara a luz, mais clara.
- **Phong** (robô, caminhão, decoração): soma a especular =
  `specularStrength · max(dot(direçãoDoObservador, reflexo), 0)^shininess`. Depende de onde
  está a câmera (`viewPosition`); `shininess` alto = brilho pequeno e intenso (vidro, faróis).
- **Normais**: a caixa repete a mesma normal nos 6 vértices de cada face (arestas vivas, como
  nos slides 28–30). Nas superfícies paramétricas a normal vem do **produto vetorial** de duas
  tangentes (`n = u × v`, slide 35) em `ParametricGeometry`.
- **Matriz das normais**: no vertex shader, `transpose(inverse(mat3(modelMatrix))) * vertexNormal`
  mantém a normal perpendicular mesmo com escala (ex.: caixas escaladas).
- Cores acima de 1,0 (olhos, faróis, semáforo) dão aparência de "luz própria".

---

## 9. Shadow Mapping (seção 6.9 do livro)

Ideia: um ponto está na sombra se, olhando **a partir da luz**, existe algo mais próximo da
luz na mesma direção.

1. **Câmera da luz** (`light/shadow.py`): uma câmera **ortográfica** (raios paralelos, como a
   luz direcional) é filha da `DirectionalLight` e olha na direção dela. Cobre a plataforma
   (`cameraBounds = [-21, 21, -16, 16, 1, 60]`).
2. **1ª passada – mapa de profundidade** (`Renderer.render`): a cena é desenhada pela câmera
   da luz em um `RenderTarget` de 2048×2048 (framebuffer fora da tela) usando o
   `DepthMaterial`, que grava a profundidade de cada pixel (`gl_FragCoord.z`).
3. **2ª passada – cena normal**: no vertex shader cada vértice também é projetado pela câmera
   da luz (`shadowPosition0`). No fragment shader converte-se de [−1, 1] para [0, 1], lê-se a
   profundidade gravada no mapa e compara-se: se o pixel está mais longe da luz que o valor
   gravado (+ bias), está em sombra e sua cor é multiplicada por `1 − strength`.
4. O mapa é refeito **todo quadro**, por isso a sombra acompanha o caminhão, as rodas, a tampa
   e o robô em movimento, sempre na direção da luz.

Ajustes além do livro (bons para mostrar domínio):

| Ajuste | Problema que resolve |
|---|---|
| Profundidade codificada em 24 bits nos canais RGB (`packDepth`/`unpackDepth`) | com 8 bits a precisão é baixa e surgem manchas |
| Bias proporcional à inclinação | *shadow acne*: pontilhado de sombra na própria superfície |
| PCF 3×3 (média de 9 comparações) | borda da sombra serrilhada |
| `Mesh.castShadow = False` em lâmpadas | objetos "luminosos" não projetam sombra |

Diferença importante: **sombreamento** (lado escuro de um objeto, vem do `dot` da difusa) ≠
**sombra projetada** (um objeto escurecendo outro, vem do Shadow Mapping).

---

## 10. Requisitos da entrega × onde estão

| Exigência | Onde está |
|---|---|
| Código-fonte e componentes do framework | `core/`, `geometry/`, `material/`, `light/`, `extras/` + `models/`, `environment/`, `animation/`, `main.py` |
| Shaders | strings GLSL em `material/lambertMaterial.py`, `phongMaterial.py`, `depthMaterial.py` |
| Texturas e recursos | `assets/textures/` + `tools/gerar_texturas.py` |
| Arquivo de dependências | `requirements.txt` |
| README: integrantes e temas | seções 1 e 2 |
| README: cena e interação | seções 3 e 4 |
| README: instalação, execução, controles | seções 5, 6 e 7 |
| README: contribuições individuais | seção 12 (**preencher**) |
| README: fontes | seção 13 |
| README: arquivos/classes dos recursos gráficos | seção 9 |
| Declaração de uso de IA | seção 14 do README (**completar a revisão humana**) |

Critérios do projeto (70%): funcionamento, modelagem, integração, transformações, animação e
interação, controles, texturas, iluminação, sombras e documentação — todos cobertos acima.

---

## 11. Perguntas prováveis e respostas curtas

**O que é um atributo e o que é um uniform?**
Atributo muda a cada vértice (posição, UV, normal); uniform é igual para todos os vértices de
um desenho (matrizes, cor, luzes).

**Por que a matriz de visão é a inversa da câmera?**
A GPU não move a câmera: move o mundo no sentido oposto. A inversa leva as coordenadas do
mundo para o ponto de vista da câmera.

**Como o braço acompanha o robô?**
Ele é filho do tronco; a matriz de mundo do braço é a do tronco multiplicada pela local dele.

**Como a tampa gira na dobradiça e não no centro?**
Ela está dentro de um pivô posicionado na dobradiça e deslocada meia altura para baixo; o pivô
gira em Z.

**Como garantem que a animação não depende do FPS?**
Toda posição e ângulo é velocidade × `deltaTime`. Rodamos a 20 e 60 FPS e os tempos das etapas
foram iguais.

**Como a rotação das rodas fica coerente?**
`ângulo = distância percorrida / raio` (rolamento sem deslizar), aplicado no mesmo passo do
deslocamento.

**Onde está a interação entre os dois?**
Na máquina de estados: o robô só sai da base quando o caminhão para; a tampa só abre quando o
robô chega; o braço só se move com a tampa aberta; a tampa só fecha quando o robô recua; o
caminhão só parte com a tampa fechada.

**Por que câmera ortográfica na sombra?**
Luz direcional tem raios paralelos; projeção ortográfica também não converge.

**O que é shadow acne e como resolveram?**
A superfície sombreando a si mesma por falta de precisão. Resolvido com bias (maior em
superfícies inclinadas) e profundidade com 24 bits.

**Diferença entre Lambert e Phong?**
Lambert = ambiente + difusa (fosco). Phong soma a especular, que depende da posição do
observador (brilho).

**Para que servem as normais?**
Dizem para onde a superfície aponta; a difusa e a especular dependem delas.

**Por que a caixa tem vértices repetidos?**
Cada face precisa da sua própria normal; o mesmo canto pertence a três faces com normais
diferentes.

**Como a caixa passa do caminhão para a mão sem pular?**
`trocarPai`: guarda a matriz de mundo e calcula a local nova com a inversa da matriz do novo pai.

**Onde usam escala?**
No sinalizador do robô (pulsa durante o trabalho) e nas caixas decorativas (cubo unitário
escalado).

**Por que o PyOpenGL está com ERROR_CHECKING desligado?**
Desempenho: a verificação chama `glGetError` após cada função e consumia mais da metade do
tempo de cada quadro. Junto com o envio dos uniforms uma vez por material, o FPS subiu de cerca
de 10 para cerca de 58. Para depurar, basta voltar para `True`.

---


