# settings.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

path = 'postgresql+psycopg2://postgres:secret@localhost/default'
 
# Engine の作成
Engine = create_engine(
  path,
  echo=False
)
Base = declarative_base()