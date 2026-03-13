class Admin:
    def __init__(self, id, username, password, full_name, email, role, created_at=""):
        self.id = id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email
        self.role = role
        self.created_at = created_at
        self.is_active = True
        
    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)
        obj.__dict__.update(d)
        return obj