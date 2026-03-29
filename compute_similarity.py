import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# max euclidean distance to connect two songs (lower = more similar)
THRESHOLD  = 0.25
AUDIO_FEATURES = ["danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo"]

def main():
    df = pd.read_csv("data/sampled_songs.csv")
    # normalize audio features to [0, 1] so all features are on the same scale
    scaler = MinMaxScaler()
    feature_matrix = scaler.fit_transform(df[AUDIO_FEATURES].values)

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

    # make sure strokes songs have edges, shd remove later
    strokes_ids   = df[df["track_artist"].str.contains("The Strokes", case=False, na=False)]["song_id"]
    strokes_edges = pairs_df[pairs_df["song_id_a"].isin(strokes_ids) | pairs_df["song_id_b"].isin(strokes_ids)]
    print(f"Strokes songs have {len(strokes_edges)} edges")

if __name__ == "__main__":
    main()