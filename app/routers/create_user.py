from passlib.context import CryptContext
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from ..database import Base, engine, SessionLocal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    def verify_password(self, plain_password):
        return pwd_context.verify(plain_password, self.hashed_password)

    @staticmethod
    def create_hashed_password(plain_password):
        return pwd_context.hash(plain_password)

# Exemplo de como criar um usuário com senha hasheada:
def create_user(db: Session, username: str, password: str):
    hashed_password = User.create_hashed_password(password)
    db_user = User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Exemplo de uso (em algum lugar da sua lógica de registro de usuário ou administrativa):
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        new_user = create_user(db, "john.doe", "minhasenha123")
        print(f"Usuário criado com ID: {new_user.user_id}")
    finally:
        db.close()