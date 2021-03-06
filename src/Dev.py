from src.TERMGUI.Log import Log
from src.FileManagement.File import File

# Definitions
FILEPATH = ".dev"

class Dev:

    def isDev():
        return Dev.get("DEVELOPMENT")

    def get(key):
        data = Dev._get_data()

        if key in data:

            if "DEVELOPMENT" in data and not data["DEVELOPMENT"]:
                return False

            if data[key] and key != "DEVELOPMENT":
                Log(f'Development Mode: {key}',"warning")
                Log.press_enter()

            return data[key]
        else:
            data[key] = False
            File.set_json(FILEPATH, data)
            return False

    # PRIVATE

    def _get_data():
        json_file = File.get_json(FILEPATH)

        if not json_file:
            json_file = { "DEVELOPMENT": False, }

            File.set_json(
                filepath = FILEPATH,
                data     = json_file
            )

        return json_file
