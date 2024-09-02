from datetime import datetime

from django.contrib.auth import get_user_model
from ninja_extra import api_controller, route, status
from ninja_extra.permissions import IsAdminUser, IsAuthenticated
from ninja_jwt import schema
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import TokenObtainSlidingController
from ninja_jwt.tokens import SlidingToken

from django.conf import settings
from django.core.mail import send_mail
from verify_email.email_handler import send_verification_email

from ninja_backend.apps.users.schema import (
    CreateUserSchema,
    EnableDisableUserOutSchema,
    EnableDisableUserSchema,
    UserTokenOutSchema,
    UserOutSchema,
)

User = get_user_model()


@api_controller("/auth", tags=["users"], auth=JWTAuth())
class UserController:
    # @route.post(
    #     "/create", response={201: UserTokenOutSchema}, url_name="user-create", auth=None
    # )
    # def create_user(self, user_schema: CreateUserSchema):
    #     user = user_schema.create()
    #     token = SlidingToken.for_user(user)
    #     return UserTokenOutSchema(
    #         user=user,
    #         token=str(token),
    #         token_exp_date=datetime.utcfromtimestamp(token["exp"]),
    #     )
    @route.post(
        "/create", response={201: UserTokenOutSchema}, url_name="user-create", auth=None
    )
    def create_user(self, user_schema: CreateUserSchema, subject: str, message: str):
        # 创建用户
        user = user_schema.create()
        token = SlidingToken.for_user(user)
        # 获取用户的邮箱
        user_email = user.email
        # 调用发送邮件的函数
        self.send_email(user_email, subject, message)
        # 返回用户和 token 信息
        return UserTokenOutSchema(
            user=user,
            token=str(token),
            token_exp_date=datetime.utcfromtimestamp(token["exp"]),
        )

    def send_email(self, email: str, subject: str, message: str):
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return {"message": "Email sent successfully!"}

    @route.put(
        "/{int:pk}/enable-disable",
        permissions=[IsAuthenticated, IsAdminUser],
        response=EnableDisableUserOutSchema,
        url_name="user-enable-disable",
    )
    def enable_disable_user(self, pk: int):
        user_schema = EnableDisableUserSchema(user_id=str(pk))
        user_schema.update()
        return EnableDisableUserOutSchema(message="Action Successful")

    @route.delete(
        "/{int:pk}/delete",
        permissions=[IsAuthenticated, IsAdminUser],
        response=EnableDisableUserOutSchema,
        url_name="user-delete",
    )
    def delete_user(self, pk: int):
        user_schema = EnableDisableUserSchema(user_id=str(pk))
        user_schema.delete()
        return self.create_response("", status_code=status.HTTP_204_NO_CONTENT)
    @route.get(
        "/get_user", response={200: UserOutSchema}, url_name="user-get", auth=JWTAuth()
    )
    def get_user(self,request):
        user = request.user
        return UserOutSchema(
            user=user,
        )
@api_controller("/auth", tags=["auth"])
class UserTokenController(TokenObtainSlidingController):
    auto_import = True

    @route.post("/login", response=UserTokenOutSchema, url_name="login")
    def obtain_token(self, user_token: schema.TokenObtainSlidingSerializer):
        user = user_token._user
        token = SlidingToken.for_user(user)
        return UserTokenOutSchema(
            user=user,
            token=str(token),
            token_exp_date=datetime.utcfromtimestamp(token["exp"]),
        )

    @route.post(
        "/api-token-refresh",
        response=schema.TokenRefreshSlidingSerializer,
        url_name="refresh",
    )
    def refresh_token(self, refresh_token: schema.TokenRefreshSlidingSchema):
        refresh = schema.TokenRefreshSlidingSerializer(**refresh_token.dict())
        return refresh

    @route.post("/send-email")
    def send_email(self, email: str, subject: str, message: str):
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return {"message": "Email sent successfully!"}
