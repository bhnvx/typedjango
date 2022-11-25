from rest_framework import status


class AlreadyExistsError(Exception):
    status = status.HTTP_409_CONFLICT
    detail = "이미 존재합니다."