from utils import header, ScreenHelper, THEME_ADMIN, success, save_data, info, pause
from CandidateListView import display_CandidateListView
from CandidateIdInput import CandidateIdInput
from CandidateExistenceValidator import exists
from CandidateActivePollValidator import validate
from  CandidateDeleteConfirmation import confirm
from CandidateDeactivator import deactivate
from CandidateDeleteLogger import log 

class DeleteCandidate:

    def execute(self):

        ScreenHelper.clear_screen()

        header("DELETE CANDIDATE", THEME_ADMIN)

        if not display_CandidateListView():
            return

        cid = CandidateIdInput()

        if cid is None:
            return

        if not exists(cid):
            return

        if not validate(cid):
            return

        if confirm(cid):

            deleted_name = deactivate(cid)

            log(cid, deleted_name)

            print()

            success(f"Candidate '{deleted_name}' has been deactivated.")

            save_data()

        else:

            info("Deletion cancelled.")

        pause()