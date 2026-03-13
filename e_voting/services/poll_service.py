"""
PollService — Business logic for poll and position management.

This service manages the full lifecycle of elections:
  - Position CRUD (elective offices like President, Governor)
  - Poll CRUD (elections that group positions together)
  - Poll state transitions: draft → open → closed (→ reopened)
  - Candidate assignment to positions within polls
  - Eligibility filtering when assigning candidates

Positions and polls are managed together in one service because
they are tightly coupled — a poll always contains positions, and
positions are created primarily to be used in polls.
"""

import datetime

from e_voting.constants import MIN_CANDIDATE_AGE
from e_voting.models.poll import Poll, PollPosition
from e_voting.models.position import Position


class PollService:
    """Business logic for poll and position management."""

    def __init__(self, store):
        self._store = store

    # ══════════════════════════════════════════════════════════
    #  POSITION MANAGEMENT
    # ══════════════════════════════════════════════════════════

    def create_position(self, title, description, level, max_winners,
                        min_candidate_age, created_by):
        """Create a new elective position. Returns the Position object."""
        position_id = self._store.next_id("position")
        position = Position(
            position_id=position_id,
            title=title,
            description=description,
            level=level.capitalize(),
            max_winners=max_winners,
            min_candidate_age=min_candidate_age,
            created_by=created_by,
        )
        self._store.positions[position_id] = position
        self._store.log_action(
            "CREATE_POSITION", created_by,
            f"Created position: {title} (ID: {position_id})"
        )
        self._store.save()
        return position

    def get_all_positions(self):
        """Return all positions (active and inactive)."""
        return self._store.positions

    def get_active_positions(self):
        """Return only active positions (for use in poll creation)."""
        return {
            pid: p for pid, p in self._store.positions.items()
            if p.is_active
        }

    def update_position(self, position_id, updates, updated_by):
        """Apply field updates to a position. Returns updated Position or None."""
        position = self._store.positions.get(position_id)
        if not position:
            return None
        for key, value in updates.items():
            if value is not None and hasattr(position, key):
                setattr(position, key, value)
        self._store.log_action(
            "UPDATE_POSITION", updated_by,
            f"Updated position: {position.title}"
        )
        self._store.save()
        return position

    def can_deactivate_position(self, position_id):
        """Check whether a position can be deactivated.
        A position that is part of an open poll cannot be removed.
        Returns (can_delete: bool, reason: str or None)."""
        for poll in self._store.polls.values():
            if poll.is_open():
                for poll_pos in poll.positions:
                    if poll_pos.position_id == position_id:
                        return False, (
                            f"Cannot delete - in active poll: {poll.title}"
                        )
        return True, None

    def deactivate_position(self, position_id, deactivated_by):
        """Soft-delete a position. Returns True on success."""
        position = self._store.positions.get(position_id)
        if not position:
            return False
        position.deactivate()
        self._store.log_action(
            "DELETE_POSITION", deactivated_by,
            f"Deactivated position: {position.title}"
        )
        self._store.save()
        return True

    # ══════════════════════════════════════════════════════════
    #  POLL MANAGEMENT
    # ══════════════════════════════════════════════════════════

    def validate_poll_dates(self, start_date_str, end_date_str):
        """Validate that start and end dates are valid and in correct order.
        Returns (start_date, end_date, None) on success,
        or (None, None, error_message) on failure."""
        try:
            start = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            end = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
            if end <= start:
                return None, None, "End date must be after start date."
            return start, end, None
        except ValueError:
            return None, None, "Invalid date format."

    def create_poll(self, title, description, election_type, start_date,
                    end_date, position_ids, station_ids, created_by):
        """Create a new poll in DRAFT status with the selected positions
        and stations. Only active positions are included.
        Returns (poll, None) on success or (None, error_message) on failure."""
        # Build PollPosition objects from the selected position IDs
        poll_positions = []
        for pid in position_ids:
            position = self._store.positions.get(pid)
            if position and position.is_active:
                poll_positions.append(PollPosition(
                    position_id=pid,
                    position_title=position.title,
                    max_winners=position.max_winners,
                ))

        if not poll_positions:
            return None, "No valid positions selected."

        poll_id = self._store.next_id("poll")
        poll = Poll(
            poll_id=poll_id,
            title=title,
            description=description,
            election_type=election_type,
            start_date=start_date,
            end_date=end_date,
            positions=poll_positions,
            station_ids=station_ids,
            created_by=created_by,
        )
        self._store.polls[poll_id] = poll
        self._store.log_action(
            "CREATE_POLL", created_by,
            f"Created poll: {title} (ID: {poll_id})"
        )
        self._store.save()
        return poll, None

    def get_all_polls(self):
        """Return all polls regardless of status."""
        return self._store.polls

    def get_poll(self, poll_id):
        """Look up a single poll by ID."""
        return self._store.polls.get(poll_id)

    def update_poll(self, poll_id, updates, updated_by):
        """Update poll fields. Open polls and polls with votes cannot be edited.
        Returns (poll, None) on success or (None, error_message) on failure."""
        poll = self._store.polls.get(poll_id)
        if not poll:
            return None, "Poll not found."
        if poll.is_open():
            return None, "Cannot update an open poll. Close it first."
        if poll.is_closed() and poll.total_votes_cast > 0:
            return None, "Cannot update a poll with votes."
        for key, value in updates.items():
            if value is not None and hasattr(poll, key):
                setattr(poll, key, value)
        self._store.log_action(
            "UPDATE_POLL", updated_by,
            f"Updated poll: {poll.title}"
        )
        self._store.save()
        return poll, None

    def delete_poll(self, poll_id, deleted_by):
        """Permanently delete a poll and all associated vote records.
        Open polls cannot be deleted — they must be closed first.
        Returns None on success, or an error message string."""
        poll = self._store.polls.get(poll_id)
        if not poll:
            return "Poll not found."
        if poll.is_open():
            return "Cannot delete an open poll. Close it first."
        deleted_title = poll.title
        del self._store.polls[poll_id]
        # Also remove all votes associated with this poll
        self._store.votes = [
            v for v in self._store.votes if v.poll_id != poll_id
        ]
        self._store.log_action(
            "DELETE_POLL", deleted_by,
            f"Deleted poll: {deleted_title}"
        )
        self._store.save()
        return None

    # ── Poll State Transitions ───────────────────────────────

    def open_poll(self, poll_id, opened_by):
        """Transition poll from DRAFT to OPEN — voting begins.
        Requires at least one position to have candidates assigned."""
        poll = self._store.polls.get(poll_id)
        if not poll:
            return "Poll not found."
        if not poll.has_any_candidates():
            return "Cannot open - no candidates assigned."
        poll.open_poll()
        self._store.log_action(
            "OPEN_POLL", opened_by, f"Opened poll: {poll.title}"
        )
        self._store.save()
        return None

    def close_poll(self, poll_id, closed_by):
        """Transition poll from OPEN to CLOSED — voting ends."""
        poll = self._store.polls.get(poll_id)
        if not poll:
            return "Poll not found."
        poll.close_poll()
        self._store.log_action(
            "CLOSE_POLL", closed_by, f"Closed poll: {poll.title}"
        )
        self._store.save()
        return None

    def reopen_poll(self, poll_id, reopened_by):
        """Transition poll from CLOSED back to OPEN — resume voting."""
        poll = self._store.polls.get(poll_id)
        if not poll:
            return "Poll not found."
        poll.open_poll()
        self._store.log_action(
            "REOPEN_POLL", reopened_by, f"Reopened poll: {poll.title}"
        )
        self._store.save()
        return None

    # ── Candidate Assignment ─────────────────────────────────

    def assign_candidates_to_position(self, poll_id, position_index,
                                      candidate_ids, assigned_by):
        """Replace the candidate list for a specific position within a poll.
        Only candidates who meet the position's minimum age requirement
        and are active/approved are included.
        Returns the count of valid candidates assigned."""
        poll = self._store.polls.get(poll_id)
        if not poll or position_index >= len(poll.positions):
            return 0

        poll_pos = poll.positions[position_index]
        position = self._store.positions.get(poll_pos.position_id)
        min_age = (position.min_candidate_age if position
                   else MIN_CANDIDATE_AGE)

        # Filter to only eligible candidates
        valid_ids = []
        for cid in candidate_ids:
            candidate = self._store.candidates.get(cid)
            if candidate and candidate.is_eligible_for_position(min_age):
                valid_ids.append(cid)

        poll_pos.candidate_ids = valid_ids
        self._store.log_action(
            "ASSIGN_CANDIDATES", assigned_by,
            f"Updated candidates for poll: {poll.title}"
        )
        self._store.save()
        return len(valid_ids)

    def get_eligible_candidates(self, position_id):
        """Return all candidates who meet the eligibility criteria
        for the given position (active, approved, old enough)."""
        position = self._store.positions.get(position_id)
        min_age = (position.min_candidate_age if position
                   else MIN_CANDIDATE_AGE)
        return {
            cid: c for cid, c in self._store.candidates.items()
            if c.is_eligible_for_position(min_age)
        }
