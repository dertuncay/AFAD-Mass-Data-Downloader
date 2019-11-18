from obspy import Trace, Stream, UTCDateTime
import numpy as np
import os
from datetime import datetime
from obspy.core.util.attribdict import AttribDict

def mag_type(val):
  ''''imagtyp': I    Magnitude type:
  * IMB (52): Bodywave Magnitude
  * IMS (53): Surfacewave Magnitude
  * IML (54): Local Magnitude
  * IMW (55): Moment Magnitude
  * IMD (56): Duration Magnitude
  * IMX (57): User Defined Magnitude'''
  val = val.lower()
  if val == 'mb':
    return 52
  elif val == 'ms':
    return 53
  elif val == 'ml':
    return 54
  elif val == 'mw':
    return 55
  elif val == 'md':
    return 56
  else:
    return 0

def mag_seperator(val):
  ''' Checks if multiple magnitude types are associated with the earthquake.
  If so, following hierarchy is considered:
  1. Mw
  2. Ml
  3. Ms
  4. Md
  5. Mb'''
  val = val.lower()
  mags = val.split(',')
  mags = [w.replace('\r', '') for w in mags]
  mags = [w.replace('\n', '') for w in mags]
  magnitudes = []; mag_types = [];
  for mag in mags:
    if mag[0] == ' ':
      mag = mag[1:]
    mag,imagtyp = mag.split(' ')
    magnitudes.append(mag)
    mag_types.append(imagtyp)
  if 'mw' in mag_types:
    idx = mag_types.index('mw')
    return magnitudes[idx], mag_type(mag_types[idx])
  elif 'ml' in mag_types:
    idx = mag_types.index('ml')
    return magnitudes[idx], mag_type(mag_types[idx])
  elif 'ms' in mag_types:
    idx = mag_types.index('ms')
    return magnitudes[idx], mag_type(mag_types[idx])
  elif 'md' in mag_types:
    idx = mag_types.index('md')
    return magnitudes[idx], mag_type(mag_types[idx])
  elif 'mb' in mag_types:
    idx = mag_types.index('mb')
    return magnitudes[idx], mag_type(mag_types[idx])
    return
  
def txt2sac(txt,output_dir = os.getcwd()):
  ''' This function will convert txt file to SAC file'''
  with open(txt) as eqfile:
    if os.stat(txt).st_size == 0:
      print(txt + ' is empty')
      return
    head = [next(eqfile) for x in range(14)]
      
  head = [line.rstrip('\n') for line in head]
  hd =  AttribDict()
  hd['sac'] = AttribDict()
  # Retrieve Event Information
  # Retrieve EventTime
  s = ''.join(i for i in head[2] if i.isdigit())
  evtime = datetime.strptime(s, '%Y%m%d%H%M%S%f')
  # Retrieve EVLA, EVLO
  _,coors = head[3].split(':')
  # Remove space, N and E 
  coors = coors.replace(' ','')
  coors = coors.replace('N','')
  coors = coors.replace('E','')
  evla,evlo = coors.split('-')
  hd['sac'].evla = float(evla.replace(',','.')); hd['sac'].evlo = float(evlo.replace(',','.'))
  # Retrieve EVDP
  _,depth = head[4].split(':')
  evdp = depth.replace(' ','')
  hd['sac'].evdp = float(evdp)
  # Retrieve MAG
  _,mags = head[5].split(':')
  # Check if multiple Magnitude types are associated with the earthquake
  if ',' in mags:
    mag,imagtyp = mag_seperator(mags)
    hd['sac'].imagtyp = imagtyp
  else:
    _, mag,imagtyp = mags.split(' ')
    hd['sac'].imagtyp = mag_type(imagtyp)
  hd['sac'].mag = float(mag.replace(',','.'))
  # Retrieve Station Information
  # Assign Network
  hd['network'] = 'AFAD'
  # Assing Location
  hd['location'] = 00
  # Retrieve KSTNM
  _,stnm = head[8].split(':')
  kstnm = stnm.replace(' ','')
  hd['station'] = kstnm
  # Retrieve STLA, STLO
  _,coors = head[7].split(':')
  # Remove space, N and E 
  coors = coors.replace(' ','')
  coors = coors.replace('N','')
  coors = coors.replace('E','')
  stla,stlo = coors.split('-')
  hd['sac'].stla = float(stla.replace(',','.')); hd['sac'].stlo = float(stlo.replace(',','.'))
  # Retrieve STEL
  _,el = head[8].split(':')
  stel = el.replace(' ','')
  hd['stel'] = float(stel.replace(',','.'))
  # Retrieve Record Information
  # Retrieve Recordtime
  s = ''.join(i for i in head[11] if i.isdigit())
  starttime = datetime.strptime(s, '%d%m%Y%H%M%S%f')
  hd['starttime'] = UTCDateTime(starttime)
  hd['sac'].o = UTCDateTime(starttime) - UTCDateTime(evtime) 
  # Retrieve NPTS
  _,nptss = head[12].split(':')
  npts = nptss.replace(' ','')
  hd['npts'] = int(npts)
  # Retrieve DELTA
  _,dt = head[13].split(':')
  delta = dt.replace(' ','')
  hd['delta'] = float(delta.replace(',','.'))
  hd['sampling_rate'] = 1/hd['delta']
  hd['endtime'] = hd['starttime'] + hd['npts']*hd['delta']
  hd['sac'].lcalda = 1; hd['sac'].lovrok = 1
  eqfile.close()
  # Read Waveform
  with open(txt) as eqfile:
    wfs = eqfile.readlines()[18:]
  wfs = [line.rstrip('\n') for line in wfs]
  wfs = [line.split(' ') for line in wfs]
  wfs = [list(filter(None, line)) for line in wfs]
  e = []; n = []; z = [];
  for line in wfs:
    n.append(line[0])
    e.append(line[1])
    z.append(line[2])
  #East
  tracee = Trace(np.asarray(e))
  hd['channel'] = 'HGE'
  tracee.stats = hd
  st = Stream(traces=[tracee])
  st.write(os.path.join(output_dir,st[0].id + '.SAC'), format='SAC')
  #North
  tracen = Trace(np.asarray(n))
  hd['channel'] = 'HGN'
  tracen.stats = hd
  st = Stream(traces=[tracen])
  st.write(os.path.join(output_dir,st[0].id + '.SAC'), format='SAC')
  #Vertical
  tracez = Trace(np.asarray(z))
  hd['channel'] = 'HGZ'
  tracez.stats = hd
  st = Stream(traces=[tracez])
  st.write(os.path.join(output_dir,st[0].id + '.SAC'), format='SAC')
  return
