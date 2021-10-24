import pickle

from sqlalchemy.orm import Session

from face_api.database.models import User


def get_all_users(db: Session) -> dict:
    users = db.query(User).all()

    users_dict = {}
    for user in users:
        try:
            users_dict[user.id] = pickle.loads(user.face_encoding)
        except pickle.UnpicklingError:
            continue
    # users_dict = {f"{user.first_name} {user.last_name}": pickle.loads(user.face_encoding) for user in users}

    return users_dict


def set_face_encoding(db: Session, user_id: int, face_encoding):
    user = db.query(User).filter_by(id=user_id).first()
    user.face_encoding = face_encoding
    db.commit()


def get_alhosn_status(db: Session, user_id: int) -> str:
    user = db.query(User).filter_by(id=user_id).first()
    return user.alhosn_status
