from OpenGL.GL import *

from material.material import Material


# Modelo de Phong: componentes ambiente + difusa + especular (superfícies brilhantes).
# Suporta textura e recebimento de sombras (Shadow Mapping).
class PhongMaterial(Material):

    def __init__(self, texture=None, properties={}, useShadow=False):
        vertexShaderCode = """
        uniform mat4 projectionMatrix;
        uniform mat4 viewMatrix;
        uniform mat4 modelMatrix;

        // atributos de vértice
        in vec3 vertexPosition;
        in vec2 vertexUV;
        in vec3 vertexNormal;

        // dados enviados ao fragment shader (interpolados)
        out vec3 position;
        out vec2 UV;
        out vec3 normal;

        struct Shadow
        {
            vec3 lightDirection;
            mat4 projectionMatrix;
            mat4 viewMatrix;
            sampler2D depthTextureSampler;
            float strength;
            float bias;
        };
        uniform bool useShadow;
        uniform Shadow shadow0;
        out vec3 shadowPosition0;

        void main()
        {
            gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);

            // posição do vértice no mundo
            position = vec3(modelMatrix * vec4(vertexPosition, 1.0));
            UV = vertexUV;

            // matriz das normais: mantém a normal perpendicular à superfície
            // mesmo quando o objeto sofre escala
            normal = normalize(transpose(inverse(mat3(modelMatrix))) * vertexNormal);

            // posição do vértice no espaço de recorte da câmera da luz
            if (useShadow)
            {
                vec4 temp0 = shadow0.projectionMatrix * shadow0.viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
                shadowPosition0 = vec3(temp0);
            }
        }
        """

        fragmentShaderCode = """
        struct Light
        {
            int lightType;      // 1 = ambiente, 2 = direcional, 3 = pontual
            vec3 color;
            vec3 direction;
            vec3 position;
            vec3 attenuation;
        };
        uniform Light light0;
        uniform Light light1;
        uniform Light light2;
        uniform Light light3;

        uniform vec3 viewPosition;
        uniform float specularStrength;
        uniform float shininess;

        vec3 lightCalc(Light light, vec3 pointPosition, vec3 pointNormal)
        {
            float ambient = 0;
            float diffuse = 0;
            float specular = 0;
            float attenuation = 1;
            vec3 lightDirection = vec3(0, 0, 0);

            if (light.lightType == 1)           // luz ambiente
            {
                ambient = 1;
            }
            else if (light.lightType == 2)      // luz direcional
            {
                lightDirection = normalize(light.direction);
            }
            else if (light.lightType == 3)      // luz pontual
            {
                lightDirection = normalize(pointPosition - light.position);
                float distance = length(light.position - pointPosition);
                attenuation = 1.0 / (light.attenuation[0]
                                     + light.attenuation[1] * distance
                                     + light.attenuation[2] * distance * distance);
            }

            if (light.lightType > 1)
            {
                // difusa: proporcional ao cosseno entre a normal e a direção da luz
                pointNormal = normalize(pointNormal);
                diffuse = max(dot(pointNormal, -lightDirection), 0.0);
                diffuse *= attenuation;

                // especular: brilho que depende da posição do observador
                if (diffuse > 0)
                {
                    vec3 viewDirection = normalize(viewPosition - pointPosition);
                    vec3 reflectDirection = reflect(lightDirection, pointNormal);
                    specular = max(dot(viewDirection, reflectDirection), 0.0);
                    specular = specularStrength * pow(specular, shininess);
                }
            }

            return light.color * (ambient + diffuse + specular);
        }

        uniform vec3 baseColor;
        uniform bool useTexture;
        uniform sampler2D textureSampler;
        uniform vec2 repeatUV;

        in vec3 position;
        in vec2 UV;
        in vec3 normal;
        out vec4 fragColor;

        struct Shadow
        {
            vec3 lightDirection;
            mat4 projectionMatrix;
            mat4 viewMatrix;
            sampler2D depthTextureSampler;
            float strength;
            float bias;
        };
        uniform bool useShadow;
        uniform Shadow shadow0;
        in vec3 shadowPosition0;

        // decodifica a profundidade gravada pelo DepthMaterial
        float unpackDepth(vec3 color)
        {
            return dot(color, vec3(1.0, 1.0 / 255.0, 1.0 / 65025.0));
        }

        void main()
        {
            vec4 color = vec4(baseColor, 1.0);
            if (useTexture)
                color *= texture(textureSampler, UV * repeatUV);

            // soma a contribuição de todas as luzes
            vec3 total = vec3(0, 0, 0);
            total += lightCalc(light0, position, normal);
            total += lightCalc(light1, position, normal);
            total += lightCalc(light2, position, normal);
            total += lightCalc(light3, position, normal);
            color *= vec4(total, 1);

            if (useShadow)
            {
                // converte de [-1, 1] para [0, 1] (coordenadas de textura e profundidade)
                vec3 shadowCoord = (shadowPosition0.xyz + 1.0) / 2.0;

                // apenas superfícies voltadas para a luz recebem sombra projetada
                float cosAngle = dot(normalize(normal), -normalize(shadow0.lightDirection));
                bool facingLight = (cosAngle > 0.01);

                bool insideMap = shadowCoord.x > 0.0 && shadowCoord.x < 1.0 &&
                                 shadowCoord.y > 0.0 && shadowCoord.y < 1.0 &&
                                 shadowCoord.z < 1.0;

                if (facingLight && insideMap)
                {
                    // PCF 3x3: média de 9 comparações suaviza a borda da sombra
                    vec2 texel = 1.0 / vec2(textureSize(shadow0.depthTextureSampler, 0));
                    float fragmentDistanceToLight = shadowCoord.z;
                    float shadowAmount = 0.0;
                    // bias proporcional à inclinação: superfícies quase paralelas
                    // aos raios de luz precisam de mais tolerância
                    float tanAngle = sqrt(1.0 - cosAngle * cosAngle) / cosAngle;
                    float bias = shadow0.bias * clamp(tanAngle, 1.0, 8.0);
                    for (int x = -1; x <= 1; x++)
                    {
                        for (int y = -1; y <= 1; y++)
                        {
                            vec3 depthColor = texture(shadow0.depthTextureSampler,
                                                      shadowCoord.xy + vec2(x, y) * texel).rgb;
                            float closestDistanceToLight = unpackDepth(depthColor);
                            // o fragmento está em sombra se há algo mais próximo da luz
                            if (fragmentDistanceToLight > closestDistanceToLight + bias)
                                shadowAmount += 1.0;
                        }
                    }
                    shadowAmount /= 9.0;
                    float s = 1.0 - shadow0.strength * shadowAmount;
                    color *= vec4(s, s, s, 1);
                }
            }

            fragColor = color;
        }
        """

        super().__init__(vertexShaderCode, fragmentShaderCode)

        self.addUniform("vec3", "baseColor", [1.0, 1.0, 1.0])
        self.addUniform("Light", "light0", None)
        self.addUniform("Light", "light1", None)
        self.addUniform("Light", "light2", None)
        self.addUniform("Light", "light3", None)

        # posição da câmera e parâmetros do brilho especular
        self.addUniform("vec3", "viewPosition", [0, 0, 0])
        self.addUniform("float", "specularStrength", 1.0)
        self.addUniform("float", "shininess", 32.0)

        # quantas vezes a textura se repete em U e V
        self.addUniform("vec2", "repeatUV", [1.0, 1.0])

        if texture is None:
            self.addUniform("bool", "useTexture", False)
        else:
            self.addUniform("bool", "useTexture", True)
            self.addUniform("sampler2D", "textureSampler", [texture.textureRef, 1])

        if useShadow:
            self.addUniform("bool", "useShadow", True)
            self.addUniform("Shadow", "shadow0", None)
        else:
            self.addUniform("bool", "useShadow", False)

        self.locateUniforms()

        # renderiza os dois lados dos triângulos
        self.settings["doubleSide"] = True
        # renderiza apenas as arestas
        self.settings["wireframe"] = False

        self.setProperties(properties)

    def updateRenderSettings(self):
        if self.settings["doubleSide"]:
            glDisable(GL_CULL_FACE)
        else:
            glEnable(GL_CULL_FACE)

        if self.settings["wireframe"]:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
