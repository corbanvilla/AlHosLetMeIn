import numpy as np
from numpy.linalg import norm


def compare_faces(f1, f2):

    def normalize(embedding):
        embedding_norm = norm(embedding)
        normed_embedding = embedding / embedding_norm
        return normed_embedding

    f1 = normalize(f1)
    f2 = normalize(f2)

    return (1. + np.dot(f1, f2)) / 2


def find_closest_match(profiles, f1):
    dists = np.array([compare_faces(profile, f1) for profile in profiles.values()])

    closest_match = np.argmax(dists)
    profile_name = list(profiles)[closest_match]
    score = round(100 * dists[closest_match], 2)

    return profile_name, score

