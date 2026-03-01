from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    institution = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Researcher(Base):
    __tablename__ = 'researchers'
    id = Column(String, primary_key=True) # snake_case ID
    name = Column(String, nullable=False)
    institution = Column(String)
    role = Column(String) # Pionero, Formador, Investigador, Becario
    notes = Column(Text)
    activity_start = Column(Integer) # Decade (e.g., 1960)
    activity_end = Column(Integer) # Decade (e.g., 2020)
    is_phd_in_progress = Column(Boolean, default=False)
    photo_url = Column(String) # URL to researcher photo
    scholar_url = Column(String) # Google Scholar profile URL
    researchgate_url = Column(String) # ResearchGate profile URL
    orcid_url = Column(String) # ORCID profile URL
    keywords = Column(Text) # Comma-separated keywords (up to 10)
    gender = Column(String, default="Desconocido")
    province = Column(String)
    city = Column(String)
    verified = Column(Boolean, default=False)
    
    # Audit
    created_by = Column(Integer, ForeignKey('users.id'))
    last_edited_by = Column(Integer, ForeignKey('users.id'))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    students_rel = relationship("Relationship", foreign_keys="[Relationship.director_id]", back_populates="director")
    directors_rel = relationship("Relationship", foreign_keys="[Relationship.student_id]", back_populates="student")
    publications = relationship("Publication", back_populates="researcher", cascade="all, delete-orphan")

class Publication(Base):
    __tablename__ = 'publications'
    id = Column(Integer, primary_key=True)
    researcher_id = Column(String, ForeignKey('researchers.id'), nullable=False)
    title = Column(Text, nullable=False)
    year = Column(Integer)
    journal = Column(String)
    citation_count = Column(Integer)
    url = Column(String)
    
    researcher = relationship("Researcher", back_populates="publications")

class Relationship(Base):
    __tablename__ = 'relationships'
    id = Column(Integer, primary_key=True)
    student_id = Column(String, ForeignKey('researchers.id'), nullable=False)
    director_id = Column(String, ForeignKey('researchers.id'), nullable=False)
    type = Column(String, default="Primary") # Primary (Thesis), Secondary (Co-direction/Mentor)
    verified = Column(Boolean, default=False)
    
    student = relationship("Researcher", foreign_keys=[student_id], back_populates="directors_rel")
    director = relationship("Researcher", foreign_keys=[director_id], back_populates="students_rel")

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action = Column(String, nullable=False) # CREATE, UPDATE, DELETE
    target_type = Column(String) # Researcher, Relationship
    target_id = Column(String)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
class Suggestion(Base):
    __tablename__ = 'suggestions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    target_type = Column(String) # Researcher, Relationship
    target_id = Column(String)
    suggested_changes = Column(Text) # JSON or text description
    status = Column(String, default="Pending") # Pending, Approved, Rejected
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="suggestions")


# Database Setup
engine = create_engine('sqlite:///genealogy.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
