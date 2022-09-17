import datetime as dt
from fastapi import APIRouter, HTTPException, Query
from src.database import Session, City, User, Picnic, PicnicRegistration
from sqlalchemy.exc import SQLAlchemyError

route_picnic = APIRouter()


@route_picnic.get('/picnic', summary='All Picnics', tags=['Picnic'])
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


@route_picnic.post('/picnic', summary='Picnic Add', tags=['Picnic'])
def picnic_add(city_id: int = None, datetime: dt.datetime = None):
    s = Session()
    try:
        city = Session().query(City).filter(City.id == city_id).first()
        if not city:
            raise HTTPException(status_code=400, detail='Неверно указан gorod')

        p = Picnic(city_id=city_id, time=datetime)
        s.add(p)
        s.commit()

        return {
            'id': p.id,
            'city': city.name,
            'time': p.time,
        }
    except SQLAlchemyError:
        raise HTTPException(status_code=500)
    finally:
        s.close()


@route_picnic.post('/picnic/register', summary='Picnic Registration', tags=['Picnic'])
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
