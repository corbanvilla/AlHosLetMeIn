import numpy as np

def cosine_similarity(f1: np.ndarray, f2: np.ndarray) -> float:
    """
    Find cos(theta) between two angles.

    1 = Perfect match
    0 = Complete opposite

    cos(theta) = 1 means theta=0. If our angle is 0,
    it's the same point.

    Higher values = closer matches
    Lower values = further matches
    """

    # Calculate the dot product of our values
    dot_product = sum(v1 * v2 for v1, v2 in zip(f1, f2))

    # Calculate Frobenius norms
    f1_norm = sum([x ** 2 for x in f1]) ** (1 / 2)
    f2_norm = sum([x ** 2 for x in f2]) ** (1 / 2)

    # This is cos(theta):
    cos_theta = dot_product / (f1_norm * f2_norm)

    return cos_theta


def find_closest_face_match(profiles: list, f1: np.ndarray):
    dists = np.array([cosine_similarity(profile, f1) for profile in profiles.values()])
    closest_match = np.argmax(dists)
    profile_name = list(profiles)[closest_match]
    score = round(100 * dists[closest_match], 2)

    return profile_name, score
