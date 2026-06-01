#load_dotenv() reads your .env file and loads everything into environment variables.
#os.getenv("KEY") fetches the value of that variable.
from dotenv import load_dotenv
import os   

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = "HS256"
    JWT_DECODE_ALGORITHMS = ["HS256"]