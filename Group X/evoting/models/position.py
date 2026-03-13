class Position:
    def __init__(self, id, title, description, level, max_winners, min_candidate_age=25, created_by="", created_at=""):
        self.id = id
        self.title = title
        self.description = description
        self.level = level
        self.max_winners = max_winners
        self.min_candidate_age = min_candidate_age
        self.is_active = True
        self.created_at = created_at
        self.created_by = created_by
        
    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)
        obj.__dict__.update(d)
        return obj