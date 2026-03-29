import pandas as pd      
SAMPLE_SIZE = 1500 # total songs to keep 
AUDIO_FEATURES = ["danceability", "energy", "loudness", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo"]

def main():
    df = pd.read_csv("data/spotify.csv")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    rename = {"artists": "track_artist", "album_name": "track_album_name"}
    df = df.rename(columns={k: v for k, v in rename.items() if k in df.columns})
    df = df.drop(columns=[c for c in df.columns if c.startswith("unnamed")], errors="ignore")
    print("Columns:", df.columns.tolist())

    # drop rows missing audio features
    required_cols = AUDIO_FEATURES + ["track_name", "track_artist"]
    df = df.dropna(subset=required_cols)

    # separate strokes and regina songs (must-keep)
    strokes  = df[df["track_artist"].str.contains("The Strokes",   case=False, na=False)]
    regina   = df[df["track_artist"].str.contains("Regina Spektor", case=False, na=False)]
    must_keep = pd.concat([strokes, regina]).drop_duplicates()
    print(f"Strokes songs:  {len(strokes)}")
    print(f"Regina songs:   {len(regina)}")

    # random sample from the rest to fill up to SAMPLE_SIZE
    rest = df[~df.index.isin(must_keep.index)]
    n_random = max(0, SAMPLE_SIZE - len(must_keep))
    random_sample = rest.sample(n=min(n_random, len(rest)), random_state=42)

    # combine must-keep and random sample
    sampled = pd.concat([must_keep, random_sample]).reset_index(drop=True)
    sampled["song_id"] = sampled.index  # integer ID for each song
    print(f"sample size: {len(sampled)} songs")
    sampled.to_csv("data/sampled_songs.csv", index=False)

if __name__ == "__main__":
    main()