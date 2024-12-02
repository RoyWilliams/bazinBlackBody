import json
import settings_bbb
from lasair import LasairError, lasair_client as lasair
endpoint = "https://lasair-ztf.lsst.ac.uk/api"
lasair_api = lasair(settings_bbb.API_TOKEN)

objectId = 'ZTF24absojni'
alert = lasair_api.objects([objectId])[0]
with open('sample_alert/ZTF24absojni.json', 'w') as f:
    f.write(json.dumps(alert))


import BBBEngine
BE = BBBEngine.BBB('ZTF', verbose=True)
BE.read_alert(alert)
(dicte, dictb) =  BE.make_fit(alert)
if dicte: 
    BE.plot(alert, dicte, 'image/%s.png'%objectId)
if dictb: 
    BE.plot(alert, dictb, 'image/%s.png'%objectId)
