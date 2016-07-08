import random
from hashlib import sha384


def get_random_hash(alg=sha384):
     return alg(str(random.getrandbits(1024))).hexdigest()
