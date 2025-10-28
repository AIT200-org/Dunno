#main.py

from db import SessionLocal
from models.user import User
from models.group import Group
from models.message import Message


def main():
    session = SessionLocal()

    # ➕ Créer quelques utilisateurs
    user1 = User(username="Wattara", email="pedjoganaouattara@gmail.com")
    user2 = User(username="Coulibaly Sara", email="coulsara@gmail.com", language="fr")

    session.add_all([user1, user2])
    session.commit()

    print("✅ Users added successfully.")

    # 🔍 Vérifier un utilisateur
    saved_user = session.query(User).filter_by(username="Wattara").first()
    if saved_user:
        print("👤 Found:", saved_user.username, "-", saved_user.email)

    session.close()

if __name__ == "__main__":
    main()