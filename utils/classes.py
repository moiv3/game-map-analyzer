# import for Classes
from pydantic import BaseModel, EmailStr
from typing import Annotated, List, Dict
from annotated_types import MinLen
from datetime import datetime

# Classes
class Error(BaseModel):
    error: bool
    message: str

class Success(BaseModel):
    ok: bool
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
    task_id: int

class UserPreferences(BaseModel):
    send_mail: bool

class CredentialIn(BaseModel):
    credential: str

class TaskWip(BaseModel):
    任務編號: int
    遊戲類型: str
    影片備註: str | None
    狀態: str
    上傳時間: datetime
    最後更新時間: datetime

class TaskCompleted(BaseModel):
    任務編號: int
    遊戲類型: str
    影片備註: str | None
    狀態: str
    最後更新時間: datetime
    地圖: str | None
    影片: str | None
    路徑分析: str | None
    系統訊息: str | None

class TaskQueueOut(BaseModel):
    tasks_wip: List[TaskWip]
    tasks_completed: List[TaskCompleted]

class WebsiteStatistics(BaseModel):
    tasks: Dict
    game: Dict

class MemberPreferences(BaseModel):
    send_mail: bool

class PreferencesOut(BaseModel):
    ok: bool
    member_preferences: MemberPreferences