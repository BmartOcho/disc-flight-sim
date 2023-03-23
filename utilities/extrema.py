import numpy as np
from scipy.signal import argrelextrema

def find_extrema(x, y):
    # Find the indices of the local maxima and minima
    maxima_idx = argrelextrema(x, np.greater)[0]
    minima_idx = argrelextrema(x, np.less)[0]

    # Get the x and y values at the extrema
    maxima_x = x[maxima_idx]
    maxima_y = y[maxima_idx]
    minima_x = x[minima_idx]
    minima_y = y[minima_idx]

    # Combine the maxima and minima into a single array
    extrema_x = np.concatenate((maxima_x, minima_x))
    extrema_y = np.concatenate((maxima_y, minima_y))

    # Determine whether each extrema is a maximum or minimum
    is_maxima = np.zeros(len(extrema_x), dtype=bool)
    is_maxima[:len(maxima_x)] = True

    # Sort the extrema by x-value
    idx = np.argsort(extrema_x)
    extrema_x = extrema_x[idx]
    extrema_y = extrema_y[idx]
    is_maxima = is_maxima[idx]

    # Convert the boolean array to a list of strings
    extrema_type = ["arrow-left" if is_max else "arrow-right" for is_max in is_maxima]

    return extrema_x, extrema_y, extrema_type
