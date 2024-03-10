""" @ IOC - Joan Quintana - 2024 - CE IABD """
import json
import requests

host = '0.0.0.0'
port = '8001'

url = f'http://{host}:{port}/invocations'

headers = {
		'Content-Type': 'application/json',
}

test_data = {
"dataframe_split": {
"columns": ["matricula", "durada", "hora", "dia_setmana_dec"],
"data": [
	["6897 JWK", 12195, 12.2, 6.5], ["6897 JWK", 11881, 11.2, 6.5], ["6897 JWK", 12885, 11.5, 6.5],
	["6897 JWK", 10549, 11.1, 6.5], ["6897 JWK", 2359, 11.6, 6.5], ["3560 ROQ", 7197, 21.5, 6.9],
	["3560 ROQ", 4941, 21.1, 5.9], ["3560 ROQ", 13461, 20.1, 6.8], ["3560 ROQ", 13818, 19.4, 5.8],
	["3560 ROQ", 11251, 19.9, 6.8]
	]
}}

json_string = json.dumps(test_data)
r = requests.post(url=url, headers=headers, data=json_string)

print(f'Predictions: {r.text}')
