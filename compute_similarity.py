'''
compute_similarity: computes euclidean distance similarity scores of
    the sampled songs to a specific artist, including feature weighting
    based on expert opinions on music perception:
    (https://pmc.ncbi.nlm.nih.gov/articles/PMC5405345/#:~:text=Overall%2C%20the%20results%20of%20this,perception%20of%20short%20music%20clips.)

Contributors: Sahana Dhar (euclidean distance set-up) 
    and Anya Wild (feature weights)
'''

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# max euclidean distance to connect two songs (lower = more similar)
THRESHOLD  = 0.25
AUDIO_FEATURES = ["danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo"]
ARTIST = "The Strokes" ### replace for diff artists!

def main():
    df = pd.read_csv("data/sampled_songs.csv")
    # normalize audio features to [0, 1] so all features are on the same scale
    scaler = MinMaxScaler()
    feature_matrix = scaler.fit_transform(df[AUDIO_FEATURES].values)

    # add feature weighting before distance calculation!! -- we think improves recs
    # (based on experts "timbre (energy, acoustic), rhythm (tempo), harmony (valence)")
    WEIGHTS = np.array([
    1.,  # danceability
    2.5,  # energy -- more!
    1.,  # loudness
    .5,  # speechiness -- less
    2.5,  # acousticness -- more!
    1.,  # instrumentalness
    .5,  # liveness -- less
    1.5,  # valence -- little more
    2.,  # tempo -- litte more
    ])
    feature_matrix = feature_matrix * WEIGHTS

    # compute pairwise euclidean distance between all song pairs
    diff = feature_matrix[:, np.newaxis, :] - feature_matrix[np.newaxis, :, :]  
    dist_matrix = np.sqrt((diff ** 2).sum(axis=2))                               

    # upper triangle only to avoid duplicate pairs and self-loops
    rows, cols = np.triu_indices(len(df), k=1)
    distances  = dist_matrix[rows, cols]

    # keep  pairs below the distance threshold
    mask = distances <= THRESHOLD
    rows, cols, distances = rows[mask], cols[mask], distances[mask]

    # convert distance to similarity score (1 = identical, 0 = totally different)
    similarity = np.round(1 - (distances / distances.max()), 4)
    pairs_df = pd.DataFrame({
        "song_id_a":  df["song_id"].values[rows],
        "song_id_b":  df["song_id"].values[cols],
        "similarity": similarity})

    print(f"{len(pairs_df):,} edges below distance threshold {THRESHOLD}")

    # save node file
    node_cols = ["song_id", "track_name", "track_artist", "track_album_name"] + AUDIO_FEATURES
    node_cols = [c for c in node_cols if c in df.columns]
    df[node_cols].to_csv("data/songs_nodes.csv", index=False)

    # save edge file
    pairs_df.to_csv("data/song_pairs.csv", index=False)

    # make sure ARTIST songs have edges, shd remove later
    artist_ids   = df[df["track_artist"].str.contains(ARTIST, case=False, na=False)]["song_id"]
    artist_edges = pairs_df[pairs_df["song_id_a"].isin(artist_ids) | pairs_df["song_id_b"].isin(artist_ids)]
    print(f"{ARTIST} songs have {len(artist_edges)} edges")

if __name__ == "__main__":
    main()