from sqlalchemy.orm import Session
import models, schemas
from typing import Optional, List
from datetime import datetime
from sqlalchemy import desc

# 用户相关

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str) -> models.User:
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        avatar=user.avatar
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# 用户统计

def get_user_stat(db: Session, user_id: int) -> Optional[models.UserStat]:
    return db.query(models.UserStat).filter(models.UserStat.user_id == user_id).first()

def create_user_stat(db: Session, user_id: int) -> models.UserStat:
    stat = models.UserStat(user_id=user_id)
    db.add(stat)
    db.commit()
    db.refresh(stat)
    return stat

# 冥想会话

def create_meditation_session(db: Session, user_id: int, session: schemas.MeditationSessionCreate) -> models.MeditationSession:
    db_session = models.MeditationSession(
        user_id=user_id,
        duration=session.duration,
        tap_count=session.tap_count
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_meditation_sessions(db: Session, user_id: int, limit: int = 10) -> List[models.MeditationSession]:
    return db.query(models.MeditationSession).filter(models.MeditationSession.user_id == user_id).order_by(desc(models.MeditationSession.created_at)).limit(limit).all()

# 成就

def get_achievements(db: Session) -> List[models.Achievement]:
    return db.query(models.Achievement).all()

def unlock_achievement(db: Session, user_id: int, achievement_id: int) -> models.UserAchievement:
    ua = models.UserAchievement(user_id=user_id, achievement_id=achievement_id)
    db.add(ua)
    db.commit()
    db.refresh(ua)
    return ua

def get_user_achievements(db: Session, user_id: int) -> List[models.UserAchievement]:
    return db.query(models.UserAchievement).filter(models.UserAchievement.user_id == user_id).all()

# 排行榜

def get_leaderboard(db: Session, period: str, limit: int = 10) -> List[models.Leaderboard]:
    return db.query(models.Leaderboard).filter(models.Leaderboard.period == period).order_by(models.Leaderboard.rank).limit(limit).all()

# 分享任务

def get_share_tasks(db: Session) -> List[models.ShareTask]:
    return db.query(models.ShareTask).all()

def complete_share_task(db: Session, user_id: int, task_id: int) -> models.UserShareTask:
    ust = models.UserShareTask(user_id=user_id, task_id=task_id, completed=True, completed_at=datetime.utcnow())
    db.add(ust)
    db.commit()
    db.refresh(ust)
    return ust

def get_user_share_tasks(db: Session, user_id: int) -> List[models.UserShareTask]:
    return db.query(models.UserShareTask).filter(models.UserShareTask.user_id == user_id).all() 