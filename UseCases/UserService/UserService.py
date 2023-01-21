from Infrastructure.Persistence.Repository import Repository 
from Entities.User import User

class UserService:
    repository = Repository()

    def get_user(self, email: str, url: str, password: str):
        # Check if user exists 
        if (not self.repository.check_user(email, url)):
            # Create user
            self.repository.create_user(email, url, password)
        else: 
            raw_user = self.repository.get_user(email, url)

        return User()
