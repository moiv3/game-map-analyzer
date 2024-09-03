# import for Classes
from pydantic import BaseModel, EmailStr
from typing import Annotated
from annotated_types import MinLen

# Classes
class Error(BaseModel):
    error: bool
    message: str

class SignupFormData(BaseModel):
    name: Annotated[str, MinLen(1)]
    email: EmailStr
    password: Annotated[str, MinLen(1)]

class SigninFormData(BaseModel):
    email: EmailStr
    password: Annotated[str, MinLen(1)]

class TokenOut(BaseModel):
    token: str

class UserSigninData(BaseModel):
    id: int
    name: Annotated[str, MinLen(1)]
    email: EmailStr

class UserSigninDataOut(BaseModel):
    data: UserSigninData

class VideoParseInfo(BaseModel):
    youtube_id: str
    api_key: str

class VideoParseInfoUploaded(BaseModel):
    video_id: int

class UserPreferences(BaseModel):
    send_mail: bool

class CredentialIn(BaseModel):
    credential: str