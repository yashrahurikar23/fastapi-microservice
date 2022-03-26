from main import redis, Order
import time

key = 'order_refunded'
group = 'payment_group'

try:
  redis.xgroup_create(key, group)
except:
  print('Group already exists!')

while True:
  try:
    results = redis.xreadgroup(group, key, { key: '>' }, None)
    
    if results != []:
      for result in results:
        obj = result[1][0][1]
        product = Order.get(obj['product_id'])
        product.quantity = product.quantity - int(obj['quantity'])
        product.save()


  except Exception as e:
    print(str(e))
  time.sleep(1)
