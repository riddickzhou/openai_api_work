from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        self.password = user_data['password']
        self.first_name = user_data['first_name']


class PromptResponse:
    def __init__(self, prompt, response, original_response=None, machine_feedback=None,
                 human_check=None, human_response=None, human_reason=None,
                 user_id=None, _id=None, source=None, created_at=None, **kwargs):
        self.prompt = prompt
        self.response = response
        self.original_response = original_response
        self.machine_feedback = machine_feedback
        self.human_check = human_check
        self.human_response = human_response
        self.human_reason = human_reason
        self.user_id = user_id
        self._id = _id
        self.source = source
        self.created_at = created_at
