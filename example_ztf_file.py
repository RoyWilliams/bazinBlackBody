import json
objectId = 'ZTF24absojni'
file = 'sample_alert/%s.json' % objectId
alert = json.loads(open(file).read())

import BBBEngine
BE = BBBEngine.BBB('ZTF', verbose=True)
BE.read_alert(alert)
(dicte, dictb) =  BE.make_fit(alert)
if dicte: 
    BE.plot(alert, dicte, 'image/%s.png'%objectId)
if dictb: 
    BE.plot(alert, dictb, 'image/%s.png'%objectId)
