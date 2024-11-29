import json, sys
import settings_bbb
from coreBBB import *

is_lsst    = settings_bbb.LSST
verbose    = settings_bbb.VERBOSE

def mag2flux(mag, magerr, magzpsci):
    # flux in microJ
    flux =  math.pow(10, (magzpsci-mag)/2.5)
    fluxerr = magerr * flux * 0.92  # ln(10)/2.5
    return (flux, fluxerr)

def get_lc(alert):
    if settings_bbb.LSST:
        objectId = alert['diaObject']['diaObjectId']
        sources  = alert['diaSourcesList']
        forced   = alert['diaForcedSourcesList']
        mjdkey   = 'midpointMjdTai'
        bandkey  = 'band'
    else:
        objectId = alert['objectId']
        sources  = [c for c in alert['candidates'] if 'candid' in c]
        forced   = alert['forcedphot']
        mjdkey   = 'mjd'
        bandkey  = 'fid'

    lc = {
        'objectId': objectId,
        'mjd_discovery': 0,
        't':        [],  # days after discovery
        'bandindex':[],  # index of the waveband
        'flux':     [],  # flux in microJ or nanoJ
        'fluxerr':  []
         }
    lc['TNS'] = alert.get('TNS', None)

    sources.sort(key = lambda c: c[mjdkey])
    lc['mjd_discovery'] = sources[0][mjdkey]

    if len(sources) < 5:
        return None
    if verbose:
        print('%s has %s' % (objectId, len(sources)))
    for c in sources:
        if is_lsst:
            lc['bandindex']     .append(settings_bbb.BANDS.index(c['band']))
            (flux, fluxerr) = (c['psfFlux'], c['psfFluxErr'])
        else:
            lc['bandindex']     .append(c['fid'])
            (flux, fluxerr) = mag2flux(c['magpsf'], c['sigmapsf'], c['magzpsci'])

        lc['t']      .append(c[mjdkey] - lc['mjd_discovery'])
        lc['flux']   .append(flux)
        lc['fluxerr'].append(fluxerr)

    lc['post_discovery'] = lc['t'][-1]
        
    forced.sort(key = lambda f: f[mjdkey])
    
# see if we can find four forced phot points before first detection
    nforced = settings_bbb.N_FORCED

    nforced_found = 0
    for ii in range(len(forced)): # go backwards just past discovery
        i = len(forced)-ii-1
        f = forced[i]
        if f[mjdkey] < lc['mjd_discovery']:
            t = f[mjdkey]-lc['mjd_discovery']
            lc['t'].insert(0, t)
            if is_lsst:
                lc['bandindex'].insert(0, settings_bbb.BANDS.index(f[bandkey]))
                (flux, fluxerr) = (f['psfFlux'], f['psfFluxErr'])
            else:
                lc['bandindex'].insert(0, f[bandkey])
                (flux, fluxerr) = (f['forcediffimflux'], f['forcediffimfluxunc'])
            lc['flux'].insert(0, flux)
            lc['fluxerr'].insert(0, fluxerr)
            nforced_found += 1
            if nforced_found >= nforced:
                break
    return lc

def make_fit(alert, pexpit0, pbazin0, plotdir=None):
    lc = get_lc(alert)
    if not lc:
        return (None, None)

    tobs = lc['t']
    lobs = [settings_bbb.WL[i] for i in lc['bandindex']]
    fobs = lc['flux']
    npoint = len(lc['t'])
    objectId = lc['objectId']

    dicte = fit_expit(tobs, lobs, fobs, pexpit0)
    if dicte:
        if verbose:
            print('Expit: T= %.2f (g-r=%.3f), k=%.3f' % \
                (dicte['T'], g_minus_r(dicte['T']), dicte['k']))
        filename = '%s_e.png' % objectId
        if plotdir:
            plot(lc, dicte, plotdir+'/'+filename, False)
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
            plot(lc, dictb, plotdir+'/'+filename, True)
        except:
            pass
        dictb['post_discovery'] = lc['post_discovery']
        try:
            dictb['tns_name'] = lc['TNS']['tns_prefix'] +' '+ lc['TNS']['tns_name']
        except:
            dictb['tns_name'] = ''

    return (dicte, dictb)

###################
def run(alert, plotdir=None):
    A = 10000
    T = 8
    t0 = -6
    kr = 1
    kf = 0.1

    pexpit0 = [A, T, kr-kf]
    pbazin0 = [A, T, t0, kr, kf]

    (dicte, dictb) =  make_fit(alert, pexpit0, pbazin0, plotdir)
    if dicte: 
        return dicte
    if dictb: 
        return dictb
    return None

if __name__ == '__main__':
#    file = 'sample_alert/99999999999.json'
#    alert = json.loads(open(file).read())

    from lasair import LasairError, lasair_client as lasair
    endpoint = "https://lasair-ztf.lsst.ac.uk/api"
    objectId = 'ZTF24absojni'
    lasair_api = lasair(settings_bbb.API_TOKEN)
    alert = lasair_api.objects([objectId])[0]

    run(alert, plotdir='image')
