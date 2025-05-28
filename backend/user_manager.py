from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm.exc import NoResultFound
class UserManager:
    def __init__(self, session):
        self.session = session

    def create_user(self, username, password, role='user'):
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role=role
        self.session.add(new_user)
        self.session.commit()
        return new_user

    def get_user_by_username(self, username):
        try:
            return self.session.query(User).filter_by(username=username).one()
        except NoResultFound:
            return None

    def verify_password(self, user, password):
        return check_password_hash(user.password, password)

    def get_all_users(self):
        return self.session.query(User).all()

    def get_user(self, user_id):
        return self.session.query(User).get(user_id)

    def update_user(self, user_id, updated_data):
        user = self.get_user(user_id)
        if user:
            for key, value in updated_data.items():
                if hasattr(user, key):
                    if key == 'password':
                        user.password = generate_password_hash(value)
                    else:
                        setattr(user, key, value)
            self.session.commit()
            return user
        return None

    def delete_user(self, user_id):
        user = self.get_user(user_id)
        if user:
            self.session.delete(user)
            self.session.commit()
            return True
        return False