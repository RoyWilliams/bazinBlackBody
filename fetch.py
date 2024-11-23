import json, sys, settings, random
from runBBB import *
import lasair

# This function deals with an object once it is received from Lasair
def handle_object(objectId, L, topic_out):
    dict = run(objectId, L, verbose=verbose)

    if not dict:
        return 0

    if 'k' in dict:
        classification = 'exp'
    else:
        classification = 'bazin'
    explanation    = ''
    # first character of classification is b or e
    try:
        url = settings.URL_ROOT + '%s_%s.png' % (objectId, classification[0])   
    except:
        url = ''

    # now we annotate the Lasair data with the classification
    L.annotate(
        topic_out, 
        objectId, 
        classification,
        version='0.1', 
        explanation=explanation, 
        classdict=dict, 
        url=url)
    print(objectId, '-- annotated!\n')
    return 1

#####################################
verbose = False
if len(sys.argv) > 1 and sys.argv[1] == 'verbose':
    verbose = True
# first we set up pulling the stream from Lasair
# a fresh group_id gets all, an old group_id starts where it left off
#group_id = 'gid%04d' % random.randint(1, 1000)
group_id = settings.GROUP_ID

# a filter from Lasair, example 'lasair_2SN-likecandidates'
topic_in = settings.TOPIC_IN

# kafka consumer that we can suck from
consumer = lasair.lasair_consumer('kafka.lsst.ac.uk:9092', group_id, topic_in)

# the lasair client will be used for pulling all the info about the object
# and for annotating it
L = lasair.lasair_client(settings.API_TOKEN)

# TOPIC_OUT is an annotator owned by a user. API_TOKEN must be that users token.
topic_out = settings.TOPIC_OUT

# just get a few to start
max_alert = settings.MAX_ALERT

n_alert = n_annotate = 0
while n_alert < max_alert:
    msg = consumer.poll(timeout=20)
    if msg is None:
        break
    if msg.error():
        print(str(msg.error()))
        break
    jsonmsg = json.loads(msg.value())
    objectId       = jsonmsg['objectId']
    n_alert += 1

# Lets just see what we have before making any annotations
    n_annotate += handle_object(objectId, L, topic_out)

if verbose:
    print('Annotated %d of %d objects' % (n_annotate, n_alert))
