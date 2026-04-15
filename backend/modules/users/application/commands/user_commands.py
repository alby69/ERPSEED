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
    userId: int
    data: dict

@dataclass
class DeleteUserCommand:
    userId: int
    current_userId: int

@dataclass
class ResetPasswordCommand:
    userId: int
    new_password: str
