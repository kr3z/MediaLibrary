from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy import Integer

from Base import Base,engine

class IdSequenceTable(Base):
    __tablename__ = "Id_Sequence"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    sequence_value: Mapped[int] = mapped_column(Integer)

class Id_Sequence:
    def __init__(self):
        with Session(engine) as session:
            self.id_seq = session.query(IdSequenceTable).get(1)
            if self.id_seq is None:
                self.id_seq = IdSequenceTable(id=1, sequence_value=1)
                session.add(self.id_seq)
                session.flush()
                session.commit()
        self.fill_pool()
            #self.current_value = self.id_seq.sequence_value
            #self.max_id_value = self.current_value + 100
        #print("Sequence inited with currval: %s maxval: %s" % (self.current_value,self.max_id_value))

    def fill_pool(self):
        with Session(engine) as session:
            self.id_seq = session.query(IdSequenceTable).get(1)
            self.current_value = self.id_seq.sequence_value
            self.id_seq.sequence_value += 100
            self.max_id_value = self.id_seq.sequence_value
            session.flush()
            session.commit()


    def next_value(self):
        nextval = self.current_value
        self.current_value += 1
        #print("Retrieve nextval: %s maxval: %s" % (self.current_value,self.max_id_value))
        if self.current_value >= self.max_id_value:
            #print("maxval exceeded, incrementing sequence")
            self.fill_pool()


        return nextval

Base.metadata.create_all(engine)