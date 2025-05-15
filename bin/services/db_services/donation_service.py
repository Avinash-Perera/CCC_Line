from fastapi import HTTPException
from sqlalchemy import update, func, select, bindparam

from bin.db.postgresDB import db_connection
from sqlalchemy.orm import Session
from bin.models import pg_models
from sqlalchemy.exc import SQLAlchemyError
from bin.response.response_model import ErrorResponseModel
from bin.services.db_services.payment_service import PaymentService
from bin.utils.response_codes import PaymentStatus

db: Session = next(db_connection())


def create_new_donation_record(request, db_session: Session = None):
    donation = None
    try:
        donation = pg_models.DonationTable(
            first_name=request.first_name,
            second_name=request.second_name,
            email=request.email,
            mobile_no=request.phone_number,
            message=request.message,
            currency_id=request.currency_id,
            amount=request.amount,
            donation_id=request.donation_id
        )

        db_session.add(donation)
        db_session.flush()

        if request.donation_id == 2:
            rider_donation = pg_models.RiderDonation(
                rider_id=request.rider_id,
                donation_id=donation.record_id
            )
            db_session.add(rider_donation)

            update_query = update(pg_models.RidersTable).where(
                pg_models.RidersTable.rider_id == request.rider_id
            ).values(
                rider_raise=pg_models.RidersTable.rider_raise + request.amount
            )
            db_session.execute(update_query)

        return donation

    except SQLAlchemyError as e:
        db_session.rollback()
        if donation and donation.record_id:
            db_session.delete(donation)
            db_session.commit()
        raise HTTPException(status_code=400, detail=str(e))


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


async def payment_callback_function(request, db_session: Session):
    try:
        resultIndicator = request.query_params.get("resultIndicator")
        if not resultIndicator:
            raise HTTPException(status_code=400, detail="Missing resultIndicator parameter")

        stmt = select(pg_models.Transaction).where(
            pg_models.Transaction.success_indicator == resultIndicator
        ).with_for_update()

        transaction = db_session.execute(stmt).scalar_one_or_none()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        try:
            payment_details = await PaymentService.verify_payment(
                transaction.mpgs_order_id,
                transaction.currency,
                db_session
            )

            transaction.status = payment_details["status"].value
            transaction.gateway_code = payment_details["gateway_code"].value

            if payment_details["status"] == PaymentStatus.COMPLETED:
                await update_payment_timestamp(transaction.donation_id, db_session)

            db_session.commit()

            return {
                "status": payment_details["status"],
                "gateway_code": payment_details["gateway_code"],
                "transaction": transaction
            }

        except Exception as e:
            db_session.rollback()
            raise

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_currency_by_id(currency_id: int):
    try:
        currency = db.query(pg_models.CurrencyTable).filter(
            pg_models.CurrencyTable.currency_id == currency_id
        ).first()

        if not currency:
            raise HTTPException(status_code=404, detail=f"Currency with ID {currency_id} not found")

        return currency

    except SQLAlchemyError as e:
        db.rollback()
        raise ErrorResponseModel(str(e), 400)

async def update_payment_timestamp(donation_id: int, db_session: Session = None):
    """Update the payment_done_at timestamp for a donation"""
    try:
        donation = db_session.execute(
            select(pg_models.DonationTable)
            .where(pg_models.DonationTable.record_id == donation_id)
        ).scalar_one_or_none()

        if donation:
            donation.payment_done_at = func.now()
            db_session.commit()
            return True
        return False

    except SQLAlchemyError as e:
        db_session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

