# tests/test_voting_service.py
from src.services.voting_service import VotingService
from src.data.store import DataStore

def test_prevent_duplicate_vote():
    ds = DataStore()
    vs = VotingService(ds)
    voter = ds.create_voter(...)  # fixture
    assert vs.cast_vote(voter, poll_id=1, pos_id=1, cand_id=1)
    assert not vs.cast_vote(voter, poll_id=1, pos_id=1, cand_id=2)  # duplicate poll-pos
