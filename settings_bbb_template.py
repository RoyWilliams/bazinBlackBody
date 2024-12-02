# The array of wavelengths then their names
WL    = [0.380, 0.500, 0.620, 0.740, 0.880, 1.000, ]
BANDS = ['u',   'g',   'r'  , 'i'  , 'z'  , 'y'    ]

# When fitting a light curve, try to find this many FP fluxes
# to put at the beginning
N_FORCED  = 4

# for using annotate.py
API_TOKEN = 'lasair AI token here'
TOPIC_IN  = 'your feeder query topic name'
TOPIC_OUT = 'your annotator name'
IMAGE_DIR = '/mnt/cephfs/roy/BBBimages/'
URL_ROOT  = 'https://static.lasair.lsst.ac.uk/ztf/BBBimages/'
GROUP_ID  = 'LASAIR93'
MAX_ALERT = 200

