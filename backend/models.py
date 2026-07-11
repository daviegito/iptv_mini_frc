from sqlalchemy import Column, Integer, String
from database import Base
from pydantic import BaseModel

# Modelo do Banco de Dados (Tabela Usuários)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    perfil = Column(String) # Pode ser 'admin', 'lan' ou 'wan'

# Modelos do Pydantic (Validação de Dados que entram/saem da API)
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    perfil: str | None = None
