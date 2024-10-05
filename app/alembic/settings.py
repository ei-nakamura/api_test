from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
import os

path = os.environ.get("APP_DATABASE_URL")
 
# Engine の作成
Engine = create_engine(
  path,
  echo=False
)
Base = declarative_base()