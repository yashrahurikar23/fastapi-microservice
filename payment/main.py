from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks

from redis_om import get_redis_connection, HashModel

from starlette.requests import Request
import requests, time

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=['http://localhost:3000'],
  allow_methods=['*'],
  allow_headers=['*'],

)

# This will be a separate DB from the inventory DB since this is a separate microservice
redis = get_redis_connection(
  host='redis-18172.c1.asia-northeast1-1.gce.cloud.redislabs.com',
  port=18172,
  password='hFlM45JriYnP4t0A0SpKBrD042wmUOIx',
  decode_responses=True
)

class Order(HashModel):
  product_id: str
  price: float
  fee: float
  total: float
  quantity: int
  status: str # pending, completed, refunded

  class Meta:
    database = redis


#Order CRUD APIs
@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks): # id, quantity
  body = await request.json()

  req = requests.get('http://localhost:8000/products/%s' % body['id'])

  product = req.json()

  order = Order(
    product_id = body['id'],
    price = product['price'],
    fee = 0.2 * product['price'],
    total = 1.2 * product['price'],
    quantity = body['quantity'],
    status = 'pending'
  )

  background_tasks.add_task(order_completed, order)

  order.save()

  return order 


@app.get('/orders')
def all():
  orders = Order.all_pks()
  return [format_order(pk) for pk in orders]

@app.get('/orders/{pk}')
def get(pk: str):
  return Order.get(pk)

@app.delete('/orders/{pk}')
def delete(pk: str):
  return Order.get(pk)

def format_order(pk: str):
  order = Order.get(pk)
  
  return order

def order_completed(order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed', order.dict(), '*')