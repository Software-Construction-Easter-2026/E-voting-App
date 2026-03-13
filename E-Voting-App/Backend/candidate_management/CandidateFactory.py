import datetime
import DataStore

class CandidateFactory:

    @staticmethod
    def create_CandidateFactory(
        candidate_id,
        full_name,
        national_id,
        dob_str,
        age,
        gender,
        education,
        party,
        manifesto,
        address,
        phone,
        email,
        years_experience
    ):

        return {
            "id": candidate_id,
            "full_name": full_name,
            "national_id": national_id,
            "date_of_birth": dob_str,
            "age": age,
            "gender": gender,
            "education": education,
            "party": party,
            "manifesto": manifesto,
            "address": address,
            "phone": phone,
            "email": email,
            "has_criminal_record": False,
            "years_experience": years_experience,
            "is_active": True,
            "is_approved": True,
            "created_at": str(datetime.datetime.now()),
            "created_by": DataStore.current_user["username"]
        }