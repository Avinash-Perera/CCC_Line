from bin.db.postgresDB import db_connection
from sqlalchemy.orm import Session
from bin.models import pg_models
from sqlalchemy.exc import SQLAlchemyError
from bin.response.response_model import ErrorResponseModel

db: Session = next(db_connection())

def create_new_rider(request,img_name):
    try:
        data = pg_models.RidersTable(
            rider_name = request.rider_name,
            rider_email = request.rider_email,
            mobile_no = request.rider_phone_no,
            rider_goal = request.rider_goal,
            rider_raise = request.rider_raise,
            rider_img = img_name,
        )

        db.add(data)
        db.commit()
        db.refresh(data)
        return data

    except SQLAlchemyError as e:
        db.rollback()
        raise ErrorResponseModel(str(e), 404)


def all_riders():
    try:
        data = db.query(
            pg_models.RidersTable
        ).all()

        return data
    except SQLAlchemyError as e:
        raise ErrorResponseModel(str(e), 404)