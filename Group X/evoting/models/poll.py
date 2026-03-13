class Poll:
    def __init__(self, id, title, description, election_type, start_date, end_date, positions, station_ids, created_by="", created_at=""):
        self.id = id
        self.title = title
        self.description = description
        self.election_type = election_type
        self.start_date = start_date
        self.end_date = end_date
        self.positions = positions
        self.station_ids = station_ids
        self.status = "draft"
        self.total_votes_cast = 0
        self.created_at = created_at
        self.created_by = created_by
        
    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)
        obj.__dict__.update(d)
        return obj