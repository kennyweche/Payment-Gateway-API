import json

#data = {'username':'kim','password':'kim'}
data = "{\"id\":\"04ce7522c188855f2cd7907c6746f76a\",\"names\":\"KimKiogora\",\"business_number\":\"874900\"}"
d = json.load(data);

print d

y = json.dumps(d)

print json.dumps(json.loads(d))



