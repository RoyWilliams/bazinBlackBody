import json

objectId = 99999999999
file = 'sample_alert/%d.json' % objectId
alert = json.loads(open(file).read())

import BBBEngine
BE = BBBEngine.BBB('LSST', verbose=True)
BE.get_lc(alert)
(dicte, dictb) =  BE.make_fit(alert)
if dicte: 
    BE.plot(alert, dicte, 'image/%s.png'%objectId)
if dictb: 
    BE.plot(alert, dictb, 'image/%s.png'%objectId)
