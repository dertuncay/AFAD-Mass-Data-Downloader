from obspy import Trace, Stream, UTCDateTime
import numpy as np
from datetime import datetime
from obspy.core.util.attribdict import AttribDict

def mag_type(val):
  val = val.lower()
  ''''imagtyp': I    Magnitude type:
  * IMB (52): Bodywave Magnitude
  * IMS (53): Surfacewave Magnitude
  * IML (54): Local Magnitude
  * IMW (55): Moment Magnitude
  * IMD (56): Duration Magnitude
  * IMX (57): User Defined Magnitude''',
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
  
def txt2sac(txt):
  ''' This function will convert txt file to SAC file'''
  with open(txt) as eqfile:
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
  hd['sac'].evla = float(evla); hd['sac'].evlo = float(evlo)
  # Retrieve EVDP
  _,depth = head[4].split(':')
  evdp = depth.replace(' ','')
  hd['sac'].evdp = float(evdp)
  # Retrieve MAG
  _,mags = head[5].split(':')
  _, mag,imagtyp = mags.split(' ')
  hd['sac'].mag = float(mag)
  hd['sac'].imagtyp = mag_type(imagtyp)
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
  hd['sac'].stla = float(stla); hd['sac'].stlo = float(stlo)
  # Retrieve STEL
  _,el = head[8].split(':')
  stel = el.replace(' ','')
  hd['stel'] = float(stel)
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
  hd['delta'] = float(delta)
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
  st.write(st[0].id + '.SAC', format='SAC')
  #North
  tracen = Trace(np.asarray(n))
  hd['channel'] = 'HGN'
  tracen.stats = hd
  st = Stream(traces=[tracen])
  st.write(st[0].id + '.SAC', format='SAC')
  #Vertical
  tracez = Trace(np.asarray(z))
  hd['channel'] = 'HGZ'
  tracez.stats = hd
  st = Stream(traces=[tracez])
  st.write(st[0].id + '.SAC', format='SAC')
  return
