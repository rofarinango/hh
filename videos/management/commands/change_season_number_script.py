from django.core.management.base import BaseCommand
from videos.models import Playlist
import re


class Command(BaseCommand):
    help = 'Update the season number for all playlists based on their titles'

    def handle(self, *args, **kwargs):
        # Retrieve all playlists from the database
        playlists = Playlist.objects.all()

        # Create a dictionary of playlist_id to title
        playlist_dict = {playlist.playlist_id: playlist.title for playlist in playlists}

        for playlist_id, title in playlist_dict.items():
            # Determine the season number from the title
            season_number = self.extract_season_number(title)

            if season_number:
                try:
                    playlist = Playlist.objects.get(playlist_id=playlist_id)
                    playlist.season_number = season_number
                    playlist.save()

                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully updated season number to {season_number} for playlist {playlist_id}.'))
                except Playlist.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Playlist with ID {playlist_id} does not exist.'))
            else:
                self.stdout.write(self.style.WARNING(
                    f'No season number found for playlist with ID {playlist_id} and title "{title}".'))

    def extract_season_number(self, title):
        # Extract the season number from titles like "Temporada X"
        match = re.search(r'Temporada (\d+)', title)
        if match:
            return int(match.group(1))
        return None
