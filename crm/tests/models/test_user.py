from typing import Optional

import pytest
from django.db.utils import DataError, IntegrityError
from django.test import TransactionTestCase

from crm.models import User


def make_user(
    username: str = "00000001",
    # パスワードはtest
    password: Optional[str] = "test",
    email: Optional[str] = "test_management_one@test.com",
) -> User:
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
    )
    return user


class TestUser(TransactionTestCase):
    fixtures = ["crm.json"]

    def test_user_username(self):
        new_user = make_user(username="00000004")
        assert new_user is not None
        assert new_user.username == "00000004"
        assert str(new_user) == "00000004"
        # 社員番号がすでに使用されている時
        with pytest.raises(IntegrityError) as e:
            user = make_user(username="00000004")
        # 社員番号が未入力の時
        with pytest.raises(ValueError) as e:
            user = make_user(username=None)
        # 社員番号が8桁を超える時
        with pytest.raises(DataError) as e:
            user = make_user(username="123456789")
        # 社員番号が8桁に満たない時
        with pytest.raises(IntegrityError) as e:
            user = make_user(username="1234567")
        # 社員番号に数字以外の文字列が使用されている時
        with pytest.raises(IntegrityError) as e:
            user = make_user(username="abcdefgh")
        # 社員番号が空文字時
        with pytest.raises(ValueError) as e:
            user = make_user(username="")

    def test_user_email(self):
        # メールアドレスがすでに使用されている時
        with pytest.raises(IntegrityError) as e:
            user = make_user(email="test_general_one@test.com")
        # メールアドレスが254文字を超える時
        with pytest.raises(DataError) as e:
            # 255文字のメールアドレスを作成
            email = "a" * 246 + "@test.com"
            user = make_user(email=email)
        # メールアドレスが未記入の時
        with pytest.raises(IntegrityError) as e:
            user = make_user(email=None)
