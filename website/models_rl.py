from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        self.password = user_data['password']
        self.first_name = user_data['first_name']
        self.is_admin = user_data.get('is_admin', False)
        self.is_approved = user_data.get('is_approved', False)


class PromptResponse:
    def __init__(self, prompt, response, machine_feedback=None,
                 human_response=None, human_reason=None, user_id=None, _id=None, source=None, created_at=None, **kwargs):
        self.prompt = prompt
        self.machine_feedback = machine_feedback
        self.human_response = human_response
        self.human_reason = human_reason
        self.user_id = user_id
        self._id = _id
        self.source = source
        self.created_at = created_at
