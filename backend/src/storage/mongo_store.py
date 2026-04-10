from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from ..config import MONGODB_DB_NAME, MONGODB_URI


class MongoStore:
    def __init__(self) -> None:
        self.client = None
        self.db = None
        if MONGODB_URI:
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[MONGODB_DB_NAME]

    def is_enabled(self) -> bool:
        return self.db is not None

    def save_session(self, payload: dict[str, Any]) -> bool:
        if not self.db:
            return False
        try:
            payload["created_at"] = datetime.now(timezone.utc)
            self.db["emotion_sessions"].insert_one(payload)
            return True
        except PyMongoError:
            return False

    def get_sessions(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self.db:
            return []
        try:
            cursor = self.db["emotion_sessions"].find({}).sort("created_at", -1).limit(limit)
            sessions = []
            for doc in cursor:
                normalized = self._normalize_doc(doc)
                sessions.append(normalized)
            return sessions
        except PyMongoError:
            return []

    @staticmethod
    def _normalize_doc(doc: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(doc)
        if "_id" in normalized and isinstance(normalized["_id"], ObjectId):
            normalized["_id"] = str(normalized["_id"])
        if "created_at" in normalized and isinstance(normalized["created_at"], datetime):
            normalized["created_at"] = normalized["created_at"].isoformat()
        return normalized
