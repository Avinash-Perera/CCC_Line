from sqlalchemy import Column, func, JSON, ForeignKey, Numeric
from sqlalchemy import String, Integer, Float, DateTime, Boolean, Text

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
    payment_done_at = Column(DateTime, nullable=True)


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

class ApiLog(Base):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_url = Column(String, nullable=False)
    request_method = Column(String, nullable=False)
    request_headers = Column(JSON, nullable=True)
    request_payload = Column(JSON, nullable=True)
    response_status = Column(Integer, nullable=True)
    response_headers = Column(JSON, nullable=True)
    response_body = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    donation_id = Column(Integer, ForeignKey('donation.record_id'))
    mpgs_order_id = Column(String, unique=True)
    session_id = Column(String)
    success_indicator = Column(String)
    status = Column(String, default="initiated")
    amount = Column(Numeric(10, 2))
    currency = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())





