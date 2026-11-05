from material.material import Material


# Material usado na 1ª passada do Shadow Mapping:
# grava a profundidade do fragmento (vista pela câmera da luz) na textura
class DepthMaterial(Material):

    def __init__(self):
        vertexShaderCode = """
        in vec3 vertexPosition;
        uniform mat4 projectionMatrix;
        uniform mat4 viewMatrix;
        uniform mat4 modelMatrix;

        void main()
        {
            gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
        }
        """

        fragmentShaderCode = """
        out vec4 fragColor;

        // codifica a profundidade (0 a 1) em três canais de 8 bits,
        // obtendo 24 bits de precisão em vez de apenas 8
        vec3 packDepth(float depth)
        {
            vec3 enc = fract(depth * vec3(1.0, 255.0, 65025.0));
            enc -= enc.yzz * vec3(1.0 / 255.0, 1.0 / 255.0, 0.0);
            return enc;
        }

        void main()
        {
            // gl_FragCoord.z: profundidade do fragmento no intervalo [0, 1]
            float z = min(gl_FragCoord.z, 0.999999);
            fragColor = vec4(packDepth(z), 1.0);
        }
        """

        super().__init__(vertexShaderCode, fragmentShaderCode)
        self.locateUniforms()
