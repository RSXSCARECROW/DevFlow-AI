import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

import models
from database import SessionLocal


load_dotenv()


# =========================
# CONFIGURATION
# =========================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "devflow-development-secret-change-this"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# =========================
# PASSWORD SECURITY
# =========================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# =========================
# ROUTER
# =========================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================
# DATABASE DEPENDENCY
# =========================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================
# SCHEMAS
# =========================

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# =========================
# HELPER FUNCTIONS
# =========================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(
    user_id: int
) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (JWTError, ValueError):
        raise credentials_exception

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if user is None:
        raise credentials_exception

    return user


# =========================
# REGISTER
# =========================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):

    existing_username = db.query(models.User).filter(
        models.User.username == user_data.username
    ).first()

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    existing_email = db.query(models.User).filter(
        models.User.email == user_data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(
            user_data.password
        )
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# =========================
# LOGIN
# =========================

@router.post(
    "/login",
    response_model=TokenResponse
)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    password_valid = verify_password(
        form_data.password,
        user.hashed_password
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================
# CURRENT USER
# =========================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: models.User = Depends(
        get_current_user
    )
):

    return current_user