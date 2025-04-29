from datetime import datetime, timedelta, timezone
from typing import Annotated, List

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from model import Token, User, engine
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlmodel import (Field, Relationship, Session, SQLModel, String,
                      create_engine, select)
