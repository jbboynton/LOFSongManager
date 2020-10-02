from glob import glob
from pathlib import Path
from src.helpers import *
from src.Drive import Drive
from src.hashing import *
from src.env import LOFSM_DIR_HASH

def compress_and_upload(main_menu):
    # Get extracted project names and list them
    drive          = Drive()
    drive_projects = drive.ls(search=LOFSM_DIR_HASH)

    clear_screen()
    display_title("What project would you like to compress?")

    # Get extracted project names and list them
    projects     = get_folders("extracted_songs")
    project      = projects[ list_options([ x.name for x in projects ], back=main_menu) ]
    temp_project = Path(f"temp/{project.name}")
    comp_project = Path(f"compressed_songs/{project.name}.lof")

    local_original   = Path(f"{project}/{project.stem}_original.song")
    local_conflict   = Path(f"{project}/{project.stem}_yourversion.song")
    local_version    = Path(f"{project}/{project.stem}.song")
    download_version = Path(f"{temp_project}/{project.stem}.song")

    # Check remote to see if a project exists on the cloud
    yes_remote = check_remote_db(drive, comp_project.name)
    if yes_remote:
        # See if we have the latest project in the local cache
        if not compare_hash(drive, comp_project.name):
            # We can't upload if there is a newer version already up!
            print("")
            print(f':: A newer version exists on the cloud!')
            print(f'   You can not upload a project when your version is older!')
            print("")
            print(f'   You must download the new version from the cloud and')
            print(f'   merge the two projects before uploading.')
            print("")
            print(f'   Exiting..')
            pause()
            exit()

    # Make sure the temp file is cleared and make temp dir
    clear_temp()

    # Extract existing compressed project first if exists
    if comp_project.is_file():
        untar_file(comp_project, "temp")
    else:
        mkdir(temp_project)

    # If the compressed version is the same as the extracted version
    if yes_remote and local_version.exists() and download_version.exists() \
            and filecmp.cmp(local_version.absolute(), download_version.absolute()):
        print("")
        print(f':: You already have the most up-to-date')
        print(f'   compressed project for "{project.stem}"!')
        print("")
        print(f'   Continuing is not advisable!')
        print("")
        print("   Continue anyway?")
        if input("   (y/n): ") != 'y':
            return 0

    # Check to make sure there are no prior conflicts
    if local_conflict.exists():
        log("Warning: You still have existing conflicts!!")
        print("")
        print(f':: Project file "{local_conflict}" still exists.')
        print(f'   This gets created when there are conflicts between your local project')
        print(f'   and an updated project downloaded from the drive.  If these conflicts')
        print(f'   do not get resolved before you compress and upload, you will lose all')
        print(f'   your local changes!')
        print("")
        print(f'   If you have ALREADY resolved these conflicts, then type "yes"')
        print("")
        print(f'   If you have NOT yet resolved these conflicts, then type "no"')
        print("")
        if input("   (yes/no): ") == "yes":
            print(":: Are you definitely sure you want to erase your conflict file?")
            if input("   (yes/no): ") != "yes":
                log("Exiting...")
                pause()
                exit()
        else:
            log("Exiting...")
            pause()
            exit()

        local_conflict.unlink()

    remove_dummy_files(project)

    # Copy or convert files to temp dir
    for path in glob(f"{project}/*"):
        path = Path(path)

        # catch all *.song files but ignore all but the main *.song file
        if path.suffix == ".song":
            # We only want to compress the *.song file
            if path.name == local_version.name:
                recursive_overwrite(local_version.absolute(), download_version.absolute())
                recursive_overwrite(local_version.absolute(), local_original.absolute())
        elif path.name == "Media":
            wav_to_mp3(f"{project}/Media", f"{temp_project}/Media")
        elif path.name == "Bounces":
            wav_to_mp3(f"{project}/Bounces", f"{temp_project}/Bounces")
        elif path.name != "Cache" and path.suffix != ".autosave":
            recursive_overwrite(path.absolute(), f"{temp_project.absolute()}/{path.name}")
        else:
            pass
            # Cache folder gets re-generated when the project is opened by studio one
            # We don't need to compress the autosave files.
            # We also don't need to save the autosave history but we can do that later,
            #  The filesize isnt that expensive.

    create_dummy_files(project)

    tar_file(temp_project, comp_project)

    log(f"Uploading '{comp_project.name}' to the cloud..\n      Please be patient..")
    parent = drive.get_info(search=LOFSM_DIR_HASH)
    drive.update_or_upload(comp_project.absolute(), Drive.mimeType['zip'], parents=[parent['id']])

    set_local_hash_from_file(comp_project.name, comp_project.absolute())
    set_remote_hash_from_local(drive, comp_project.name)

    # Clean up after ourselves
    clear_temp()

    log("Compression Complete!")
    pause()
