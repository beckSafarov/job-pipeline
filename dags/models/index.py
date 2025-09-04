from sqlalchemy import (  # type: ignore
    Column,
    Integer,
    String,
    Text,
    Boolean,
    BigInteger,
    DateTime,
    ForeignKey,
    Float,
    Numeric,
    Identity,
)
from sqlalchemy.orm import relationship #type:ignore
from sqlalchemy.ext.declarative import declarative_base #type:ignore
from utils.db_utils import get_db_engine

Base = declarative_base()


class Area(Base):
    __tablename__ = "areas"

    area_id = Column(Numeric(4), primary_key=True)
    name = Column(Text)

    # Relationships
    jobs = relationship("Job", back_populates="area")

    def __repr__(self):
        return f"<Area(area_id={self.area_id}, name='{self.name}')>"


class Employer(Base):
    __tablename__ = "employer"

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    is_accredited = Column(Boolean)

    # Relationships
    jobs = relationship("Job", back_populates="employer")

    def __repr__(self):
        return f"<Employer(id={self.id}, name='{self.name}', is_accredited={self.is_accredited})>"


class Job(Base):
    __tablename__ = "job"

    id = Column(Integer, primary_key=True)
    source_id = Column(BigInteger)
    title = Column(Text, nullable=False)
    area_id = Column(Numeric(4), ForeignKey("areas.area_id"), nullable=False)
    employer_id = Column(
        Integer, ForeignKey("employer.id"), name="employer", nullable=False
    )
    schedule = Column(Text)
    work_format = Column(Text)
    working_hours = Column(Text)
    employment_form = Column(Text)
    experience = Column(String)
    is_internship = Column(Boolean)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)

    # Relationships
    area = relationship("Area", back_populates="jobs")
    employer = relationship("Employer", back_populates="jobs")
    address = relationship("Address", uselist=False, back_populates="job")
    languages = relationship("JobLanguage", back_populates="job")
    skills = relationship("JobSkill", back_populates="job")
    roles = relationship("JobRole", back_populates="job")
    salary = relationship("Salary", uselist=False, back_populates="job")

    def __repr__(self):
        return (
            f"<Job(id={self.id}, title='{self.title}', employer_id={self.employer_id})>"
        )


class Address(Base):
    __tablename__ = "address"

    job_id = Column(Integer, ForeignKey("job.id"), primary_key=True)
    lat = Column(Float)
    lng = Column(Float)
    city = Column(Text)
    street = Column(Text)
    building = Column(Text)

    # Relationships
    job = relationship("Job", back_populates="address")

    def __repr__(self):
        return f"<Address(job_id={self.job_id}, city='{self.city}')>"


class JobLanguage(Base):
    __tablename__ = "job_languages"

    job_id = Column(Integer, ForeignKey("job.id"), primary_key=True)
    lang_id = Column(Text, primary_key=True)
    lang_level = Column(Text)

    # Relationships
    job = relationship("Job", back_populates="languages")

    def __repr__(self):
        return f"<JobLanguage(job_id={self.job_id}, lang_id='{self.lang_id}', lang_level='{self.lang_level}')>"


class JobSkill(Base):
    __tablename__ = "job_skills"

    job_id = Column(Integer, ForeignKey("job.id"), primary_key=True)
    skill_name = Column(Text, primary_key=True)

    # Relationships
    job = relationship("Job", back_populates="skills")

    def __repr__(self):
        return f"<JobSkill(job_id={self.job_id}, skill_name='{self.skill_name}')>"


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(Text)

    # Relationships
    job_roles = relationship("JobRole", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class JobRole(Base):
    __tablename__ = "job_roles"

    job_id = Column(Integer, ForeignKey("job.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)

    # Relationships
    job = relationship("Job", back_populates="roles")
    role = relationship("Role", back_populates="job_roles")

    def __repr__(self):
        return f"<JobRole(job_id={self.job_id}, role_id={self.role_id})>"


class Salary(Base):
    __tablename__ = "salary"

    job_id = Column(Integer, ForeignKey("job.id"), primary_key=True)
    salary_from = Column(BigInteger)
    salary_to = Column(BigInteger)
    salary_from_usd = Column(Numeric(12, 2))
    salary_to_usd = Column(Numeric(12, 2))
    currency = Column(Text, nullable=False)

    # Relationships
    job = relationship("Job", back_populates="salary")

    def __repr__(self):
        return f"<Salary(job_id={self.job_id}, salary_from={self.salary_from}, salary_to={self.salary_to}, currency='{self.currency}')>"


class JobProcessed(Base):
    __tablename__ = "job_processed"

    job_id = Column(Integer, ForeignKey("job.id"), primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default="now()")
    description = Column(Text)
    role_id = Column(Integer, ForeignKey("roles.id"))

    # Relationships
    job = relationship("Job")
    role = relationship("Role")

    def __repr__(self):
        return f"<JobProcessed(job_id={self.job_id}, role_id={self.role_id})>"


class ExtractedTag(Base):
    __tablename__ = "extracted_tags"

    job_id = Column(Integer, ForeignKey("job.id"), primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default="now()")
    tag = Column(Text, primary_key=True, nullable=False)

    # Relationships
    job = relationship("Job")

    def __repr__(self):
        return f"<ExtractedTag(job_id={self.job_id}, tag='{self.tag}')>"


class ExtractedSkill(Base):
    __tablename__ = "extracted_skills"

    job_id = Column(Integer, ForeignKey("job.id"), primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default="now()")
    skill = Column(Text, primary_key=True, nullable=False)
    skill_type = Column(String)

    # Relationships
    job = relationship("Job")

    def __repr__(self):
        return f"<ExtractedSkill(job_id={self.job_id}, skill='{self.skill}', skill_type='{self.skill_type}')>"


engine = get_db_engine()
Base.metadata.create_all(engine)
