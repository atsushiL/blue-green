import time
from django.utils import timezone
from ag_smile_leaseback_crm_back import settings
from authlib.jose import jwt, JoseError


def generate_token(data, expire):
    header = {"alg": "HS256"}
    key = settings.SECRET_KEY
    exp = {"exp": int(time.time()) + expire}
    data.update(exp)
    return jwt.encode(header=header, payload=data, key=key).decode()


def validate_token(token):
    token = token.encode()
    key = settings.SECRET_KEY
    try:
        data = jwt.decode(token, key)
        data.validate(now=timezone.now().timestamp())
    except JoseError:
        return False
    return data
