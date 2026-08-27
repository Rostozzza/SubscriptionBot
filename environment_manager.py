import os
from dotenv import load_dotenv

class EnvironmentManager:
    def __init__(self, env_file=".env"):
        self.env_file = env_file
        self.load_environment_variables()

    def load_environment_variables(self):
        load_dotenv(self.env_file)

    def get_variable(self, key):
        return os.getenv(key)