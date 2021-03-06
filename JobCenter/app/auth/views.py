# -*- coding: utf-8 -*-
# @Author: guomaoqiu
# @File Name: views.py
# @Date:   2019-03-19 11:59:48
# @Last Modified by:   guomaoqiu
# @Last Modified time: 2019-05-15 16:50:44
import random

from flask import render_template, redirect, request, url_for, flash, jsonify, current_app, make_response
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db


from ..models import User,LoginLog
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
import time
from .ali_msg import aliyun_sms_send


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            # print (request.headers.get('X-Forwarded-For',request.remote_addr))
            login_log = LoginLog()
            login_log.login_ip = request.headers.get('X-Forwarded-For',request.remote_addr)
            login_log.login_browser = str(request.user_agent)
            login_log.login_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

            # print (login_log)
            # print(login_log.login_ip,login_log.login_browser,login_log.login_time)
  
            db.session.add(login_log) # 提交
            db.session.commit()

            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.','danger')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.',"success")
    return redirect(url_for('auth.login'))


from ..constants import IMAGE_CODE_REDIS_EXPIRES
from .captchacode import captcha
from ..get_redis import connect_redis, get_redis_data, set_redis_data

@auth.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    """
    获取图片验证码
    ：params image_code_id: 图片验证码编号
    : return: 图片验证码
    """
    # 获取参数
    # 检验参数
    # 业务逻辑处理
    # 生成验证码图片
    # 生成图片验证码，其返回为名字、文本、以及图片
    name, text, image_data = captcha.generate_captcha()
    # print(text)
    # print(name)
    # 验证码真是值与编号保存到redis中
    try:
        # print("asdasd", image_code_id)
        set_redis_data('ImageCode_%s' % image_code_id, text, '120')
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)
        return jsonify('保存图片验证码失败')

    # 返回图片
    response = make_response(image_data)

    response.headers["Content-type"] = "image/png"

    return response






msg = 0

@auth.route("/sms_codes/<int:mobile>")
def get_sms_code(mobile):
    """获取短信验证码"""
    # 1.获取参数
    # 2. 校验参数
    # 3. 业务逻辑处理
    # 从redis中取出真实的图片验证码
    # 判断图片验证码是否过期

    # 与用户填写的值对比
    # 判断手机号存在不，
    # try:
    user = User.query.filter_by(mobile=mobile).first()
    # except Exception as e:
    #     current_user.logger.error(e)
    # else:
    if user is not None:
        return jsonify("手机号已存在")
    # 不存在则生成短信验证码
    code = "%06d" % random.randint(0, 999999)
    # 保存真实的短信验证码

    # 发送短信
    # 返回值
    result = aliyun_sms_send(code)
    if result == 0:
        return jsonify('发送成功')
    else:
        return jsonify('发送失败')





@auth.route('/register1905', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    mobile=form.mobile.data,
                    msg_code=form.msg_code.data
        )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('已经向您的邮箱发送了一份确认邮件.','success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!',"success")
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.',"info")
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)

@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)

@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)

@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))

