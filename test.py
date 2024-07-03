import numpy as np
import matplotlib.pyplot as plt

def perlin_noise(width, height, scale=100):
    """
    Generate 2D Perlin noise using numpy.
    :param width: Width of the noise array
    :param height: Height of the noise array
    :param scale: Scale of the noise pattern
    :return: 2D numpy array of Perlin noise
    """
    x = np.linspace(0, 1, width, endpoint=False)
    y = np.linspace(0, 1, height, endpoint=False)
    X, Y = np.meshgrid(x, y)
    noise = np.zeros((height, width))
    octaves = 6
    persistence = 0.5
    lacunarity = 2.0
    
    for i in range(octaves):
        freq = scale * (lacunarity ** i)
        amp = persistence ** i
        noise += amp * perlin_noise_2d(X * freq, Y * freq)
    
    noise = (noise - np.min(noise)) / (np.max(noise) - np.min(noise))
    return noise

def perlin_noise_2d(x, y):
    x0 = np.floor(x).astype(int)
    x1 = x0 + 1
    y0 = np.floor(y).astype(int)
    y1 = y0 + 1
    
    tx = x - x0
    ty = y - y0
    
    u = smoothstep(tx)
    v = smoothstep(ty)
    
    gradients = np.random.randn(256, 2)
    
    def gradient(h, x, y):
        vectors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
        g = vectors[h % 4]
        return g[:, :, 0] * x + g[:, :, 1] * y

    g00 = gradient(hash(x0, y0), tx, ty)
    g10 = gradient(hash(x1, y0), tx - 1, ty)
    g01 = gradient(hash(x0, y1), tx, ty - 1)
    g11 = gradient(hash(x1, y1), tx - 1, ty - 1)
    
    nx0 = mix(g00, g10, u)
    nx1 = mix(g01, g11, u)
    nxy = mix(nx0, nx1, v)
    
    return nxy

def hash(x, y):
    return (x * 1619 + y * 31337) & 0xFFFFFFFF

def mix(a, b, t):
    return a * (1 - t) + b * t

def smoothstep(t):
    return t * t * (3 - 2 * t)

if __name__ == "__main__":
    m, n = 100, 200
    
    l_weight = []
    l_scale = []
    n_scales = np.random.randint(4, 11)
    
    for i in range(n_scales):
        l_weight.append(np.random.random())
        l_scale.append(np.random.randint(1, 16))
    
    l_weight = np.array(l_weight)
    l_weight = l_weight / np.linalg.norm(l_weight)
    noise_matrix = np.zeros((m, n))
    
    for i in range(n_scales):
        noise_matrix += l_weight[i] * perlin_noise(n, m, scale=l_scale[i])
    
    plt.imshow(noise_matrix, cmap='gray', interpolation='nearest')
    plt.colorbar()
    plt.title('Bruit de Perlin 2D')
    plt.show()
