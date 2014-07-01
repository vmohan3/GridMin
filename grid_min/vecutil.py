from vec import Vec

def list2vec(L):
    """Given a list L of field elements, return a Vec with domain {0...len(L)-1}
    whose entry i is L[i]
    """
    return Vec(set(range(len(L))), dict((k,L[k]) for k in range(len(L))))

def zero_vec(D):
    """Returns a zero vector with the given domain
    """
    return Vec(D, dict())
