from pydantic import BaseModel

class SessionData(BaseModel):
    user_id: int

    def get_inf(self):
        data = {
            'auth_': False,
            'user_id:': None,
            'user_pass': ''
        }
        if self.user_id:
            data = {
                'auth_': True,
                'user_id:': self.user_id
            }
        return data