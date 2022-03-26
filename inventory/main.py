from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=['http://localhost:3000'],
  allow_methods=['*'],
  allow_headers=['*'],

)

redis = get_redis_connection(
  host='redis-18172.c1.asia-northeast1-1.gce.cloud.redislabs.com',
  port=18172,
  password='hFlM45JriYnP4t0A0SpKBrD042wmUOIx',
  decode_responses=True
)

class Product(HashModel):
  name: str
  price: float
  quantity: int

  class Meta:
    database = redis

#Product CRUD APIs
@app.post('/products')
def create(product: Product):
  return product.save()

@app.get('/products')
def all():
  products = Product.all_pks()
  return [format_product(pk) for pk in products]

@app.get('/products/{pk}')
def get(pk: str):
  return Product.get(pk)

@app.delete('/products/{pk}')
def delete(pk: str):
  return Product.get(pk)

def format_product(pk: str):
  product = Product.get(pk)
  
  return {
    'id': product.pk,
    'name': product.name,
    'price': product.price,
    'quantity': product.quantity
  }
