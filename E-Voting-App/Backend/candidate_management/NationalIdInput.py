from utils import Input, UI

class NationalIdInput:

    @staticmethod
    def get_NationalIdInput():
        national_id = Input.prompt("National ID: ")

        if not national_id:
            UI.error("National ID cannot be empty.")
            Input.pause()
            return None

        return national_id