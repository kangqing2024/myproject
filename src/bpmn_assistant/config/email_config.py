import os


# 从环境变量中获取邮箱配置信息
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.qq.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '2631452568@qq.com')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'cixblktftcrdecdi')