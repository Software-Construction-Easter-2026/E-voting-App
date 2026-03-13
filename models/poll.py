"""
Poll model — Represents an election/poll and its lifecycle.

A poll goes through three states (state machine pattern):
    DRAFT  →  OPEN  →  CLOSED
              ↑          │
              └──────────┘  (can be reopened)

- DRAFT: Initial state. Candidates can be assigned, settings edited.
- OPEN:  Voting is active. No modifications allowed.
- CLOSED: Voting is finished. Results can be viewed. Can be reopened.

Each poll contains one or more PollPosition objects that link positions
to their assigned candidates for this specific election.
"""

import datetime

from e_voting.constants import POLL_STATUS_DRAFT, POLL_STATUS_OPEN, POLL_STATUS_CLOSED


class PollPosition:
    """Links a Position to a Poll with its assigned candidate list.

    This is a value object — it exists only within the context of a Poll
    and tracks which candidates are competing for a particular position
    in that specific election.

    Attributes:
        position_id: References the Position this entry represents.
        position_title: Denormalised title for display convenience.
        candidate_ids: List of Candidate IDs assigned to compete.
        max_winners: Number of seats/winners for this position.
    """

    def __init__(self, position_id, position_title, candidate_ids=None,
                 max_winners=1):
        self.position_id = position_id
        self.position_title = position_title
        self.candidate_ids = candidate_ids if candidate_ids is not None else []
        self.max_winners = max_winners

    def has_candidates(self):
        """A position must have at least one candidate before
        the poll can be opened for voting."""
        return bool(self.candidate_ids)

    def to_dict(self):
        """Serialise to a plain dictionary for JSON persistence."""
        return {
            "position_id": self.position_id,
            "position_title": self.position_title,
            "candidate_ids": self.candidate_ids,
            "max_winners": self.max_winners,
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a PollPosition from a stored dictionary."""
        return cls(
            position_id=data["position_id"],
            position_title=data["position_title"],
            candidate_ids=data.get("candidate_ids", []),
            max_winners=data.get("max_winners", 1),
        )


class Poll:
    """Domain entity for an election / poll.

    Attributes:
        id: Unique auto-incremented identifier.
        title: Human-readable name of the election.
        election_type: Category — "General", "Primary", "By-election", etc.
        start_date / end_date: Planned election period (YYYY-MM-DD strings).
        positions: List of PollPosition objects for this election.
        station_ids: Which voting stations participate in this poll.
        status: Current lifecycle state — "draft", "open", or "closed".
        total_votes_cast: Running counter incremented with each ballot.
    """

    DRAFT = POLL_STATUS_DRAFT
    OPEN = POLL_STATUS_OPEN
    CLOSED = POLL_STATUS_CLOSED

    def __init__(self, poll_id, title, description, election_type,
                 start_date, end_date, positions=None, station_ids=None,
                 status="draft", total_votes_cast=0,
                 created_at=None, created_by=None):
        self.id = poll_id
        self.title = title
        self.description = description
        self.election_type = election_type
        self.start_date = start_date
        self.end_date = end_date
        self.positions = positions or []
        self.station_ids = station_ids or []
        self.status = status
        self.total_votes_cast = total_votes_cast
        self.created_at = created_at or str(datetime.datetime.now())
        self.created_by = created_by

    # ── Status query methods ─────────────────────────────────

    def is_draft(self):
        """True if the poll has not yet been opened for voting."""
        return self.status == self.DRAFT

    def is_open(self):
        """True if voting is currently active."""
        return self.status == self.OPEN

    def is_closed(self):
        """True if voting has ended."""
        return self.status == self.CLOSED

    def has_any_candidates(self):
        """A poll cannot be opened unless at least one position
        has candidates assigned to it."""
        return any(pos.has_candidates() for pos in self.positions)

    # ── State transition methods ─────────────────────────────

    def open_poll(self):
        """Transition from DRAFT (or CLOSED) to OPEN — begins voting."""
        self.status = self.OPEN

    def close_poll(self):
        """Transition from OPEN to CLOSED — stops accepting votes."""
        self.status = self.CLOSED

    def record_vote(self):
        """Increment the running vote counter after a ballot is cast."""
        self.total_votes_cast += 1

    # ── Serialisation ────────────────────────────────────────

    def to_dict(self):
        """Serialise to a plain dictionary for JSON persistence.
        Nested PollPosition objects are also serialised."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "election_type": self.election_type,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "positions": [p.to_dict() for p in self.positions],
            "station_ids": self.station_ids,
            "status": self.status,
            "total_votes_cast": self.total_votes_cast,
            "created_at": self.created_at,
            "created_by": self.created_by,
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct a Poll instance from a stored dictionary.
        Also reconstructs the nested PollPosition list."""
        positions = [
            PollPosition.from_dict(p) for p in data.get("positions", [])
        ]
        return cls(
            poll_id=data["id"],
            title=data["title"],
            description=data["description"],
            election_type=data["election_type"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            positions=positions,
            station_ids=data.get("station_ids", []),
            status=data.get("status", POLL_STATUS_DRAFT),
            total_votes_cast=data.get("total_votes_cast", 0),  # noqa: default for missing field
            created_at=data.get("created_at"),
            created_by=data.get("created_by"),
        )