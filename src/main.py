import uvicorn
from fastapi import FastAPI
from routes.route_city import route_city
from routes.route_user import route_user
from routes.route_picnic import route_picnic

app = FastAPI()

app.include_router(route_city, prefix='/city')
app.include_router(route_user, prefix='/user')
app.include_router(route_picnic, prefix='/picnic')


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=20612, debug=True)
