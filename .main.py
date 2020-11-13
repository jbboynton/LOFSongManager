from src.Settings import Settings
from src.FileManagement.Folder import Folder
from src.menus.main_menu import main_menu

# MAIN FUNCTION
if __name__ == '__main__':

    # Create file structure if it doesn't exist
    Folder.create("compressed_songs")
    Folder.create("extracted_songs")
    Folder.create("temp")
    Folder.create("templates")

    # Create settings file if it doesn't exist
    Settings.create()

    # Start main menu
    main_menu()
