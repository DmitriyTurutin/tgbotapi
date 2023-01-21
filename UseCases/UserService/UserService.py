from Infrastructure.Persistence.Repository import Repository 
from Entities.User import User

class UserService:
    repository = Repository()

    def __init__(self) -> None:
        pass

    def get_user(self, email: str, url: str, password: str):
        # Check if user exists 
        user = User()
        if (not self.repository.check_user(email, url)):
            # Create user
            self.repository.create_user(email, url, password)
            user.email = email
            user.url = url
            user.password = password
            return user
        else: 
            raw_user = self.repository.get_user(email, url)
            user.url = raw_user[1]
            user.email = raw_user[2]
            user.password = raw_user[3]
            user.last_updated = raw_user[4]
            user.model_url = raw_user[5]
            return user
            