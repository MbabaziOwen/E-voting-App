class Voter:
    MIN_AGE = 18
    
    def __init__(self, id, full_name, national_id, date_of_birth, age, gender, address, phone, email, password, voter_card_number, station_id, registered_at=""):
        self.id = id
        self.full_name = full_name
        self.national_id = national_id
        self.date_of_birth = date_of_birth
        self.age = age
        self.gender = gender
        self.address = address
        self.phone = phone
        self.email = email
        self.password = password
        self.voter_card_number = voter_card_number
        self.station_id = station_id
        self.is_verified = False
        self.is_active = True
        self.has_voted_in = []
        self.registered_at = registered_at
        self.role = "voter"
        
    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)
        obj.__dict__.update(d)
        return obj