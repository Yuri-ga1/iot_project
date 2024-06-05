from pydantic import BaseModel

class SessionData(BaseModel):
    username: str
    user_pass: str

    def get_inf(self):
        data = {
            'auth_': False,
            'username:': None,
            'user_pass': ''
        }
        if self.username:
            data = {
                'auth_': True,
                'username:': self.username,
                'user_pass': self.user_pass
            }
        return data