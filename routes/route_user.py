from typing import Union
from fastapi import APIRouter, HTTPException, Query
from src.database import Session, User
from src.models import RegisterUserRequest, UserModel
from sqlalchemy import desc, asc

route_user = APIRouter()

@route_user.get('/users', summary='', tags=['User'])  # Исправлено с post запроса на get.
def users_list(answer: Union[str, None] = Query(description='asc/desc', default=None)):
    """
    Список пользователей
    """
    try:
        users = []
        if answer is None:
            users = Session().query(User).all()
        elif answer.lower() == 'asc':
            users = Session().query(User).order_by(asc(User.age)).all()
        elif answer.lower() == 'desc':
            users = Session().query(User).order_by(desc(User.age)).all()
        else:
            raise HTTPException(status_code=400, detail='Неверно указана операция')

        return [{
            'id': user.id,
            'name': user.name,
            'surname': user.surname,
            'age': user.age,
        } for user in users]

    except Exception as ex:
        raise HTTPException(status_code=500)


@route_user.post('/user/register', summary='CreateUser', response_model=UserModel, tags=['User'])
def register_user(user: RegisterUserRequest):
    """
    Регистрация пользователя
    """
    user_object = User(**user.dict())
    s = Session()
    try:
        s.add(user_object)
        s.commit()

        return UserModel.from_orm(user_object)
    finally:
        s.close()

