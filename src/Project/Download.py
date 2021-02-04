from src.Drive import Drive
from src.TERMGUI.Log import Log


class Download:
    def download_project(self):
        Log("Downloading project..")

        # Download new cache
        if not Drive.download( self.entry.data["id"], self.get_cache_file() ):
            Log("An error occurred when trying to download the project..")
            Log.press_enter()
            # something went wrong while downloading
            return False

        # Update cache 'db.json' with new hash
