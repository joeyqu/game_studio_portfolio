from sqlalchemy_utils import database_exists

def init_db(app, db, DB_NAME):
        with app.app_context():
            try:
                db.create_all()
            except exec.SQLAlchemyError as sqlalchemyerror:
                print("got the following SQLAlchemyError: " + str(sqlalchemyerror))
            except Exception as exception:
                print("got the following Exception: " + str(exception))
            finally:
                print("db.create_all() in __init__.py was successfull - no exceptions were raised")