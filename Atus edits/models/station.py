class VotingStation:
    def __init__(self, id, anme, location, region, capacity, supervisor, contact, opening_time, closing_time, created_by="", created_at=""):
        self.id = id
        self.name = self.name
        self.location = location
        self.region = region
        self.capacity = capacity
        self.supervisor = supervisor
        self.contact = contact
        self.opening_time = opening_time
        self.closing_time = closing_time
        self.is_active = True
        self.created_at = created_at
        self.created_by = created_by
        
    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls,d):
        obj = cls.__new__(cls)
        obj.__dict__.update(d)
        return obj