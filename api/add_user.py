import sys
import os

# Adiciona o diretório do projeto ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.security import generate_password_hash
from api.db import get_session
from api.models.models import User

def add_user(username, password, fname, lname):
    password_hash = generate_password_hash(password)
    new_user = User(username=username, password=password_hash, fname=fname, lname=lname)
    
    with get_session() as session:
        session.add(new_user)
        session.commit()

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python add_user.py <username> <password> <first name> <last name>")
        sys.exit(1)

    username, password, fname, lname = sys.argv[1:5]
    add_user(username, password, fname, lname)
    print(f"User {username} added successfully.")