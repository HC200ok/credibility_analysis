import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import pandas as pd


def cossim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def texts_encoder(texts):
    with tf.Graph().as_default():
        embed = hub.Module("https://tfhub.dev/google/nnlm-ja-dim128-with-normalization/1")
        embeddings = embed(texts)
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            sess.run(tf.tables_initializer())
            result = sess.run(embeddings)
    return result


def similar_event(word_vectors, source_idx, range_idx, threshold=0.85):
    similar_events = []
    source_vector = word_vectors[source_idx]
    for i in range(range_idx[0], range_idx[0]+range_idx[1]):
        if cossim(source_vector, word_vectors[i]) > threshold:
            similar_events.append(i)
    return similar_events


def grouping_events(events, word_vectors, threshold=0.8):
    results = []
    current_group = []
    
    for i, e in enumerate(events):
        current_group.append(events[i])
        if i == len(events)-1:
            results.append(current_group)
            current_group = []
        else:        
            if cossim(word_vectors[events[i]], word_vectors[events[i+1]]) > threshold:
                current_group.append(events[i+1])
            else:
                results.append(current_group)
                current_group = []

    if current_group:
        results.append(current_group)
        
    return results


def compute_instances_and_chains(df, word_vectors, size=None, day_column="day_fixed", time_decay=30, 
                                 chain_threshold=0.8, grouping_threshold=0.87):
    all_events = []
    event_instances = []
    event_chains = []
    
    if size is None:
        size = df.shape[0]
    
    for i in range(size):
        if i%1000 == 0:
            print("{}".format(i*100/df.shape[0]))
        if i in all_events:
            continue
        after_week = df.iloc[i][day_column] + pd.DateOffset(time_decay)
        today = df.iloc[i][day_column]
        len_data = df[today <= df[day_column]][df[day_column] <= after_week].shape[0]
        events = similar_event(word_vectors, i, (i, len_data), threshold=chain_threshold)
        if events == []:
            continue
        grouped_events = grouping_events(events, word_vectors, threshold=grouping_threshold)
        event_instances += grouped_events
        event_chains.append(events)
        all_events += events
        all_events = list(set(all_events))
    return event_chains, event_instances


def regrouping(grouped_events, word_vectors, threshold=0.87):
    results = []
    all_events = []
    current_group = []
    for i, ge1 in enumerate(grouped_events):
        if i in all_events:
            continue
        current_group = []
        current_group += ge1
        for j, ge2 in enumerate(grouped_events[i+1:]):
            if i+j+1 in all_events:
                continue
            if cossim(word_vectors[ge1[0]], word_vectors[ge2[0]]) > threshold:
                current_group += ge2
                all_events += [i, i+j+1]
        results.append(list(set(current_group)))
    return results


def execute(df, word_vectors, size=None, day_column="day_fixed", time_decay=14, 
            chain_threshold=0.8, grouping_threshold=0.87, 
            regrouping_threshold=0.87, regrouping_level=1):

    event_chains, grouped_events = compute_instances_and_chains(
        df, word_vectors, size, day_column, time_decay, chain_threshold, grouping_threshold)

    regrouped_events = grouped_events
    for i in range(regrouping_level):
        regrouped_events = regrouping(regrouped_events, word_vectors, regrouping_threshold)
    
    return event_chains, regrouped_events

if __name__=="__main__":
    import MeCab

    df = pd.read_csv("../data/fixed_data.csv")
    df['day_fixed'] = pd.to_datetime(df['day_fixed'])

    tagger = MeCab.Tagger("-Owakati")

    def data_define(d, tokenize=tagger.parse, c1="title", c2="body", sep="。", size=1):
        return tokenize('。'.join([d[1][c1]] + d[1][c2].split(sep)[:size]))

    df['data'] = list(map(data_define, df.iterrows()))
    df = df[['title', 'data', 'day_fixed']].sort_values(by="day_fixed")
    word_vectors = texts_encoder(df['data'].tolist())
    chains, instances = execute(df, word_vectors, size=500, regrouping_level=1)

