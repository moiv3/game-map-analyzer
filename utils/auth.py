# External Dependencies
from fastapi import Header
from fastapi.responses import JSONResponse
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, DecodeError
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from datetime import *

# Internal Dependencies
from utils.classes import TokenOut
from utils.config import SECRET_KEY, token_valid_time

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_token_header(authorization: str = Header(...)) -> TokenOut:
    stripped_token = authorization[len("Bearer "):]
    if not stripped_token:
        return False
    return TokenOut(token=stripped_token)

def check_user_signin_status(token_data):
    print(token_data)
    try:
        result = {}
        result["data"] = jwt.decode(token_data.token, SECRET_KEY, algorithms="HS256")
        print("Data:", result)
        return JSONResponse(status_code=200, content=result)
    except ExpiredSignatureError:
        print("ExpiredSignatureError")
        return JSONResponse(status_code=401, content={"data": None})
    except InvalidSignatureError:
        print("InvalidSignatureError")
        return JSONResponse(status_code=401, content={"data": None})
    except DecodeError:
        print("DecodeError")
        return JSONResponse(status_code=401, content={"data": None})
    except Exception:
        print("Other exceptions")
        return JSONResponse(status_code=401, content={"data": None})

def check_user_signin_status_return_bool(token_data):
    try:
        decode_result = jwt.decode(token_data.token, SECRET_KEY, algorithms="HS256")
        # decode success and there is an id in the result (indicating a real user)
        if decode_result["id"]:
            return decode_result
        else:
            return False
    except Exception:
        return False
    
def create_gma_token(id: int, email: str, name: str):
    user_information = {}
    user_information["id"] = id
    user_information["email"] = email
    user_information["name"] = name
    time_now = datetime.now(tz=timezone.utc)
    user_information["iat"] = time_now.timestamp()
    user_information["exp"] = (time_now + token_valid_time).timestamp()
    print(user_information)
    user_token = jwt.encode(user_information, SECRET_KEY, algorithm="HS256")
    print(user_token)
    return user_token
