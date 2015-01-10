import numpy as np

# epsilon for testing whether a number is close to zero
_EPS = np.finfo(float).eps * 4.0


def apply_matrix(mat, v):
    """Apply matrix *mat* to 3D vector v.

    """
    return np.dot(v, mat.T)


def apply_quaternion(quat, v):
    """Apply the rotation obtained from quaternion *quat* to 3D vector v.

    """
    return apply_matrix(quaternion_matrix(quat), v)


def random_quaternion(rand=None):
    """Return uniform random unit quaternion.

    rand: array like or None
        Three independent random variables that are uniformly distributed
        between 0 and 1.

    >>> q = random_quaternion()
    >>> np.allclose(1, vector_norm(q))
    True
    >>> q = random_quaternion(np.random.random(3))
    >>> len(q.shape), q.shape[0]==4
    (1, True)

    """
    if rand is None:
        rand = np.random.rand(3)
    else:
        assert len(rand) == 3
    r1 = np.sqrt(1.0 - rand[0])
    r2 = np.sqrt(rand[0])
    pi2 = np.pi * 2.0
    t1 = pi2 * rand[1]
    t2 = pi2 * rand[2]
    return np.array([np.cos(t2)*r2, np.sin(t1)*r1,
                     np.cos(t1)*r1, np.sin(t2)*r2])

def quaternion_matrix(quaternion):
    """Return homogeneous rotation matrix from quaternion.

    >>> M = quaternion_matrix([0.99810947, 0.06146124, 0, 0])
    >>> np.allclose(M, rotation_matrix(0.123, [1, 0, 0]))
    True
    >>> M = quaternion_matrix([1, 0, 0, 0])
    >>> np.allclose(M, np.identity(4))
    True
    >>> M = quaternion_matrix([0, 1, 0, 0])
    >>> np.allclose(M, np.diag([1, -1, -1, 1]))
    True

    """
    q = np.array(quaternion, dtype=np.float64, copy=True)
    n = np.dot(q, q)
    if n < _EPS:
        return np.identity(4)
    q *= np.sqrt(2.0 / n)
    q = np.outer(q, q)
    return np.array([
        [1.0-q[2, 2]-q[3, 3],     q[1, 2]-q[3, 0],     q[1, 3]+q[2, 0]],
        [    q[1, 2]+q[3, 0], 1.0-q[1, 1]-q[3, 3],     q[2, 3]-q[1, 0]],
        [    q[1, 3]-q[2, 0],     q[2, 3]+q[1, 0], 1.0-q[1, 1]-q[2, 2]]])

def cartesian_to_spherical(cartesian):
    """Convert cartesian to spherical coordinates passed as (N,3) shaped arrays."""
    xyz = cartesian
    xy = xyz[:,0]**2 + xyz[:,1]**2
    r = np.sqrt(xy + xyz[:,2]**2)
    phi = np.arctan2(np.sqrt(xy), xyz[:,2]) # for elevation angle defined from Z-axis down
    #ptsnew[:,4] = np.arctan2(xyz[:,2], np.sqrt(xy)) # for elevation angle defined from XY-plane up
    theta = np.arctan2(xyz[:,1], xyz[:,0])
    return np.array([r, theta, phi]).T
