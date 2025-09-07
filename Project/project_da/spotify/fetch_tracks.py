import os
import argparse
from typing import List, Dict
import pandas as pd
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from dotenv import load_dotenv
from utils import chunked, safe_sleep

load_dotenv()

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI', 'http://localhost:8888/callback')


def get_spotify(client_auth: bool = True, user_auth: bool = False) -> Spotify:
    if user_auth:
        scope = 'user-library-read playlist-read-private'
        auth_manager = SpotifyOAuth(scope=scope)
        return Spotify(auth_manager=auth_manager)
    if client_auth:
        auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        return Spotify(auth_manager=auth_manager)
    raise ValueError('Specify an auth method')


def fetch_playlist_tracks(sp: Spotify, playlist_id: str) -> List[Dict]:
    items = []
    limit = 100
    offset = 0
    while True:
        chunk = sp.playlist_items(playlist_id, limit=limit, offset=offset)['items']
        if not chunk:
            break
        items.extend(chunk)
        offset += len(chunk)
    tracks = []
    for it in items:
        track = it.get('track')
        if track and track.get('id'):
            track['added_at'] = it.get('added_at')
            tracks.append(track)
    return tracks


def fetch_saved_tracks(sp: Spotify) -> List[Dict]:
    items = []
    limit = 50
    offset = 0
    while True:
        page = sp.current_user_saved_tracks(limit=limit, offset=offset)
        if not page['items']:
            break
        items.extend(page['items'])
        offset += len(page['items'])
    tracks = []
    for it in items:
        track = it.get('track')
        if track and track.get('id'):
            track['added_at'] = it.get('added_at')
            tracks.append(track)
    return tracks


def fetch_artist_all_tracks(sp: Spotify, artist_id: str) -> List[Dict]:
    albums = []
    offset = 0
    limit = 50
    seen_albums = set()
    while True:
        res = sp.artist_albums(artist_id, limit=limit, offset=offset, album_type='album,single')
        items = res['items']
        if not items:
            break
        for a in items:
            if a['id'] not in seen_albums:
                albums.append(a)
                seen_albums.add(a['id'])
        offset += len(items)

    tracks = []
    for alb in albums:
        a_tracks = sp.album_tracks(alb['id'])['items']
        for t in a_tracks:
            if t.get('id'):
                tracks.append(t)
    return tracks


def fetch_search_tracks(sp: Spotify, query: str, market: str = None, max_results: int = 1000) -> List[Dict]:
    results = []
    limit = 50
    offset = 0

    while offset < max_results and offset < 1000:  # Spotify Search API 제한
        res = sp.search(q=query, type='track', market=market, limit=limit, offset=offset)
        items = res["tracks"]["items"]
        if not items:
            break
        results.extend(items)
        offset += limit
        if offset >= 1000:
            break

    return results


def enrich_tracks(sp: Spotify, tracks: List[Dict]) -> pd.DataFrame:
    track_map = {}
    for t in tracks:
        tid = t.get('id')
        if not tid:
            continue
        if tid not in track_map:
            track_map[tid] = t
    track_ids = list(track_map.keys())

    # fetch audio features in batches (max 100)
    audio_feats = {}
    for chunk in chunked(track_ids, 100):
        tries = 0
        while True:
            try:
                feats = sp.audio_features(chunk)
                break
            except Exception as e:
                tries += 1
                safe_sleep(tries)
        for f in feats:
            if f and f.get('id'):
                audio_feats[f['id']] = f

    # fetch track metadata in batches (max 50)
    meta_map = {}
    for chunk in chunked(track_ids, 50):
        tries = 0
        while True:
            try:
                metas = sp.tracks(chunk)
                break
            except Exception as e:
                tries += 1
                safe_sleep(tries)
        for tr in metas['tracks']:
            if tr and tr.get('id'):
                meta_map[tr['id']] = tr

    # fetch artist genres
    artist_ids = set()
    for tr in meta_map.values():
        for a in tr.get('artists', []):
            artist_ids.add(a['id'])
    artist_genres = {}
    for chunk in chunked(list(artist_ids), 50):
        tries = 0
        while True:
            try:
                res = sp.artists(chunk)
                break
            except Exception as e:
                tries += 1
                safe_sleep(tries)
        for art in res['artists']:
            artist_genres[art['id']] = art.get('genres', [])

    rows = []
    for tid in track_ids:
        meta = meta_map.get(tid, {})
        feat = audio_feats.get(tid, {})
        if not meta:
            continue
        artists = meta.get('artists', [])
        artist_names = [a['name'] for a in artists]
        artist_ids_list = [a['id'] for a in artists]
        genres = []
        for aid in artist_ids_list:
            genres.extend(artist_genres.get(aid, []))
        genres = list(set(genres))

        row = {
            'track_id': tid,
            'track_name': meta.get('name'),
            'artists': ';'.join(artist_names),
            'artist_ids': ';'.join([x for x in (artist_ids_list or []) if x]),
            'album_name': meta.get('album', {}).get('name'),
            'album_id': meta.get('album', {}).get('id'),
            'release_date': meta.get('album', {}).get('release_date'),
            'popularity': meta.get('popularity'),
            'duration_ms': meta.get('duration_ms'),
            'explicit': meta.get('explicit'),
            'track_url': meta.get('external_urls', {}).get('spotify'),
            'preview_url': meta.get('preview_url'),
            'genres': ';'.join(genres)
        }
        for k, v in (feat or {}).items():
            row[k] = v
        rows.append(row)

    df = pd.DataFrame(rows)
    expected_af = ['danceability','energy','key','loudness','mode','speechiness',
                   'acousticness','instrumentalness','liveness','valence','tempo','time_signature']
    for c in expected_af:
        if c not in df.columns:
            df[c] = None
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['search','playlist','artist','csv','saved'], required=True)
    parser.add_argument('--query', help='검색어 (search mode)')
    parser.add_argument('--playlist_id', help='playlist id (playlist mode)')
    parser.add_argument('--artist_id', help='artist id (artist mode)')
    parser.add_argument('--csv_file', help='csv 파일 (csv mode)')
    parser.add_argument('--out', default='outputs/tracks_dump.csv')
    parser.add_argument('--market', default=None)
    parser.add_argument('--user_auth', action='store_true', help='사용자의 saved tracks 접근을 위해 OAuth 사용')
    args = parser.parse_args()

    sp = get_spotify(client_auth=True, user_auth=args.user_auth)

    collected = []
    if args.mode == 'search':
        if not args.query:
            raise SystemExit('search 모드에서는 --query 가 필요합니다')
        collected = fetch_search_tracks(sp, args.query, market=args.market)
    elif args.mode == 'playlist':
        if not args.playlist_id:
            raise SystemExit('playlist 모드에서는 --playlist_id 가 필요합니다')
        collected = fetch_playlist_tracks(sp, args.playlist_id)
    elif args.mode == 'artist':
        if not args.artist_id:
            raise SystemExit('artist 모드에서는 --artist_id 가 필요합니다')
        collected = fetch_artist_all_tracks(sp, args.artist_id)
    elif args.mode == 'saved':
        if not args.user_auth:
            raise SystemExit('saved 모드에서는 --user_auth 옵션이 필요합니다')
        collected = fetch_saved_tracks(sp)
    elif args.mode == 'csv':
        if not args.csv_file:
            raise SystemExit('csv 모드에서는 --csv_file 이 필요합니다')
        df_in = pd.read_csv(args.csv_file)
        if 'track_id' in df_in.columns:
            ids = df_in['track_id'].dropna().astype(str).tolist()
            for i in ids:
                try:
                    t = sp.track(i)
                    collected.append(t)
                except Exception:
                    pass
        else:
            for name in df_in['track_name'].dropna().astype(str).tolist():
                res = sp.search(q=name, type='track', limit=1)
                items = res.get('tracks', {}).get('items', [])
                if items:
                    collected.append(items[0])

    print(f'Collected {len(collected)} raw track entries. Enriching...')
    df = enrich_tracks(sp, collected)
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f'Saved enriched tracks to {args.out} (rows: {len(df)})')


if __name__ == '__main__':
    main()
