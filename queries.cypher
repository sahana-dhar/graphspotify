// hw5
// put songs_nodes.csv + song_pairs.csv in neo4j import folder first

// constraints + index 
// 1 
CREATE CONSTRAINT song_id_unique IF NOT EXISTS
FOR (s:Song) REQUIRE s.song_id IS UNIQUE;

// 2
CREATE INDEX song_artist_index IF NOT EXISTS
FOR (s:Song) ON (s.artist);

// load csvs into graph, only run this once per empty db!!!
// 3
LOAD CSV WITH HEADERS FROM 'file:///songs_nodes.csv' AS row
CREATE (:Song {
    song_id: toInteger(row.song_id),
    title: row.track_name,
    artist: row.track_artist,
    album: row.track_album_name,
    danceability: toFloat(row.danceability),
    energy: toFloat(row.energy),
    loudness: toFloat(row.loudness),
    speechiness: toFloat(row.speechiness),
    acousticness: toFloat(row.acousticness),
    instrumentalness: toFloat(row.instrumentalness),
    liveness: toFloat(row.liveness),
    valence: toFloat(row.valence),
    tempo: toFloat(row.tempo)
});

// 4
LOAD CSV WITH HEADERS FROM 'file:///song_pairs.csv' AS row
MATCH (a:Song {song_id: toInteger(row.song_id_a)})
MATCH (b:Song {song_id: toInteger(row.song_id_b)})
CREATE (a)-[:SIMILAR_TO {similarity: toFloat(row.similarity)}]->(b);

// 5
MATCH (n:Song) RETURN count(n) AS total_nodes;
// 6
MATCH ()-[r:SIMILAR_TO]->() RETURN count(r) AS total_edges;

// part 3: recommendation query
// similar songs to strokes/regina but not by them, top 5, show score
// TODO: add query below

