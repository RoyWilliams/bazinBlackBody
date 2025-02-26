""""
Running the BazinBlackBody fit on an LSST alert read from a file
"""
import json

objectId = 99999999999
file = 'sample_alert/%d.json' % objectId
alert = json.loads(open(file).read())

from bazinBlackBody import BBBEngine
BE = BBBEngine.BBB('LSST', verbose=True)

(dicte, dictb) =  BE.make_fit(alert)
if dicte: 
    BE.plot(alert, dicte, 'image/%s_e.png'%objectId)
if dictb: 
    print('Peak is %f at time %f' % (dictb['peakValue'], dictb['peakTime']))
    BE.plot(alert, dictb, 'image/%s_b.png'%objectId)
