from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        self.password = user_data['password']
        self.first_name = user_data['first_name']


class PromptResponse:
    def __init__(self, prompt, response, machine_feedback=None, human_feedback=None, user_id=None, _id=None,
                 created_at=None):
        self.prompt = prompt
        self.response = response
        self.machine_feedback = machine_feedback
        self.human_feedback = human_feedback
        self.user_id = user_id
        self._id = _id
        self.created_at = created_at
