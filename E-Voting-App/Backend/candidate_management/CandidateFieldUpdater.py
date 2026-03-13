from utils import prompt, info, warning, BOLD, RESET

class CandidateFieldUpdater:

    @staticmethod
    def CandidateFieldUpdater(candidate):

        print(f"\n  {BOLD}Updating: {candidate['full_name']}{RESET}")

        info("Press Enter to keep current value\n")

        new_name = prompt(f"Full Name [{candidate['full_name']}]: ")
        if new_name:
            candidate["full_name"] = new_name

        new_party = prompt(f"Party [{candidate['party']}]: ")
        if new_party:
            candidate["party"] = new_party

        new_manifesto = prompt(f"Manifesto [{candidate['manifesto'][:50]}...]: ")
        if new_manifesto:
            candidate["manifesto"] = new_manifesto

        new_phone = prompt(f"Phone [{candidate['phone']}]: ")
        if new_phone:
            candidate["phone"] = new_phone

        new_email = prompt(f"Email [{candidate['email']}]: ")
        if new_email:
            candidate["email"] = new_email

        new_address = prompt(f"Address [{candidate['address']}]: ")
        if new_address:
            candidate["address"] = new_address

        new_exp = prompt(f"Years Experience [{candidate['years_experience']}]: ")

        if new_exp:
            try:
                candidate["years_experience"] = int(new_exp)
            except ValueError:
                warning("Invalid number, keeping old value.")