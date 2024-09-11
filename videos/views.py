from django.shortcuts import render
from decouple import config
from googleapiclient.discovery import build
from videos.models import Playlist

api_key = config('API_KEY')
channel_id = config('CHANNEL_ID')
youtube = build('youtube', 'v3', developerKey=api_key)

def home(request):
    # Get banner image of channel

    channel_response = youtube.channels().list(part='brandingSettings', id=channel_id).execute()
    channel_settings = {
        'title': channel_response['items'][0]['brandingSettings']['channel']['title'],
        'banner': channel_response['items'][0]['brandingSettings']['image']['bannerExternalUrl'],
    }
    playlists = Playlist.objects.prefetch_related('episodes').order_by('season_number')

    seasons = {}
    for playlist in playlists:
        season_title = f'Temporada {playlist.season_number}'
        seasons[season_title] = {
            'episodes': [
                {
                    'title': episode.title,
                    'videoId': episode.video_id,
                    'duration': episode.duration,
                    'thumbnail': episode.thumbnail,
                }
                for episode in playlist.episodes.all()
            ]
        }

    first_season_key = next(iter(seasons))
    seasons.pop(first_season_key)
    second_season_key = next(iter(seasons))


    return render(
        request,
        'home.html',
        {
            'seasons': seasons,
            'channel_settings': channel_settings,
            'second_season_title': second_season_key,
            'default_season_title': 'Temporada 2',
        },
    )

def watch_episode(request, episode_id):
    return render(
        request,
        'videos/watch_episode.html',
        {
            'episode_id': episode_id,
        }
    )
