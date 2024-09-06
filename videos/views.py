from django.shortcuts import render
from decouple import config
from django.http import JsonResponse
from googleapiclient.discovery import build


api_key = config('API_KEY')
channel_id = config('CHANNEL_ID')
youtube = build('youtube', 'v3', developerKey=api_key)
def home(request):
    # Get banner image of channel

    channel_response = youtube.channels().list(part='brandingSettings', id=channel_id).execute()
    print(channel_response)
    channel_settings = {
        'title': channel_response['items'][0]['brandingSettings']['channel']['title'],
        'banner': channel_response['items'][0]['brandingSettings']['image']['bannerExternalUrl'],
    }

    print(channel_settings)
    playlist_ids = []
    playlist_response = youtube.playlists().list(
        part="id",
        channelId=channel_id,
        maxResults=25
    ).execute()

    # Check if playlists exists in channel
    if playlist_response['items']:
        # Get the playlists ids
        for playlist in playlist_response['items']:
            playlist_id = playlist['id']
            playlist_ids.append(playlist_id)

    print(playlist_ids)
    videos = []
    next_page_token = None

    while True:
        # Call the playlistItems.list method to get videos
        playlist_items = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_ids[0],
            pageToken=next_page_token
        ).execute()

        # Extract video details from the response
        for item in playlist_items['items']:
            video = {
                'title': item['snippet']['title'],
                'videoId': item['snippet']['resourceId']['videoId'],
                'description': item['snippet']['description'],

            }
            videos.append(video)
        next_page_token = playlist_items.get('nextPageToken')

        # If no more pages are left, break the loop
        if not next_page_token:
            break

    return render(
        request,
        'home.html',
        {'video': videos[0], 'channel_settings': channel_settings},
    )

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
                'description': item['snippet']['description'],
                'thumbnail': item['snippet']['thumbnails']['default']['url'],
            }
            episodes.append(episode)
        next_page_token = playlist_items.get('nextPageToken')
        if not next_page_token:
            break

    return episodes
