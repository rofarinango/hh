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

class Command(BaseCommand):
    help = 'Fetch playlists and episodes from Youtube and store them in database'
    def handle(self, *args, **options):
        api_key = config('API_KEY')
        channel_id = config('CHANNEL_ID')
        youtube = build('youtube', 'v3', developerKey=api_key)

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

