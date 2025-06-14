import numpy as np
np.random.seed(42)
grid = np.random.randint(0, 2, size=(10, 10))
np.savetxt("random_input.txt", grid, fmt="%d", delimiter="")