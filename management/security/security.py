from bcrypt import hashpw, checkpw, gensalt


class Security:
    def encode(self, password: str) -> str:
        """Encode the password"""
        return str(hashpw(str.encode(password), self.generate_salt()))[2:-1]

    @staticmethod
    def check_password(password: str, hashed: str) -> bool:
        """Check if the password matches the one saved in the database"""
        return True if hashed and checkpw(str.encode(password), str.encode(hashed)) else False

    @staticmethod
    def generate_salt(rounds_: int = 4) -> bytes:
        return gensalt(rounds_)



