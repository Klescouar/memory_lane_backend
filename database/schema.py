from database.connexion import get_db_connection
from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    email: str
    name: str


class Memory(BaseModel):
    title: str
    description: str


def create_schema():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE SCHEMA IF NOT EXISTS memory_lane;
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS memory_lane.users (
            user_id VARCHAR(100) NOT NULL PRIMARY KEY,
            email VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS memory_lane.memories (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(100) NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES memory_lane.users (user_id) ON DELETE CASCADE
        );
        """
    )

    conn.commit()
    cursor.close()
    conn.close()
