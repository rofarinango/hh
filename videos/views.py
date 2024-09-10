from django.shortcuts import render
from decouple import config
from googleapiclient.discovery import build
import re
import isodate
import random


api_key = config('API_KEY')
channel_id = config('CHANNEL_ID')
youtube = build('youtube', 'v3', developerKey=api_key)

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

def home(request):
    # Get banner image of channel

    channel_response = youtube.channels().list(part='brandingSettings', id=channel_id).execute()
    channel_settings = {
        'title': channel_response['items'][0]['brandingSettings']['channel']['title'],
        'banner': channel_response['items'][0]['brandingSettings']['image']['bannerExternalUrl'],
    }

    formatted_seasons = get_seasons_titles()
    seasons = {}

    # Construct seasons json, each item key represents one season, each value will contain all the episodes for that season.
    for key, value in formatted_seasons.items():
        episodes = get_episodes_from_playlist(key)

        # Collect all episodes for the current season
        seasons[value] = {
            'episodes': [
                {
                    'title': episode['title'],
                    'videoId': episode['videoId'],
                    'thumbnail': episode['thumbnail'],
                }
                for episode in episodes
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

def get_seasons_titles():
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

    return formatted_seasons

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
            episode = {
                'title': item['snippet']['title'],
                'videoId': item['snippet']['resourceId']['videoId'],
                'thumbnail': item['snippet']['thumbnails']['default']['url'] if 'thumbnails' in item['snippet'] and 'default' in item['snippet']['thumbnails'] else None,
            }
            episodes.append(episode)
        next_page_token = playlist_items.get('nextPageToken')
        if not next_page_token:
            break

    return extract_titles(episodes)


# Function to extract the season number from the title
def extract_season_number(title):
    for season_name, number in season_mapping.items():
        if season_name in title:
            return number
    return 0

# Function to format the title
def format_title(title):
    # Remove the "- Hablando Huevadas" part
    cleaned_title = re.sub(r' - Hablando Huevadas$', '', title)
    # Extract the season number
    season_number = extract_season_number(cleaned_title)
    # Format the title as "Temporada X"
    return f'Temporada {season_number}'

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