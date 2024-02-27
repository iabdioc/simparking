'''
@ IOC - Joan Quintana - 2024 - CE IABD

curl -X POST -H "Content-Type: application/json" -d '{
  "matricula": "6897 JWK",
  "registres": "3600,7.5,0.31;2000,21.0,2.88;4000,12.4,4.52;2500,11.3,6.47;800,15.0,2.63"
}' http://localhost:5000/prediccio
'''

import json
import requests

API_ENDPOINT = "http://localhost:5000/prediccio"

data = {'matricula': '6897 JWK',
        'registres': '3600,7.5,0.31;2000,21.0,2.88;4000,12.4,4.52;2500,11.3,6.47;800,15.0,2.63'
      }

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

r = requests.post(url=API_ENDPOINT, data=json.dumps(data), headers=headers)
resposata = r.json()
print(r.json())
print("El cotxe {:s} pertany al {:s}".format(r.json()['matricula'], r.json()['tipus']))
