from distances import distances_within
from distances import distance_matrix
from distances import overlapping_points


def fequal(a, b, tol):
    return (abs(a-b) / max(abs(a), abs(b))) < tol
