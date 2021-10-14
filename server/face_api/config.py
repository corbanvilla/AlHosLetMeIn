from os import environ as env

# DATABASE_URL = env.get("DATABASE_URL") or "mysql+pymysql://root:secure_corrbaan10@172.30.224.60:3306/crypto"
DATABASE_URL = env.get("DATABASE_URL") or "sqlite:///faces.db"
