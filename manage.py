#!/usr/bin/env python3
import subprocess
import sys
import secrets
import string
import os
import json

PROJECT_NAME = "n8n"
VOLUMES = ['redis','postgress']


def generate_clear_password(length=100):
    ambiguous = {'O', '0', 'I', 'l', '1'}
    alphabet = ''.join(c for c in (string.ascii_letters + string.digits) if c not in ambiguous)
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def parse_args(argv):
    args = {}
    key = None
    for item in argv:
        if item.startswith("--"):
            key = item.lstrip("-")
            args[key] = True  # default if no value provided
        elif key:
            args[key] = item
            key = None
    return args


def up():
    """Start docker compose services"""
    for vol in VOLUMES:
        subprocess.run(["mkdir", "-p", f"/mnt/volume-db/{PROJECT_NAME}/{vol}"], check=True)
    subprocess.run(["docker", "compose", "-p", PROJECT_NAME, "up", "-d"], check=True)

def restart():
    """Docker restarts"""
    subprocess.run(["docker", "compose", "-p", PROJECT_NAME, "up", "-d","--force-recreate"], check=True)

def down():
    """Stop docker compose services and remove volumes"""
    subprocess.run(["docker", "compose", "-p", PROJECT_NAME, "down", "-v"], check=True)

def get_smtp_secrets():
    path = "/mnt/volume-db/secrets/smtp.json"
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"SMTP config file not found at: {path}")
    
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {path}: {e}")


def load_env_file(path):
    """
    Reads a .env file and returns its contents as a dictionary.
    Lines starting with # are ignored.
    """
    env_vars = {}

    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()

                # Skip comments or empty lines
                if not line or line.startswith("#"):
                    continue

                # Split only on the first '='
                if "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip().strip('"').strip("'")
    except FileNotFoundError:
        return {}

    return env_vars


class ComposeApp:

    def __init__(self, action, user, host, protocol):
        self.action = action
        self.user = user
        self.host = host
        self.protocol = protocol
        self.smtp_data = {}
        existing_vars =load_env_file('.env')

        try:
            self.smtp_data = get_smtp_secrets()
        except Exception as e:
            print(e)
            sys.exit(1)

        self.env_variables = {
            'POSTGRES_USER': "n8n_postgres_users",
            'POSTGRES_PASSWORD': generate_clear_password(),
            'POSTGRES_DB': "postgres",
            'POSTGRES_NON_ROOT_USER': "n8n_db_user",
            'POSTGRES_NON_ROOT_PASSWORD': generate_clear_password(),
            'ENCRYPTION_KEY': generate_clear_password(),
            'WEBHOOK_URL': f"{self.protocol}://{PROJECT_NAME}.{self.user}.{self.host}",
            'N8N_HOST': f"{PROJECT_NAME}.{self.user}.{self.host}",
            'N8N_PORT': 5678,
            'N8N_PROTOCOL': protocol,
            'N8N_SECURE_COOKIE': 'false',
            'N8N_RUNNERS_ENABLED': 'true',
            'OGNA_USER':user,
            'OGNA_HOST':host,
            'OGNA_PROTOCOL':protocol,
            'N8N_SMTP_HOST':self.smtp_data['host'],
            'N8N_SMTP_PORT':self.smtp_data['port'],
            'N8N_SMTP_USER':self.smtp_data['user'],
            'N8N_SMTP_PASS':self.smtp_data['password'],
            'N8N_SMTP_SENDER':self.smtp_data['sender'],
            'N8N_SMTP_SSL':"true" if str(self.smtp_data['ssl']).lower() in [1,'true',True] else "false"
        }

        for key, value in self.env_variables.items():
            self.env_variables[key] = existing_vars.get(key,value)

    def configure(self):
        with open('.env', 'w+') as env_file:
            for key, value in self.env_variables.items():
                env_file.write(f"{key}={value}")
                env_file.write("\n")

    def deploy(self):
        self.configure()
        if self.action == "up":
            up()
        elif self.action == "down":
            down()
        elif self.action == "restart":
            restart()            
        else:
            print(f"Unknown command: {self.action}")
            print("Available commands: up, down")
            sys.exit(1)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    app = ComposeApp(
        action=args.get("action"),
        user=args.get("user", 'user'),
        host=args.get("host", 'localhost'),
        protocol=args.get("protocol", 'http')
    )

    app.deploy()
