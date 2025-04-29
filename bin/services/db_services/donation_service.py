from sqlalchemy import update, func

from bin.db.postgresDB import db_connection
from sqlalchemy.orm import Session
from bin.models import pg_models
from sqlalchemy.exc import SQLAlchemyError
from bin.response.response_model import ErrorResponseModel

db: Session = next(db_connection())

def create_new_donation_record(request):
    try:
        data = pg_models.DonationTable(
            first_name = request.first_name,
            second_name = request.second_name,
            email = request.email,
            mobile_no = request.phone_number,
            message = request.message,
            currency_id = request.currency_id,
            amount = request.amount,
            donation_id = request.donation_id
        )

        db.add(data)
        db.commit()
        db.refresh(data)

        if request.donation_id == 2:
            data2 = pg_models.RiderDonation(
                rider_id=request.rider_id,
                donation_id=data.record_id
            )
            db.add(data2)
            db.commit()
            db.refresh(data)

            update_query = update(pg_models.RidersTable).where(
                pg_models.RidersTable.rider_id == request.rider_id
            ).values(
                rider_raise= pg_models.RidersTable.rider_raise + request.amount
            )

            result = db.execute(update_query)
            db.commit()

            rows_updated = result.rowcount
            print("rows", rows_updated)

        return data

    except SQLAlchemyError as e:
        db.rollback()
        raise ErrorResponseModel(str(e), 404)


def currency_list():
    try:
        data = db.query(
            pg_models.CurrencyTable
        ).all()

        return data

    except SQLAlchemyError as e:
        raise ErrorResponseModel(str(e), 404)


def donation_list():
    try:
        data = db.query(
            pg_models.DonationTypeTable
        ).all()

        return data

    except SQLAlchemyError as e:
        raise ErrorResponseModel(str(e), 404)

def sum_of_donations():
    try:
        total_amount = db.query(
            func.sum(pg_models.DonationTable.amount)
        ).filter(
            pg_models.DonationTable.donation_id == 1
        ).scalar()

        return total_amount or 0
    except SQLAlchemyError as e:
        db.rollback()
        raise ErrorResponseModel(str(e), 404)