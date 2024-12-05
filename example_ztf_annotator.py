"""
Running the BazinBlackBody fit as an annotator. Stages are:
(1) Make a filter to pre-select, it comes as TOPIC_IN
(2) Read objectIds that have passed the filter
(3) Get full alert from Laair API
(4) Try to make a BBB fit to the lightcurve
(5) If there's a fit, send annotation back to Lasair
"""
import json, sys, settings_ann, random
from BBB import BBBEngine
import lasair

# first we set up pulling the stream from Lasair
# a fresh group_id gets all, an old group_id starts where it left off
#group_id = 'gid%04d' % random.randint(1, 1000)
group_id = settings_ann.GROUP_ID

# a filter from Lasair, example 'lasair_2SN-likecandidates'
topic_in = settings_ann.TOPIC_IN

# kafka consumer that we can suck from
consumer = lasair.lasair_consumer('kafka.lsst.ac.uk:9092', group_id, topic_in)

# the lasair client will be used for pulling all the info about the object
# and for annotating it
lasair_api = lasair.lasair_client(settings_ann.API_TOKEN)

# TOPIC_OUT is an annotator owned by a user. API_TOKEN must be that users token.
topic_out = settings_ann.TOPIC_OUT

# how many to fetch
max_alert = settings_ann.MAX_ALERT

# Can change defaults for the fitting system here
BE = BBBEngine.BBB('ZTF', verbose=settings_ann.VERBOSE)

# Fetch the objectIds from the pre-filter
n_alert = n_annotate = 0
while n_alert < max_alert:
    msg = consumer.poll(timeout=20)
    if msg is None:
        break
    if msg.error():
        print(str(msg.error()))
        break

    # This will be the SELECTed fields from the pre-filter
    jsonmsg = json.loads(msg.value())
    objectId       = jsonmsg['objectId']

    # Fetch full object info from the API
    alert = lasair_api.objects([objectId])[0]

    # Make the fit(s)
    (fit_e, fit_b) =  BE.make_fit(alert)

    # Make plots; select one of the fits
    fit = None
    if fit_e:
        BE.plot(alert, fit_e, '%s/%s_e.png'% (settings_ann.IMAGE_DIR, objectId))
        classification = 'exp'
        fit = fit_e
    if fit_b:
        BE.plot(alert, fit_b, '%s/%s_b.png'% (settings_ann.IMAGE_DIR, objectId))
        classification = 'bazin'
        fit = fit_b

    # If no fit was converged, go to the next
    if not fit:
        continue

    # Explanation in natural language
    explanation    = ''

    # first character of classification is b or e
    url = settings_ann.URL_ROOT + '%s_%s.png' % (objectId, classification[0])

    # now we annotate the Lasair data with the classification
    lasair_api.annotate(
        topic_out,
        objectId,
        classification,
        version='0.1',
        explanation=explanation,
        classdict=fit,
        url=url)
    print(objectId, '-- annotated!\n')
    n_alert += 1

if settings_ann.VERBOSE:
    print('Annotated %d of %d objects' % (n_annotate, n_alert))
