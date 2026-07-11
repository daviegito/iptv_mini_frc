from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import models, database, auth

router = APIRouter(tags=["Autenticação"])

# Cria usuários padrão exigidos pelo professor (Admin, e os hosts Z, W, X, Y)
def init_db_users(db: Session):
    usuarios_iniciais = [
        {"user": "admin", "pass": "admin123", "perfil": "admin"},
        {"user": "hostz", "pass": "123", "perfil": "lan"},
        {"user": "hostw", "pass": "123", "perfil": "lan"},
        {"user": "hostx", "pass": "123", "perfil": "wan"},
        {"user": "hosty", "pass": "123", "perfil": "wan"}
    ]
    for u in usuarios_iniciais:
        if not db.query(models.User).filter(models.User.username == u["user"]).first():
            db_user = models.User(
                username=u["user"],
                hashed_password=auth.get_password_hash(u["pass"]),
                perfil=u["perfil"]
            )
            db.add(db_user)
    db.commit()


@router.post("/login", response_model=models.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # Na primeira vez que chamarem o login, garantimos que os usuários padrão existem
    init_db_users(db)
    
    # Busca o usuário no banco de dados SQLite
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    # Verifica a senha
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Se a senha estiver correta, gera o Token JWT
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Embutimos o "perfil" dentro do payload do token para não precisarmos ficar buscando no banco depois nas outras requisições
    access_token = auth.create_access_token(
        data={"sub": user.username, "perfil": user.perfil}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Rota protegida apenas para testar se o token JWT é válido
@router.get("/me", response_model=models.TokenData)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return {"username": current_user.username, "perfil": current_user.perfil}
