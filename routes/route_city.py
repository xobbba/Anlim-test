from fastapi import APIRouter, HTTPException, Query
from src.database import Session, City
from src.external_requests import CheckCityExisting


route_city = APIRouter()


@route_city.post('/city', summary='Create City', description='Создание города по его названию', tags=['City'])
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


@route_city.get('/city', summary='Get Cities', tags=['City'])
def cities_list(q: str = Query(description="Название города", default=None)):
    """
    Получение списка городов
    """
    if q is None:
        raise HTTPException(status_code=400, detail='Параметр города должен быть указан')

    try:
        cities = Session().query(City).filter(City.id == q)  # Фильтр поиска определенного города

        return [{
            'id': city.id,
            'name': city.name,
            'weather': city.weather
        } for city in cities]

    except Exception as ex:
        print(ex)
