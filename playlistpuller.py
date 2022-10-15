import spotipy
from ytmusicapi import YTMusic
import pandas

from spotipy.oauth2 import SpotifyOAuth

# Use personal account request headers to authenticate
ytapi = YTMusic(auth="headers_auth.json")

scope = "user-library-read"

# Client id and secret from a registered spotify dashboard/app
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id="", client_secret="", redirect_uri="http://localhost:8000"))


# Concatenates paginated playlist track results
def get_playlist_tracks(playlist_id=None, results=None):
    if not results:
        results = sp.playlist_items(playlist_id)

    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


# Searches youtube for the song + artist combo and returns the video id
def yt_search(row):
    res = ytapi.search(query=row["name"] + " " + row["artist_name"], filter="songs", limit=1)
    return res[0]["videoId"]


# Creates a yt playlist from a spotify tracklist
def create_yt_playlist(tracks, plname):
    print(plname)
    # Avoid empty tracks
    tracks = [t["track"] for t in tracks if t["track"]]
    print(len(tracks))

    df=pandas.DataFrame.from_records(tracks)
    df["artist_name"] = df["artists"].map(lambda artist : artist[0]["name"])
    df["album_name"] = df["album"].map(lambda album : album["name"])
    df["yt_id"] = df.apply(lambda row : yt_search(row), axis=1)

    df.to_csv(path_or_buf="%s.csv" % plname)
    ytapi.create_playlist(title=plname, description=plname, video_ids=df["yt_id"].tolist())


# Playlists
results = sp.current_user_playlists()

for i in range(0, len(results["items"])):
    plname = results["items"][i]["name"]
    numsongs = results["items"][i]["tracks"]["total"]
    #print(plname)
    #print(numsongs)

    tracks = get_playlist_tracks(playlist_id=results["items"][i]["id"])
    create_yt_playlist(tracks, plname)
    

# Liked Songs
liked = sp.current_user_saved_tracks()
liked = get_playlist_tracks(results=liked)

create_yt_playlist(liked, "Liked Songs")