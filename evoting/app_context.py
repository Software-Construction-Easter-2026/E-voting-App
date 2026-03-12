class AppContext:
    def __init__(
        self,
        repo,
        auth,
        candidate_svc,
        station_svc,
        position_svc,
        poll_svc,
        voter_svc,
        admin_svc,
        vote_svc,
        results_svc,
    ):
        self.repo = repo
        self.auth = auth
        self.candidate_svc = candidate_svc
        self.station_svc = station_svc
        self.position_svc = position_svc
        self.poll_svc = poll_svc
        self.voter_svc = voter_svc
        self.admin_svc = admin_svc
        self.vote_svc = vote_svc
        self.results_svc = results_svc
