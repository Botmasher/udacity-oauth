from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()

class TestThing(Base):
	__tablename__ = 'thing'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)

	@property
	def serialize(self):
		return {
			'name': self.name,
			'id': self.id
		}

engine = create_engine('sqlite:///testdata.db')

Base.metadata.create_all(engine)
