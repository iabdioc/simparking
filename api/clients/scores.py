'''
@ IOC - Joan Quintana - 2024 - CE IABD
'''
import requests

url = "http://localhost:5000/scores"
response = requests.get(url)

print(response.text)
print("homogeneïtat: {:.2f}".format(response.json()['h']))
