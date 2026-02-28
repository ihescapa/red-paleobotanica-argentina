import streamlit as st
import bcrypt
from models import Session, User

def hash_password(password):
    # bcrypt requires bytes
    passwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwd_bytes, salt)
    return hashed.decode('utf-8') # store as string

def verify_password(plain_password, hashed_password):
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_bytes, hashed_bytes)

def login_user(username, password):
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    
    if user and verify_password(password, user.password_hash):
        return user
    return None

def register_user(username, password, full_name, institution):
    session = Session()
    if session.query(User).filter_by(username=username).first():
        session.close()
        return False, "El usuario ya existe."
    
    new_user = User(
        username=username,
        password_hash=hash_password(password),
        full_name=full_name,
        institution=institution
    )
    session.add(new_user)
    session.commit()
    session.close()
    return True, "Usuario registrado exitosamente."
