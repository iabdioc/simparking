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
"columns": ["durada", "hora", "dia_setmana_dec", "count"],
"data": [[2.732830354476496, -0.9207855070928049, -1.1320593348043717, 3.769733523650502],
[0.26790930806008045, -0.4215349655828905, 1.7062354659081376, -0.19415503682400367],
[-0.9302374156792241, 0.4369914852445514, -0.47976588389927294, -0.45841427418897074]]
}}

json_string = json.dumps(test_data)
r = requests.post(url=url, headers=headers, data=json_string)

print(f'Predictions: {r.text}')
