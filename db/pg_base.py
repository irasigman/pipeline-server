import os
from db.pg import PostgresDB
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError


class PGBase:
    def __init__(self):
        self.ssh_tunnel = None
        self.db = None

    def start_ssh_tunnel(self):
        try:
            self.ssh_tunnel = SSHTunnelForwarder(
                (os.getenv('SSH_HOST'), int(os.getenv('SSH_PORT', 22))),
                ssh_username=os.getenv('SSH_USER'),
                ssh_password=os.getenv('SSH_PASSWORD'),
                remote_bind_address=(os.getenv('DB_HOST', 'localhost'), int(os.getenv('DB_PORT', 5432)))
            )
            self.ssh_tunnel.start()
        except BaseSSHTunnelForwarderError as e:
            raise ConnectionError(f"Failed to start SSH tunnel: {e}")

    def connect(self):
        try:
            self.start_ssh_tunnel()
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = int(os.getenv('DB_PORT', 5432))

            self.db = PostgresDB(
                db_user=os.getenv('DB_USER'),
                db_password=os.getenv('DB_PASSWORD'),
                db_name=os.getenv('DB_NAME'),
                db_host=db_host,
                db_port=db_port,
                ssh_host=os.getenv('SSH_HOST'),
                ssh_port=int(os.getenv('SSH_PORT', 22)),
                ssh_user=os.getenv('SSH_USER'),
                ssh_password=os.getenv('SSH_PASSWORD')
            )
            self.db.connect()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to the database: {e}")

    def disconnect(self):
        if self.db:
            self.db.disconnect()
        if self.ssh_tunnel:
            self.ssh_tunnel.stop()