class Candidate: 
    MIN_AGE = 25
    MAX_AGE = 75
    EDUCATION_LEVELS = [
        "Bachelor's Degree", "Master's Degree", " PhD", "Directorate"
    ]
    
    def __init__(self, id, full_name, national_id, date_of_birth, age, gender, education, party, manifesto, address, phone, email, years_experience, created_by="", created_at=""):
        self.id = id
        self.full_name = full_name
        self.national_id = national_id
        self.date_of_birth = date_of_birth
        self.age =  age
        self.gender = gender
        self.education = education
        self.party = party
        self.manifesto =  manifesto
        self.address = address
        self.phone = phone
        self.email = email
        self.years_experience = years_experience
        self.has_criminal_record = False
        self.is_active = True
        self.is_approved = True
        self.created_at = created_at
        self.created_by = created_by
        
    def to_dict(self):
        return self.__dict__
    
    @classmethod
    def from_dict(cls, d):
        obj = cls.__new__(cls)
        obj.__dict__.update(d)
        return obj