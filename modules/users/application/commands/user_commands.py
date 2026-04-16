from dataclasses import dataclass

@dataclass
class RegisterUserCommand:
    email: str
    password: str
    first_name: str = None
    last_name: str = None
    role: str = 'user'

@dataclass
class UpdateUserCommand:
    user_id: int
    data: dict

@dataclass
class DeleteUserCommand:
    user_id: int
    current_user_id: int

@dataclass
class ResetPasswordCommand:
    user_id: int
    new_password: str
