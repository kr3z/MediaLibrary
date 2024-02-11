import os
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine, Sequence

WORKING_DIR = os.path.dirname(os.path.realpath(__file__))

ENGINE_TYPE = "sqlite"

class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///" + os.path.join(WORKING_DIR, "library.db"), echo=True)

if ENGINE_TYPE == "sqlite":
    from SqliteObjects import Id_Sequence
    id_seq = Id_Sequence()
else:
    id_seq = Sequence("id_seq",metadata=Base.metadata, start=1, increment=100)