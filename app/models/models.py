from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ..extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    leetcode_profile = db.relationship(
        "LeetCodeProfile", back_populates="user", uselist=False, cascade="all, delete"
    )
    goals = db.relationship("Goal", back_populates="user", cascade="all, delete")
    friends = db.relationship(
        "Friend",
        foreign_keys="Friend.user_id",
        back_populates="user",
        cascade="all, delete",
    )
    contests = db.relationship(
        "ContestHistory", back_populates="user", cascade="all, delete"
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class LeetCodeProfile(db.Model):
    __tablename__ = "leetcode_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    leetcode_username = db.Column(db.String(64), unique=True, nullable=False)
    total_solved = db.Column(db.Integer, default=0)
    easy_solved = db.Column(db.Integer, default=0)
    medium_solved = db.Column(db.Integer, default=0)
    hard_solved = db.Column(db.Integer, default=0)
    contest_rating = db.Column(db.Float, default=0)
    contest_ranking = db.Column(db.Integer, default=0)
    acceptance_rate = db.Column(db.Float, default=0.0)

    last_synced_at = db.Column(db.DateTime)

    user = db.relationship("User", back_populates="leetcode_profile")

    def __repr__(self):
        return f"<LeetCodeProfile {self.leetcode_username}>"


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    goal_type = db.Column(db.String(64), nullable=False)  # e.g. total_solved, medium_solved, contest_rating
    description = db.Column(db.String(255))
    target_value = db.Column(db.Integer, nullable=False)
    current_value = db.Column(db.Integer, default=0)
    status = db.Column(db.String(32), default="active")  # active, completed, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="goals")

    def progress_percent(self) -> float:
        if self.target_value == 0:
            return 0.0
        return min(100.0, (self.current_value / self.target_value) * 100.0)


class Friend(db.Model):
    __tablename__ = "friends"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    friend_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", foreign_keys=[user_id], back_populates="friends")
    friend_user = db.relationship("User", foreign_keys=[friend_user_id])

    def __repr__(self):
        return f"<Friend {self.user_id} -> {self.friend_user_id}>"


class ContestHistory(db.Model):
    __tablename__ = "contest_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    contest_name = db.Column(db.String(128), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    contest_date = db.Column(db.DateTime, nullable=False)

    user = db.relationship("User", back_populates="contests")

    def __repr__(self):
        return f"<ContestHistory {self.contest_name} {self.rating}>"
