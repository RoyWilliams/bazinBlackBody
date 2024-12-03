""""
Running the BazinBlackBody fit on an LSST alert read from a file
"""
import json

objectId = 99999999999
file = 'sample_alert/%d.json' % objectId
alert = json.loads(open(file).read())

import BBBEngine
BE = BBBEngine.BBB('LSST', verbose=True)

BE.read_alert(alert)

(dicte, dictb) =  BE.make_fit(alert)
if dicte: 
    BE.plot(alert, dicte, 'image/%s_e.png'%objectId)
elif dictb: 
    BE.plot(alert, dictb, 'image/%s_b.png'%objectId)
else:
    print('Could not make fit')
