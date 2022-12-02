from django.core import mail
from django.template.loader import render_to_string


def send_password_reset(user_email, url):
    plaintext = render_to_string("../templates/reset_password.txt", {"url": url})
    html_text = render_to_string("../templates/reset_password.html", {"url": url})

    mail.send_mail(
        subject="【AG住まいるリースバックCRM】パスワード再発行のお知らせ",
        message=plaintext,
        from_email=None,
        recipient_list=[user_email],
        html_message=html_text,
    )


def send_welcome_email(user_email, username, url):
    plaintext = render_to_string("../templates/welcome_email.txt", {"username": username, "url": url})
    html_text = render_to_string("../templates/welcome_email.html", {"username": username, "url": url})

    mail.send_mail(
        subject="【AG住まいるリースバックCRM】アカウント認証のお願い",
        message=plaintext,
        from_email=None,
        recipient_list=[user_email],
        html_message=html_text,
    )


def send_refuse_email(user_email, customer_name, user_name, address):
    plaintext = render_to_string(
        "../templates/refuse_mail.txt", {
            "customer_name": customer_name, "user_name": user_name, "address": address})
    html_text = render_to_string(
        "../templates/refuse_mail.html", {
            "customer_name": customer_name, "user_name": user_name, "address": address})

    mail.send_mail(
        subject="リースバックの問い合わせについて/AG住まいるリースバック",
        from_email=None,
        message=plaintext,
        recipient_list=[user_email],
        html_message=html_text,
    )
