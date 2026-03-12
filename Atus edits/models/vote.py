class Vote:
    def __init__(self, vote_id, poll_id, position_id, candidate_id, voter_id, station_id, timestamp, abstained=False):
        self.vote_id = vote_id
        self.poll_id = poll_id
        self.position_id = position_id
        self.candidate_id = candidate_id
        self.voter_id = voter_id
        self.station_id = station_id
        self.timestamp = timestamp
        self.abstained = abstained
        
    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)
        obj.__dict__.update(d)
        return obj