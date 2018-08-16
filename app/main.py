import numpy as np

from utils.series import Series

data = np.load('sample_data.npy')
series = Series(data)
series.run()
