import smtplib
from email.mime.text import MIMEText
import random
from fastapi import Body
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from .core.user_model import User, Conversation, Message
from .config.db_config import SQLALCHEMY_DATABASE_URL
from .config.email_config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .api.requests import PhoneLoginRequest, ResetPasswordRequest, PhoneRegisterRequest
import redis
import logging

# from aliyunsdkcore.client import AcsClient
# from aliyunsdkcore.acs_exception.exceptions import ClientException
# from aliyunsdkcore.acs_exception.exceptions import ServerException
# from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest
# from .config.aliyun_config import (
#     ALIYUN_ACCESS_KEY_ID,
#     ALIYUN_ACCESS_KEY_SECRET,
#     ALIYUN_SIGN_NAME,
#     ALIYUN_REGISTER_TEMPLATE_CODE,
#     ALIYUN_RESET_PASSWORD_TEMPLATE_CODE
# )

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 数据库连接设置
engine = create_engine(SQLALCHEMY_DATABASE_URL)
try:
    connection = engine.connect()
    logger.debug("数据库连接成功")
    connection.close()
except Exception as e:
    logger.error(f"数据库连接失败: {str(e)}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 连接 Redis
redis_client = redis.Redis(host='host.docker.internal', port=6379, db=0)
try:
    redis_client.ping()
    logger.debug("Redis 连接成功")
except redis.exceptions.ConnectionError as e:
    logger.error(f"Redis 连接失败: {str(e)}")

# 发送重置密码邮件请求模型
class SendResetEmailRequest(BaseModel):
    email: str

# 登录请求模型
class LoginRequest(BaseModel):
    email: str
    password: str

# 手机号登录请求模型
class PhoneLoginRequest(BaseModel):
    phone_number: str
    password: str

# 注册请求模型
class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    verification_code: str

# 手机号注册请求模型
class PhoneRegisterRequest(BaseModel):
    username: str
    password: str
    phone_number: str
    verification_code: str

# 发送验证码请求模型
class SendVerificationCodeRequest(BaseModel):
    email: str

# 验证邮箱重置验证码请求模型
class VerifyEmailResetCodeRequest(BaseModel):
    email: str
    verification_code: str

# 验证手机号重置验证码请求模型
class VerifyPhoneResetCodeRequest(BaseModel):
    phone_number: str
    verification_code: str

# 通过邮箱重置密码请求模型
class ResetPasswordByEmailRequest(BaseModel):
    email: str
    new_password: str

# 通过手机号重置密码请求模型
class ResetPasswordByPhoneRequest(BaseModel):
    phone_number: str
    new_password: str


class UpdateUserInfoRequest(BaseModel):
    id: int
    username: str
    email: str
    phone: str

login_router = APIRouter()

# @login_router.get("/api/user_info")
# async def get_user_info(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="用户未找到")
#     return {
#         "username": user.username,
#         "email": user.email,
#         "phone": user.phone,
#         "password": user.password,
#         "created_at": user.created_at
#     }


@login_router.post("/update_user_info")
def update_user_info(request: UpdateUserInfoRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == request.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")

    user.username = request.username
    user.email = request.email
    user.phone_number = request.phone

    try:
        db.commit()
        db.refresh(user)
        updated_user_info = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number
        }
        return updated_user_info
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新用户信息失败: {str(e)}")

# 邮箱登录
@login_router.post("/login_by_email")
def login_by_email(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    logger.debug(f"user: {user} is querying login by email")
    if not user:
        logger.debug(f"login {request.email} is incorrect.")
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    if not pwd_context.verify(request.password, user.password):
        logger.debug(f"login {request.email} is incorrect.")
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    logger.debug(f"login {request.email} is correct.")
    # 返回用户信息
    return {
        "message": "登录成功",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "phone_number": user.phone_number,
        "created_at": user.created_at
    }

# 手机号登录
@login_router.post("/login_by_phone")
def login_by_phone(request: PhoneLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == request.phone_number).first()
    if not user:
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    if not pwd_context.verify(request.password, user.password):
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    return {
        "message": "登录成功",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "phone_number": user.phone_number,
        "created_at": user.created_at
    }

# 邮箱注册
@login_router.post("/register_by_email")
def register_by_email(request: RegisterRequest, db: Session = Depends(get_db)):
    logger.debug(f"Received registration request: {request}")
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        logger.debug(f"Username {request.username} already exists.")
        raise HTTPException(status_code=400, detail="用户名已存在")
        
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        logger.debug(f"Email {request.email} already exists.")
        raise HTTPException(status_code=400, detail="邮箱已被注册")

    stored_code = redis_client.get(f'verification_code:{request.email}')
    if not stored_code or stored_code.decode() != request.verification_code:
        logger.debug(f"Verification code for {request.email} is incorrect.")
        raise HTTPException(status_code=400, detail="验证码错误")

    hashed_password = pwd_context.hash(request.password)
    new_user = User(username=request.username, password=hashed_password, email=request.email)
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.debug(f"New user {new_user.id} created.")
        # 删除 Redis 中的验证码
        redis_client.delete(f'verification_code:{request.email}')
        logger.debug(f"Verification code for {request.email} deleted from Redis.")
        logger.debug(f"Registration of {request.email} successful.")
        return {"message": "注册成功", "user_id": new_user.id}
    except Exception as e:
        db.rollback()
        logger.error(f"Registration of {request.email} failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")

# 手机号注册
@login_router.post("/register_by_phone")
def register_by_phone(request: PhoneRegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    existing_phone = db.query(User).filter(User.phone_number == request.phone_number).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="手机号已被注册")

    stored_code = redis_client.get(f'phone_verification_code:{request.phone_number}')
    if not stored_code or stored_code.decode() != request.verification_code:
        raise HTTPException(status_code=400, detail="验证码错误")

    hashed_password = pwd_context.hash(request.password)
    new_user = User(username=request.username, password=hashed_password, phone_number=request.phone_number)
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        # 删除 Redis 中的验证码
        redis_client.delete(f'phone_verification_code:{request.phone_number}')
        return {"message": "注册成功", "user_id": new_user.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")

# 发送邮箱注册验证码
@login_router.post("/send_email_verification_code")
def send_email_verification_code(request: SendVerificationCodeRequest):
    email = request.email
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    # 将验证码存储到 Redis 中，设置过期时间为 5 分钟（300 秒）
    redis_client.setex(f'verification_code:{email}', 300, code)

    msg = MIMEText(f"您的注册验证码是: {code}")
    msg['Subject'] = "注册验证码"
    msg['From'] = SMTP_USERNAME
    msg['To'] = email

    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
        logger.debug(f"尝试连接 SMTP 服务器: {SMTP_SERVER}:{SMTP_PORT}")
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        logger.debug(f"尝试发送邮件到 {email}")
        server.sendmail(SMTP_USERNAME, [email], msg.as_string())
        server.quit()
        return {"message": "验证码已发送，请查收邮箱"}
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP 认证失败，请检查 SMTP 用户名和密码")
        raise HTTPException(status_code=500, detail="SMTP 认证失败，请检查 SMTP 用户名和密码")
    except smtplib.SMTPException as smtp_error:
        logger.error(f"SMTP 错误: {str(smtp_error)}")
        raise HTTPException(status_code=500, detail=f"SMTP 错误: {str(smtp_error)}")
    except Exception as e:
        logger.error(f"发送验证码失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"发送验证码失败: {str(e)}")


# # 发送手机号验证码
# @login_router.post("/send_phone_verification_code")
# def send_phone_verification_code(phone_number: str):
#     code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
#     # 将验证码存储到 Redis 中，设置过期时间为 5 分钟（300 秒）
#     redis_client.setex(f'phone_verification_code:{phone_number}', 300, code)

#     # 初始化阿里云客户端
#     client = AcsClient(ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET, 'cn-hangzhou')

#     # 发送短信
#     request = SendSmsRequest()
#     request.set_accept_format('json')
#     request.set_phone_numbers(phone_number)
#     request.set_sign_name(ALIYUN_SIGN_NAME)
#     request.set_template_code(ALIYUN_REGISTER_TEMPLATE_CODE)
#     request.set_template_param("{\"code\":\"" + code + "\"}")

#     try:
#         response = client.do_action_with_exception(request)
#         logger.debug(f"短信发送响应: {response}")
#         return {"message": "验证码已发送，请查收短信"}
#     except ClientException as e:
#         logger.error(f"阿里云客户端异常: {e}")
#         raise HTTPException(status_code=500, detail=f"发送验证码失败: {str(e)}")
#     except ServerException as e:
#         logger.error(f"阿里云服务器异常: {e}")
#         raise HTTPException(status_code=500, detail=f"发送验证码失败: {str(e)}")
#     except Exception as e:
#         logger.error(f"发送验证码失败: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"发送验证码失败: {str(e)}")

# # 发送手机号重置密码验证码
# @login_router.post("/send_phone_reset_code")
# def send_phone_reset_code(phone_number: str):
#     code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
#     # 将验证码存储到 Redis 中，设置过期时间为 5 分钟（300 秒）
#     redis_client.setex(f'phone_reset_token:{phone_number}', 300, code)

#     # 初始化阿里云客户端
#     client = AcsClient(ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET, 'cn-hangzhou')

#     # 发送短信
#     request = SendSmsRequest()
#     request.set_accept_format('json')
#     request.set_phone_numbers(phone_number)
#     request.set_sign_name(ALIYUN_SIGN_NAME)
#     request.set_template_code(ALIYUN_RESET_PASSWORD_TEMPLATE_CODE)
#     request.set_template_param("{\"code\":\"" + code + "\"}")

#     try:
#         response = client.do_action_with_exception(request)
#         logger.debug(f"短信发送响应: {response}")
#         return {"message": "重置验证码已发送，请查收短信"}
#     except ClientException as e:
#         logger.error(f"阿里云客户端异常: {e}")
#         raise HTTPException(status_code=500, detail=f"发送重置验证码失败: {str(e)}")
#     except ServerException as e:
#         logger.error(f"阿里云服务器异常: {e}")
#         raise HTTPException(status_code=500, detail=f"发送重置验证码失败: {str(e)}")
#     except Exception as e:
#         logger.error(f"发送重置验证码失败: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"发送重置验证码失败: {str(e)}")

# 发送邮箱重置密码验证码
@login_router.post("/send_email_reset_code")
def send_email_reset_code(request: SendResetEmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        logger.debug(f"User with email {request.email} does not exist.")
        raise HTTPException(status_code=404, detail="用户不存在")

    token = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    # 将重置令牌存储到 Redis 中，设置过期时间为 5 分钟（300 秒）
    redis_client.setex(f'reset_token:{request.email}', 300, token)

    msg = MIMEText(f"您的重置密码验证码是: {token}")
    msg['Subject'] = "重置密码验证码"
    msg['From'] = SMTP_USERNAME
    msg['To'] = request.email

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, [request.email], msg.as_string())
        server.quit()
        return {"message": "重置密码邮件已发送，请查收邮箱"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送重置密码邮件失败: {str(e)}")


# 验证邮箱重置验证码
@login_router.post("/verify_email_reset_code")
def verify_email_reset_code(request: VerifyEmailResetCodeRequest):
    stored_token = redis_client.get(f'reset_token:{request.email}')
    if not stored_token or stored_token.decode() != request.verification_code:
        raise HTTPException(status_code=400, detail="验证码错误")
    return {"message": "验证码验证成功"}

# 验证手机号重置验证码
@login_router.post("/verify_phone_reset_code")
def verify_phone_reset_code(request: VerifyPhoneResetCodeRequest):
    stored_token = redis_client.get(f'phone_reset_token:{request.phone_number}')
    if not stored_token or stored_token.decode() != request.verification_code:
        raise HTTPException(status_code=400, detail="验证码错误")
    return {"message": "验证码验证成功"}

# 通过邮箱重置密码
@login_router.post("/reset_password_by_email")
def reset_password_by_email(request: ResetPasswordByEmailRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    hashed_password = pwd_context.hash(request.new_password)
    user.password = hashed_password
    db.commit()
    db.refresh(user)
    # 删除 Redis 中的重置令牌
    redis_client.delete(f'reset_token:{request.email}')
    return {"message": "密码重置成功"}

# 通过手机号重置密码
@login_router.post("/reset_password_by_phone")
def reset_password_by_phone(request: ResetPasswordByPhoneRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_number == request.phone_number).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    hashed_password = pwd_context.hash(request.new_password)
    user.password = hashed_password
    db.commit()
    db.refresh(user)
    # 删除 Redis 中的重置令牌
    redis_client.delete(f'phone_reset_token:{request.phone_number}')
    return {"message": "密码重置成功"}




@login_router.post("/delete_user")
def delete_user(request: dict, db: Session = Depends(get_db)):
    user_id = request.get('id')
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    try:
        # 删除与该用户关联的对话
        conversations = db.query(Conversation).filter(Conversation.user_id == user_id).all()
        for conversation in conversations:
            # 删除与该对话关联的消息
            db.query(Message).filter(Message.conversation_id == conversation.id).delete()
        # 删除与该用户关联的对话
        db.query(Conversation).filter(Conversation.user_id == user_id).delete()
        # 删除用户账户
        db.delete(user)
        db.commit()
        return {"message": "账号已成功注销"}
    except Exception as e:
        db.rollback()
        logger.error(f"注销账号失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"注销账号失败: {str(e)}")