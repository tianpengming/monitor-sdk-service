from .common import BaseModel, engine

def create_db():
    print('create_db action')
    BaseModel.metadata.create_all(engine)

def drop_db():
    print('drop_db action')
    BaseModel.metadata.drop_all(engine)
