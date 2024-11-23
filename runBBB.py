import json, sys
import settings
from coreBBB import *
from lasair import LasairError, lasair_client as lasair
endpoint = "https://lasair-ztf.lsst.ac.uk/api"

def g_minus_r(T):
    flux_ratio = blackbody(wl[0], T) / blackbody(wl[1], T)
    return 2.5 * math.log10(flux_ratio)

def mag2flux(mag, magerr, magzpsci):
    # flux in microJ
    flux =  math.pow(10, (magzpsci-mag)/2.5)
    fluxerr = magerr * flux * 0.92  # ln(10)/2.5
    return (flux, fluxerr)


def get_lc(objectId, L, nforced, verbose=True):
    result = L.objects([objectId])[0]
    lc = {
        'objectId': objectId,
        'mjd_discovery': 0,
        't':      [],
        'pb':     [],
        'flux':   [],
        'fluxerr':[]
         }
    lc['TNS'] = result.get('TNS', None)
    candidates = [c for c in result['candidates'] if 'candid' in c]
    if len(candidates) < 5:
        return None
    if verbose:
        print('%s has %s' % (objectId, len(candidates)))
    candidates.sort(key = lambda c: c['mjd'])
    lc['mjd_discovery'] = candidates[0]['mjd']
    for c in candidates:
        (flux, fluxerr) = mag2flux(c['magpsf'], c['sigmapsf'], c['magzpsci'])
        lc['t']      .append(c['mjd'] - lc['mjd_discovery'])
        lc['pb']     .append(c['fid'])
        lc['flux']   .append(flux)
        lc['fluxerr'].append(fluxerr)

    lc['post_discovery'] = lc['t'][-1]
        
    forced = result['forcedphot']
    forced.sort(key = lambda f: f['mjd'])
    
    nforced_found = 0
    for ii in range(len(forced)): # go backwards just past discovery
        i = len(forced)-ii-1
        f = forced[i]
        if f['mjd'] < lc['mjd_discovery']:
            t = f['mjd']-lc['mjd_discovery']
            magzpsci = settings.MAGZPSCI
            lc['t'].insert(0, t)
            lc['pb'].insert(0, f['fid'])
            lc['flux'].insert(0, f['forcediffimflux'])
            lc['fluxerr'].insert(0, f['forcediffimfluxunc'])
            nforced_found += 1
            if nforced_found >= nforced:
                break
    return lc

def make_fit(objectId, L, nforced, pexpit0, pbazin0, verbose=True):
    lc = get_lc(objectId, L, nforced, verbose)
    if not lc:
        return (None, None)

    tobs = lc['t']
    lobs = [wl[i] for i in lc['pb']]
    fobs = lc['flux']
    npoint = len(lc['t'])

    dicte = fit_expit(tobs, lobs, fobs, pexpit0, verbose=True)
    if dicte:
        if verbose:
            print('Expit: T= %.2f (g-r=%.3f), k=%.3f' % \
                (dicte['T'], g_minus_r(dicte['T']), dicte['k']))
        filename = '%s_e.png' % objectId
        try:
            plot(lc, dicte, settings.IMAGE_DIR + filename, False)
        except:
            pass
        dicte['post_discovery'] = lc['post_discovery']
        try:
            dicte['tns_name'] = lc['TNS']['tns_prefix'] +' '+ lc['TNS']['tns_name']
        except:
            dicte['tns_name'] = ''

    dictb = fit_bazin(tobs, lobs, fobs, pbazin0)
    if dictb:
        if verbose:
            print('Bazin: T=%.2f (g-r=%.3f), kr=%.3f, kf=%.3f' % \
                (dictb['T'],  g_minus_r(dictb['T']), dictb['kr'], dictb['kf']))
        filename = '%s_b.png' % objectId
        try:
            plot(lc, dictb, settings.IMAGE_DIR + filename, True)
        except:
            pass
        dictb['post_discovery'] = lc['post_discovery']
        try:
            dictb['tns_name'] = lc['TNS']['tns_prefix'] +' '+ lc['TNS']['tns_name']
        except:
            dictb['tns_name'] = ''

    return (dicte, dictb)

###################
def run(objectId, L, verbose=True):
    A = 10000
    T = 8
    t0 = -6
    kr = 1
    kf = 0.1

    pexpit0 = [A, T, kr-kf]
    pbazin0 = [A, T, t0, kr, kf]

# see if we can find four forced phot points before first detection
    nforced = settings.N_FORCED

    (dicte, dictb) =  make_fit(objectId, L, nforced, pexpit0, pbazin0, verbose)
    if dicte: 
        return dicte
    if dictb: 
        return dictb
    return None
