"""
Running the BazinBlackBody fit on a ZTF alert fetched from Lasair API
"""
import json
import settings_ann

# First set up the Lasair API
from lasair import LasairError, lasair_client as lasair
endpoint = "https://lasair-ztf.lsst.ac.uk/api"
lasair_api = lasair(settings_ann.API_TOKEN)

# Fetch the alert from the API
objectId = 'ZTF24absojni'
alert = lasair_api.objects([objectId])[0]

# Now run the fits
import BBBEngine
BE = BBBEngine.BBB('ZTF', verbose=True)
BE.read_alert(alert)

# Both BazinBlackBody and ExponentialBlackBody fits are attempted
(dicte, dictb) =  BE.make_fit(alert)

if dicte: 
    BE.plot(alert, dicte, 'image/%s_e.png'%objectId)
if dictb: 
    BE.plot(alert, dictb, 'image/%s_b.png'%objectId)

