import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from functools import partial
from sklearn.metrics.pairwise import cosine_similarity


def texts_encoder(texts):
    with tf.Graph().as_default():
        embed = hub.Module("https://tfhub.dev/google/nnlm-ja-dim128/1")
        embeddings = embed(texts)
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            sess.run(tf.tables_initializer())
            result = sess.run(embeddings)
    return result


def align(base, target, threshold=0.50):
    word_vectors = texts_encoder(base+target)
    base_vectors = word_vectors[:len(base)]
    target_vectors = word_vectors[len(base):]
    return solve(target, base_vectors, target_vectors, threshold)


def solve(target, base_vectors, target_vectors, threshold=0.50):
    similarities = cosine_similarity(base_vectors, target_vectors)
    results = []
    for similarity in similarities:
        if max(similarity) > threshold:
            results.append(target[np.argmax(similarity)])
        else:
            results.append(None)
    return results


def aligns(base, targets, threshold=0.50):
    ls = [len(base)] + [len(target) for target in targets]
    pt = 0

    data = base
    for target in targets:
        data += target
    
    word_vectors = texts_encoder(data)
    target_vectors = []
    for i, l in enumerate(ls):
        if i == 0:
            base_vector = word_vectors[:l]
        else:
            target_vectors.append(word_vectors[pt:pt+l])
        pt += l

    return [solve(target, base_vector, target_vector, threshold)
                 for target, target_vector in zip(targets, target_vectors)]


def sum_aligns(Bs):
    return np.sum(Bs, axis=0)


def W(A, Bs):
    A = np.array(A)
    tmp_W = []
    for B in Bs:
        tmp_W.append(A * B)
    return np.array(tmp_W)
    

def aligns2Bs(aligns):
    return [list(map(lambda x: x is not None, align)) for align in aligns]


def score(Ws):
    return np.sum(Ws, axis=1)


def execute(base_sentence, target_sentences, tokenize, stps, threshold=0.5):
    func = partial(fmt_sentence, tokenize=tokenize, stps=stps)
    base = func(base_sentence)
    targets = list(map(func, target_sentences))
    als = aligns(base, targets, threshold=threshold)
    Bs = aligns2Bs(als)
    A = sum_aligns(Bs)
    Ws = W(A, Bs).tolist()
    return score(Ws)


def fmt_sentence(sentence, tokenize, stps):
    return [term for term in tokenize(sentence).split() if term not in stps]
    
    

    
