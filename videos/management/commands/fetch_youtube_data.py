from django.core.management.base import BaseCommand
from googleapiclient.discovery import build
from decouple import config
import re
import isodate
from videos.models import Playlist, Episode

season_mapping = {
    'Primera': 1,
    'Segunda': 2,
    'Tercera': 3,
    'Cuarta': 4,
    'Quinta': 5,
    'Sexta': 6,
    'Séptima': 7,
    'Octava': 8
}
api_key = config('API_KEY')
channel_id = config('CHANNEL_ID')
youtube = build('youtube', 'v3', developerKey=api_key)

class Command(BaseCommand):
    help = 'Fetch playlists and episodes from Youtube and store them in database'
    def handle(self, *args, **options):

        # Fetch playlists
        playlists_response = youtube.playlists().list(
            part='snippet, id',
            channelId=channel_id,
            maxResults=25,
        ).execute()

        playlist_ids = {}
        playlist_response = youtube.playlists().list(
            part="snippet,id",
            channelId=channel_id,
            maxResults=25
        ).execute()

        # Check if playlists exists in channel
        if playlist_response['items']:
            # Get the playlists ids
            for playlist in playlist_response['items']:
                if 'temporada' in playlist['snippet']['title'].lower():
                    playlist_id = playlist['id']
                    playlist_ids[playlist_id] = playlist['snippet']['title']

        sorted_seasons = dict(sorted(playlist_ids.items(), key=lambda item: extract_season_number(item[1])))
        formatted_seasons = {key: format_title(value) for key, value in sorted_seasons.items()}
        for playlist_id, title in formatted_seasons.items():
            playlist_obj, created = Playlist.objects.get_or_create(
                playlist_id=playlist_id,
                defaults={
                    'title': title,
                    'season_number': extract_season_number(title),
                }
            )
        seasons = {}
            # Construct seasons json, each item key represents one season, each value will contain all the episodes for that season.
        for key, value in formatted_seasons.items():
            episodes = get_episodes_from_playlist(key)

            # Collect all episodes for the current season
            seasons[key] = {
                'episodes': [
                    {
                        'title': episode['title'],
                        'videoId': episode['videoId'],
                        'total_minutes': episode['total_minutes'],
                        'thumbnail': episode['thumbnail'],
                    }
                    for episode in episodes
                ]
            }
        for playlist_id, episodes in seasons.items():
            for episode in episodes['episodes']:
                Episode.objects.get_or_create(
                    playlist=Playlist.objects.get(playlist_id=playlist_id),
                    video_id=episode['videoId'],
                    defaults={
                        'title': episode['title'],
                        'duration': episode['total_minutes'],
                        'thumbnail': episode['thumbnail'],
                    }
                )

        self.stdout.write(self.style.SUCCESS('Successfully fetched and stored YouTube data.'))


def format_title(title):
    # Remove the "- Hablando Huevadas" part
    cleaned_title = re.sub(r' - Hablando Huevadas$', '', title)
    # Extract the season number
    season_number = extract_season_number(cleaned_title)
    # Format the title as "Temporada X"
    return f'Temporada {season_number}'


def extract_season_number(title):
    for season_name, number in season_mapping.items():
        if season_name in title:
            return number
    return 0

def get_episodes_from_playlist(playlist_id):
    episodes = []
    next_page_token = None

    while True:
        playlist_items = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=5,
            pageToken=next_page_token
        ).execute()

        for item in playlist_items['items']:
            video_id = item['snippet']['resourceId']['videoId']
            total_minutes = get_video_total_minutes(video_id)
            episode = {
                'title': item['snippet']['title'],
                'videoId': video_id,
                'total_minutes': round(total_minutes),
                'thumbnail': item['snippet']['thumbnails']['default']['url'] if 'thumbnails' in item['snippet'] and 'default' in item['snippet']['thumbnails'] else None,
            }
            episodes.append(episode)
        next_page_token = playlist_items.get('nextPageToken')
        if not next_page_token:
            break

    return extract_titles(episodes)


def extract_titles(titles):
    modified_titles = []
    for title in titles:
        # Find all bracketed sections
        brackets = re.findall(r'\[(.*?)\]', title['title'])
        # Only include titles with brackets
        if brackets:
            # Join them with ' & ' if there are multiple, otherwise just take the single item
            new_title = ' & '.join(brackets)
            modified_titles.append({
                'title': new_title,
                'videoId': title['videoId'],
                'total_minutes': title['total_minutes'],
                'thumbnail': title['thumbnail']
            })
    return modified_titles


def get_video_total_minutes(video_id):
    video_response = youtube.videos().list(
        part="contentDetails",
        id=video_id,
    ).execute()

    total_minutes = (
        isodate.parse_duration(video_response['items'][0]['contentDetails']['duration']).total_seconds() / 60
        if 'items' in video_response and video_response['items']
        else 0)
    return total_minutes

