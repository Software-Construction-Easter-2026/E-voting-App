from utils import pause, error
import DataStore

class CandidateActivePollValidator:

    @staticmethod
    def validate(cid):

        for pid, poll in DataStore.polls.items():

            if poll["status"] == "open":

                for pos in poll.get("positions", []):

                    if cid in pos.get("candidate_ids", []):

                        error(f"Cannot delete - candidate is in active poll: {poll['title']}")
                        pause()
                        return False

        return True