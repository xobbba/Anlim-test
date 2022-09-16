import datetime as dt
import uvicorn
from typing import Union
from fastapi import FastAPI, HTTPException, Query
from database import engine, Session, Base, City, User, Picnic, PicnicRegistration
from external_requests import CheckCityExisting, GetWeatherRequest
from models import RegisterUserRequest, UserModel
from sqlalchemy import func, desc, asc
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI()


@app.post('/city', summary='Create City', description='Создание города по его названию', tags=['City'])
def create_city(city: str = Query(description="Название города", default=None)):
    if city is None:
        raise HTTPException(status_code=400, detail='Параметр city должен быть указан')
    check = CheckCityExisting()
    if not check.check_existing(city):
        raise HTTPException(status_code=400, detail='Параметр city должен быть существующим городом')

    city_object = Session().query(City).filter(City.name == city.capitalize()).first()
    if city_object is None:
        city_object = City(name=city.capitalize())
        s = Session()

        s.add(city_object)
        s.commit()

    return {'id': city_object.id, 'name': city_object.name, 'weather': city_object.weather}


@app.get('/city', summary='Get Cities', tags=['City'])
def cities_list(q: str = Query(description="Название города", default=None)):
    """
    Получение списка городов
    """
    if q is None:
        raise HTTPException(status_code=400, detail='Параметр города должен быть указан')

    try:
        cities = Session().query(City).filter(City.name == q)  # Фильтр поиска определенного города

        return [{
            'id': city.id,
            'name': city.name,
            'weather': city.weather
        } for city in cities]

    except Exception as ex:
        print(ex)


@app.get('/users', summary='', tags=['User'])  # Исправлено с post запроса на get.
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


@app.post('/user/register', summary='CreateUser', response_model=UserModel, tags=['User'])
def register_user(user: RegisterUserRequest):
    """
    Регистрация пользователя
    """
    user_object = User(**user.dict())
    s = Session()
    try:
        s.add(user_object)
        s.commit()
    finally:
        s.close()

    return UserModel.from_orm(user_object)


@app.get('/picnic', summary='All Picnics', tags=['Picnic'])
def all_picnics(datetime: dt.datetime = Query(default=None, description='Время пикника (по умолчанию не задано)'),
                past: bool = Query(default=True, description='Включая уже прошедшие пикники')):
    """
    Список всех пикников
    """
    picnics = Session().query(Picnic)
    if datetime is not None:
        picnics = picnics.filter(Picnic.time == datetime)
    if not past:
        picnics = picnics.filter(Picnic.time >= dt.datetime.now())

    return [{
        'id': pic.id,
        'city': Session().query(City).filter(City.id == pic.id).first().name,
        'time': pic.time,
        'users': [
            {
                'id': pr.user.id,
                'name': pr.user.name,
                'surname': pr.user.surname,
                'age': pr.user.age,
            }
            for pr in Session().query(PicnicRegistration).filter(PicnicRegistration.picnic_id == pic.id)],
    } for pic in picnics]


@app.post('/picnic', summary='Picnic Add', tags=['Picnic'])
def picnic_add(city_id: int = None, datetime: dt.datetime = None):
    s = Session()
    try:
        city = Session().query(City).filter(City.id == city_id).first()
        if not city:
            raise HTTPException(status_code=400, detail='Неверно указан gorod')

        p = Picnic(city_id=city_id, time=datetime)
        s.add(p)
        s.commit()
    except SQLAlchemyError:
        raise HTTPException(status_code=500)
    finally:
        s.close()

    return {
        'id': p.id,
        'city': city.name,
        'time': p.time,
    }


@app.post('/picnic/register', summary='Picnic Registration', tags=['Picnic'])
def register_to_picnic(user_id: int = Query(default=None),
                       picnic_id: int = Query(default=None)):
    """
    Регистрация пользователя на пикник
    (Этот эндпойнт необходимо реализовать в процессе выполнения тестового задания)
    """
    # TODO: Сделать логику
    s = Session()
    try:
        picnic = s.query(Picnic).filter(Picnic.id == picnic_id).first()
        if not picnic:
            raise HTTPException(status_code=400, detail='Данного id picnic не существует')

        user = s.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail='Данного id user не существует')

        registration = PicnicRegistration(user_id=user_id, picnic_id=picnic_id)
        s.add(registration)
        s.commit()

        return {
            'id': registration.id
        }

    except Exception:
        raise HTTPException(status_code=500)
    finally:
        s.close()


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=20612, debug=True)
