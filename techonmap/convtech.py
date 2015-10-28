import json

with open("techonmap.json") as f: data = json.load(f)

headers=['id','name','address','postcode','city','category','tags','creationyear','description']

print ",".join(headers)
for a in data['features']:
  b = a['properties']
  for h in headers:
    if not h in b or not b[h]:
      b[h] = ""
    else:
      if type(b[h]) == list:
        b[h] = u'|'.join(b[h])
      if type(b[h]) == int:
        b[h] = str(b[h])
      elif type(b[h]) in (str, unicode):
        b[h] = '"%s"' % b[h].encode('utf-8').replace('"', '""')
  print ",".join([b[h] for h in headers])

