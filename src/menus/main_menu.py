from src.helpers import *
from src.settings.Settings import Settings
from src.menus.download_and_extract import download_and_extract
from src.menus.compress_and_upload import compress_and_upload
from src.menus.exit_program import exit_program
from src.menus.create_new_project import create_new_project
from src.menus.open_project import open_project


## MAIN MENU
def main_menu():
    # Create default file structure if it doesnt exist
    mkdir("compressed_songs")
    mkdir("extracted_songs")
    mkdir("temp")
    mkdir("templates")

    Settings.create()

    clear_screen()
    display_title("What would you like to do?")

    menu_items = [
        ["Open Project",               open_project],
        ["Download & Extract Project", download_and_extract],
        ["Compress & Upload Project",  compress_and_upload],
        ["New Project",                create_new_project],
        ["Exit",                       exit_program],
    ]
    ans = list_options(menu_items)
    menu_items[ans][1](main_menu)

    main_menu()



# MAIN FUNCTION
if __name__ == '__main__':
    main_menu()




