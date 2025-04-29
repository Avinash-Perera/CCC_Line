from bin.models.pg_models import Base
from bin.db.postgresDB import engine


Base.metadata.create_all(bind=engine)