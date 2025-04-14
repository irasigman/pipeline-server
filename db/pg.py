import logging
import os

import logfire
from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


class PostgresDB:
    def __init__(self, db_user, db_password, db_name, db_host='localhost', db_port=5432, ssh_host=None, ssh_port=22,
                 ssh_user=None, ssh_password=None):
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.db_host = db_host
        self.db_port = db_port
        self.ssh_host = ssh_host
        self.ssh_port = ssh_port
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.server = None
        self.engine = None
        self.session = None

    def start_ssh_tunnel(self):
        if self.ssh_host and self.ssh_user and self.ssh_password:
            logging.info(f"Starting SSH tunnel to {self.ssh_host}:{self.ssh_port}")
            self.server = SSHTunnelForwarder(
                (self.ssh_host, self.ssh_port),
                ssh_username=self.ssh_user,
                ssh_password=self.ssh_password,
                remote_bind_address=(self.db_host, self.db_port)
            )
            self.server.start()
            self.db_port = self.server.local_bind_port

    def stop_ssh_tunnel(self):
        if self.server:
            self.server.stop()

    def connect(self):
        try:
            self.server = SSHTunnelForwarder(
                (self.ssh_host, self.ssh_port),
                ssh_username=self.ssh_user,
                ssh_password=self.ssh_password,
                remote_bind_address=(self.db_host, self.db_port)
            )
            self.server.start()
            logging.info("SSH tunnel started successfully.")
        except Exception as e:
            logging.error(f"Failed to start SSH tunnel: {e}")
            return

        try:
            # Database URL with the local port forwarded by the SSH tunnel
            database_url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.server.local_bind_port}/{self.db_name}"
            self.engine = create_engine(database_url, echo=True)
            Base.metadata.create_all(self.engine)
            SessionLocal = sessionmaker(bind=self.engine)
            self.session = SessionLocal()
            logging.info("Database connection established successfully.")
            logfire.instrument_sqlalchemy(engine=self.engine)
        except Exception as e:
            logging.error(f"Failed to connect to the database: {e}")
            self.stop_ssh_tunnel()

    def disconnect(self):
        if self.session:
            self.session.close()
        self.stop_ssh_tunnel()
