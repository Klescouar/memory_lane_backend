from contextlib import asynccontextmanager
from fastapi import Security, FastAPI, HTTPException, status
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from database.connexion import get_db_connection
from database.schema import Memory, User, create_schema
from utils import VerifyToken


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_schema()
    yield


app = FastAPI(lifespan=lifespan)

load_dotenv()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

token_auth_scheme = HTTPBearer()
auth = VerifyToken()


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        """Returns HTTP 403"""
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthenticatedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication"
        )


@app.post("/users/")
async def create_user(user: User):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
        INSERT INTO memory_lane.users (user_id, email, name)
        VALUES (%s, %s, %s) RETURNING user_id;
        """,
            (user.user_id, user.email, user.name),
        )
        user_id = cursor.fetchone()[0]
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return {"user_id": user_id, "email": user.email, "name": user.name}


@app.post("/memories/")
async def create_memory(memory: Memory, auth_result: str = Security(auth.verify)):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT user_id FROM memory_lane.users WHERE user_id = %s;
            """,
            (auth_result["sub"],),
        )
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        cursor.execute(
            """
            INSERT INTO memory_lane.memories (user_id, title, description)
            VALUES (%s, %s, %s) RETURNING id;
            """,
            (auth_result["sub"], memory.title, memory.description),
        )
        memory_id = cursor.fetchone()[0]
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return {
        "id": memory_id,
        "user_id": auth_result["sub"],
        "title": memory.title,
        "description": memory.description,
    }


@app.get("/memories/")
async def get_memories(auth_result: str = Security(auth.verify)):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, title, description
            FROM memory_lane.memories
            WHERE user_id = %s;
            """,
            (auth_result["sub"],),
        )
        memories = cursor.fetchall()

        memories_dict = [
            {"id": row[0], "title": row[1], "description": row[2]} for row in memories
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return memories_dict
