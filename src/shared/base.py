from .database import SessionLocalMain, SessionLocalAuth


def get_db():
    db = SessionLocalMain()
    try:
        yield db
    finally:
        db.close()
def get_auth_db():
    db = SessionLocalAuth()
    try:
        yield db
    finally:
        db.close()