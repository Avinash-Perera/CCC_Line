from sqlalchemy import Column, ForeignKey, Numeric, func
from sqlalchemy import String, Integer, Float, Sequence, DateTime, Boolean
from sqlalchemy.orm import relationship

from bin.db.postgresDB import Base


class DonationTable(Base):
    __tablename__ = "donation"

    record_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    second_name = Column(String, index=True)
    email = Column(String, index=True)
    mobile_no = Column(String(10), nullable=True)
    message = Column(String, index=True,nullable=True)
    currency_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    donation_id = Column(Integer,nullable=False)
    created_at = Column(DateTime, default=func.now())


class CurrencyTable(Base):
    __tablename__ = "currency"

    currency_id = Column(Integer, primary_key=True, index=True)
    currency_name = Column(String, index=True)
    currency_code = Column(String, index=True)

class DonationTypeTable(Base):
    __tablename__ = "donation_type"

    donation_id = Column(Integer, primary_key=True, index=True)
    donation_name = Column(String, index=True)
    is_general_donation = Column(Boolean, index=True)


class RidersTable(Base):
    __tablename__ = "riders_info"

    rider_id = Column(Integer, primary_key=True, index=True)
    rider_name = Column(String, index=True)
    rider_email = Column(String, index=True)
    mobile_no = Column(String(10), nullable=True)
    rider_goal = Column(Float, nullable=False)
    rider_raise = Column(Float, nullable=False)
    rider_img = Column(String, index=True)

class RiderDonation(Base):
    __tablename__ = "riders_donations"

    rider_id = Column(Integer, primary_key=True)
    donation_id = Column(Integer, primary_key=True)





