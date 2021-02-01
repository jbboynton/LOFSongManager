from src.Tar import Tar
from src.dev import Dev
from src.Drive import Drive
from src.FileManagement.File import File
from src.FileManagement.Folder import Folder


class Compress:

    def compress_project(self):
        # Clean out temp project if it exists
        Log("Cleaning out temp folder")
        Folder.delete( self.get_temp_dir() )

        # Extract cache if it exists
        if self.is_cached():
            Tar.extract(
                filepath    = self.get_cache_file(),
                destination = self.get_temp_dir().parent
            )
        else:
            Folder.create( self.get_temp_dir() )

        # Create folders if they dont exist
        self.create_required_folders(temp=True)

        # Copy from 'extracted_songs' to 'temp'
        if not self.move_extracted_song_to_temp():
            Log("Could not move project from 'extracted_songs' to 'temp'..","warning")
            Log.press_enter()
            return False

        # Compress project to *.lof
        Tar.compress(
            folderpath  = self.get_temp_dir(),
            destination = self.get_cache_file()
        )

        return True

    def move_extracted_song_to_temp(self):
        for location in ["Media", "Bounces"]:

            # Remove unused cached audio from location
            # Garbage collector for unused audio files
            mp3s      = Folder.ls_files( self.get_temp_dir()/location, "mp3" )
            wav_names = [ x.stem for x in Folder.ls_files( self.get_root_dir()/location, "mp3" ) ]
            for mp3 in mp3s:
                if mp3.stem not in wav_names:
                    File.delete(mp3)

            # Convert and move wavs to mp3s
            Log(f'Converting "{location}" wav\'s to mp3\'s')
            if not Audio.folder_to_mp3( self.get_root_dir()/location, self.get_temp_dir()/location ):
                return False

            # Copy over dummy.json
            Log(f'Copying over "{location}" dummy.json')
            if self.get_dummy_db(location, temp=False).exists():
                File.recursive_overwrite(
                    self.get_dummy_db(location, temp=False),
                    self.get_dummy_db(location, temp=True),
                )

        # Upload scratch files and mixdowns
        mp3s = Folder.ls_files( self.get_temp_dir()/"Media", "mp3", "Scratch*" )
        mp3s.extend( Folder.ls_files( self.get_temp_dir()/"Media", "mp3", "SCRATCH*" ) )

        # NEED SOME WAY TO MERGE IN MIXDOWNS IN HERE TO NOT DUPLICATE CODE!
        mp3s.extend( Folder.ls_files( self.get_temp_dir()/"Mixdown", "mp3" ) )

        for mp3 in mp3s:
            mix_folder_id = Drive.get_id( self.entry.name )

            if not Drive.get_id( mp3.name, mix_folder_id ):
                Log(f'Uploading "{mp3.name}" to the cloud',"sub")
                mp3_id = Drive.upload(
                    filepath = mp3,
                    mimeType = Drive.mimeType["mp3"],
                    parents  = mix_folder_id
                )
                Slack.send_link(
                    link_name = f'Scratch for {self.entry.name}, "{mp3.name}"',
                    ID        = mp3_id
                )
            else:
                Log(f'Audio file "{mp3.name}" already exists on the cloud!',"sub")


    ## DIALOGS ##

    def dialog_remove_unused_audio_files(self):
        dialog = Dialog(
            title = "Remove Unused Audio Files",
            body  = [
                f'Studio One will open and allow you to remove',
                f'unused audio files from the pool.',
                f'\n',
                f'\n',
                f'DO NOT FORGET to check the box that says to ',
                f'"Delete Files Permanently"!',
                f'\n',
                f'\n',
                f'NOT Advised but... Press "n" at the next prompt',
                f'if you want to skip this.',
                f'\n',
                f'\n',
            ]
        )

        if dialog.get_mult_choice(["y","n"]) == "y":
            return True
        return False

    ## END DIALOGS ##
