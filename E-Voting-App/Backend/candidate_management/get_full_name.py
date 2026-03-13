from utils import Input, UI


def get_full_name():
    full_name = Input.prompt("Full Name: ")

    if not full_name:
        UI.error("Name cannot be empty.")
        Input.pause()
        return None

    return full_name