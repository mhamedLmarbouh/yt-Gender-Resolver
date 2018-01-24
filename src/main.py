from time import time
import requests

t=time()
rp=requests.get('https://www.googleapis.com/plus/v1/people/109037766917854562036?key=AIzaSyBMrNA6dW6j5Rx-gqqQtKD8iYpK4nmPUpY').json()
print(time()-t)
print(rp.keys())