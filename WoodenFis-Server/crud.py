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

def get_user_by_phone(db: Session, phone: str) -> Optional[models.User]:
    """根据手机号查询用户"""
    return db.query(models.User).filter(models.User.phone == phone).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str) -> models.User:
    db_user = models.User(
        username=user.username,
        email=user.email,
        phone=user.phone,
        hashed_password=hashed_password,
        avatar=user.avatar
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_by_phone(db: Session, user: schemas.UserCreateByPhone) -> models.User:
    """通过手机号创建用户（无密码）"""
    db_user = models.User(
        username=user.username,
        phone=user.phone,
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

# 验证码相关

def create_verification_code(db: Session, phone: str, code: str, expires_at: datetime) -> models.VerificationCode:
    """创建验证码记录"""
    # 先将该手机号之前的验证码标记为已使用
    db.query(models.VerificationCode).filter(
        models.VerificationCode.phone == phone,
        models.VerificationCode.used == False
    ).update({models.VerificationCode.used: True})
    
    db_code = models.VerificationCode(
        phone=phone,
        code=code,
        expires_at=expires_at
    )
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    return db_code

def get_valid_verification_code(db: Session, phone: str, code: str) -> Optional[models.VerificationCode]:
    """获取有效的验证码"""
    return db.query(models.VerificationCode).filter(
        models.VerificationCode.phone == phone,
        models.VerificationCode.code == code,
        models.VerificationCode.used == False,
        models.VerificationCode.expires_at > datetime.utcnow()
    ).first()

def use_verification_code(db: Session, code_id: int):
    """标记验证码为已使用"""
    db.query(models.VerificationCode).filter(
        models.VerificationCode.id == code_id
    ).update({models.VerificationCode.used: True})
    db.commit() 