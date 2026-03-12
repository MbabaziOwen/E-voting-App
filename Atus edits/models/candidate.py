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
        