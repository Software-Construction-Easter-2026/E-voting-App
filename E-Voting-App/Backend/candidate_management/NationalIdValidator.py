import DataStore

class NationalIdValidator:

    @staticmethod
    def exists(national_id):
        for c in DataStore.candidates.values():
            if c["national_id"] == national_id:
                return True
        return False