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
    # Generate grid coordinates
    x = np.linspace(0, 1, width, endpoint=False)
    y = np.linspace(0, 1, height, endpoint=False)
    X, Y = np.meshgrid(x, y)
    # Generate noise using Perlin algorithm
    noise = np.zeros((height, width))
    octaves = 6
    persistence = 0.5
    lacunarity = 2.0
    for i in range(octaves):
        freq = scale * (lacunarity ** i)
        amp = persistence ** i
        noise += amp * perlin_noise_2d(X * freq, Y * freq)
    # Normalize the noise to [0, 1]
    noise = (noise - np.min(noise)) / (np.max(noise) - np.min(noise))
    return noise

def perlin_noise_2d(x, y):
    """
    Generate 2D Perlin noise.
    :param x: X coordinates
    :param y: Y coordinates
    :return: 2D numpy array of Perlin noise
    """
    # Integer coordinates
    x0 = np.floor(x).astype(int)
    x1 = x0 + 1
    y0 = np.floor(y).astype(int)
    y1 = y0 + 1
    # Fractional coordinates
    tx = x - x0
    ty = y - y0
    # Smooth interpolation function (in this case, cubic)
    u = smoothstep(tx)
    v = smoothstep(ty)
    # Gradients at the integer coordinates
    gradients = np.random.randn(256, 2)
    g00 = gradients[hash(x0, y0) % 256]
    g01 = gradients[hash(x0, y1) % 256]
    g10 = gradients[hash(x1, y0) % 256]
    g11 = gradients[hash(x1, y1) % 256]
    # Vectors from the grid points to (x, y)
    dx00 = np.stack((tx, ty), axis=-1)
    dx01 = np.stack((tx, ty - 1), axis=-1)
    dx10 = np.stack((tx - 1, ty), axis=-1)
    dx11 = np.stack((tx - 1, ty - 1), axis=-1)
    # Dot products between gradients and vectors
    n00 = np.sum(g00 * dx00, axis=-1)
    n01 = np.sum(g01 * dx01, axis=-1)
    n10 = np.sum(g10 * dx10, axis=-1)
    n11 = np.sum(g11 * dx11, axis=-1)
    # Bicubic interpolation
    wx = cubic(u)
    nx0 = mix(n00, n10, wx)
    nx1 = mix(n01, n11, wx)
    wy = cubic(v)
    nxy = mix(nx0, nx1, wy)
    return nxy
def hash(x, y):
    """
    Pseudo-random hash function.
    :param x: X coordinate
    :param y: Y coordinate
    :return: Pseudo-random value
    """
    return (x * 1619 + y * 31337) % 65536
def mix(a, b, t):
    """
    Linear interpolation.
    :param a: Value 1
    :param b: Value 2
    :param t: Interpolation factor
    :return: Interpolated value
    """
    return a * (1 - t) + b * t
def smoothstep(t):
    """
    Smoothing function.
    :param t: Value to smooth
    :return: Smoothed value
    """
    return t * t * (3 - 2 * t)
def cubic(t):
    """
    Cubic interpolation.
    :param t: Value to interpolate
    :return: Interpolated value
    """
    return t * t * (3 - 2 * t)

if __name__ == "__main__":
    # Dimensions de la matrice de bruit de Perlin
    m = 100
    n = 200
    # Générer le bruit de Perlin
    l_weight = []
    l_scale = []
    n_scales = np.random.randint(4, 11)
    for i in range(n_scales):
        l_weight.append(np.random.random())
        l_scale.append(np.random.randint(1, 16))
    l_weight = np.array(l_weight)
    l_weight = l_weight/np.linalg.norm(l_weight)
    noise_matrix = np.zeros((m, n))
    for i in range(n_scales):
        noise_matrix += l_weight[i]*perlin_noise(n, m, scale=l_scale[i])
    # Affichage du bruit de Perlin
    plt.imshow(noise_matrix, cmap='gray', interpolation='nearest')
    plt.colorbar()
    plt.title('Bruit de Perlin 2D')
    plt.show()
