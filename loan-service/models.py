from sqlalchemy import create_engine, Column, Integer, Float, String, Date, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Define the base for declarative models
Base = declarative_base()

class Borrower(Base):
    __tablename__ = 'borrowers'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    contact_info = Column(String)
    credit_score = Column(Integer)

    loans = relationship("Loan", back_populates="borrower")

class Loan(Base):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    term = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    status = Column(String, nullable=False) # e.g., 'active', 'paid off', 'defaulted'
    borrower_id = Column(Integer, ForeignKey('borrowers.id'), nullable=False)

    borrower = relationship("Borrower", back_populates="loans")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False) # In a real app, store hashed passwords
    role = Column(String, nullable=False) # e.g., 'user', 'admin'
    permissions = Column(String) # comma-separated string of permissions

    refresh_tokens = relationship("RefreshToken", back_populates="user")

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")

# Example of how you would create the database tables (you would run this separately)
# if __name__ == "__main__":
#     engine = create_engine('sqlite:///loan_book.db')
#     Base.metadata.create_all(engine)