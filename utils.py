import mechanize, re, os, requests, warnings, urllib.request, shutil
import pandas as pd
from bs4 import BeautifulSoup 
from datetime import datetime
warnings.filterwarnings('ignore')

def inputparameter_fixer(par_min,par_max,par_type):
  ''' Function will use magnitudes of 0 and 9.9 for minimum and maximum magnitudes when one of them is not given.
  Minimum and maximum depth will be assigned as 0 and 999km when one of them is not given.'''
  if par_type == 'm':
    if len(par_min) == 0:
      par_min == 0
    elif len(par_max) == 0:
      par_max = 9.9
  elif par_type == 'd':
    if len(par_min) == 0:
      par_min == 0
    elif len(par_max) == 0:
      par_max = 999
  return par_min, par_max    

def load_input(brwsr,inputs='input.dat'):
  with open(inputs, 'r') as f:
    parameters = []
    for count, line in enumerate(f, start=1):
      line = line.rstrip('\n')
      print(line)
      if count % 2 == 0:
        line = line.replace(' ', '')
        parameters.append(line)
  # Start Time
  start_day, start_month, start_year = parameters[0].split('/')
  start_day = brwsr.find_control(name='from_day', type='select').get(str(start_day))
  start_day.selected = True
  start_month = brwsr.find_control(name='from_month', type='select').get(str(start_month))
  start_month.selected = True
  start_year = brwsr.find_control(name='from_year', type='select').get(str(start_year))
  start_year.selected = True
  # Stop Time
  end_day, end_month, end_year = parameters[1].split('/')
  end_day = brwsr.find_control(name='to_day', type='select').get(str(end_day))
  end_day.selected = True
  end_month = brwsr.find_control(name='to_month', type='select').get(str(end_month))
  end_month.selected = True
  end_year = brwsr.find_control(name='to_year', type='select').get(str(end_year))
  end_year.selected = True
  # Latitudes
  if len(parameters[2]) != 0:
    start_lat, stop_lat = parameters[2].split('-')
  else:
    start_lat = str(34.00)
    stop_lat = str(43.00)
  brwsr['from_epi_lat'] = str(start_lat)
  brwsr['to_epi_lat'] = str(stop_lat)
  # Longitudes
  if len(parameters[3]) != 0:
    start_lon = str(24.00)
    stop_lon = str(45.82)
  else:
    start_lon, stop_lon = parameters[3].split('-')
  brwsr['from_epi_lon'] = str(start_lon)
  brwsr['to_epi_lon'] = str(stop_lon)
  # Depth
  if len(parameters[4]) != 0:
    start_d, stop_d = parameters[4].split('-')
    if len(start_d) + len(stop_d) != 0:
      start_d, stop_d = inputparameter_fixer(start_d, stop_d,'d')
    brwsr['from_depth'] = str(start_d)
    brwsr['to_depth'] = str(stop_d)
  # MD
  if len(parameters[5]) != 0:
    md_min, md_max = parameters[5].split('-')
    if len(md_min) + len(md_max) != 0:
      md_min, md_max = inputparameter_fixer(md_min, md_max,'m')
    brwsr['from_md'] = str(md_min)
    brwsr['to_md'] = str(md_max)
  # ML
  if len(parameters[6]) != 0:
    ml_min, ml_max = parameters[6].split('-')
    if len(ml_min) + len(ml_max) != 0:
      ml_min, ml_max = inputparameter_fixer(ml_min, ml_max,'m')
    brwsr['from_ml'] = str(ml_min)
    brwsr['to_ml'] = str(ml_max)
  # MS
  if len(parameters[7]) != 0:
    ms_min, ms_max = parameters[7].split('-')
    if len(ms_min) + len(ms_max) != 0:
      ms_min, ms_max = inputparameter_fixer(ms_min, ms_max,'m')
    brwsr['from_ms'] = str(ms_min)
    brwsr['to_ms'] = str(ms_max)
  # MW
  if len(parameters[8]) != 0:
    mw_min, mw_max = parameters[8].split('-')
    if len(mw_min) + len(mw_max) != 0:
      mw_min, mw_max = inputparameter_fixer(mw_min, mw_max,'m')
    brwsr['from_mw'] = str(mw_min)
    brwsr['to_mw'] = str(mw_max)
  # MB
  if len(parameters[9]) != 0:
    mb_min, mb_max = parameters[9].split('-')
    if len(mb_min) + len(mb_max) != 0:
      mb_min, mb_max = inputparameter_fixer(mb_min, mb_max,'m')
    brwsr['from_mb'] = str(mb_min)
    brwsr['to_mb'] = str(mb_max)
  return brwsr

def readable_results(brwsr):
  #search_result(brwsr)
  response = brwsr.submit()
  text = response.read()
  soup = BeautifulSoup(text)
  return soup

def make_search(soup,output_name=datetime.now().strftime('%Y-%m-%d%H.%M.%S'),search_result=True,earthquake_results=True,get_data=True):
  ''' Making the search by using input parameters
  input: input file
  output_name: give a name of your search
  search_result: Download search results as a csv file
  earthquake_results: Download paramaters of each earthquake as a csv file
  get_data: download each waveform of each earthquake
  '''
  if len(output_name) == 0:
    output_name=datetime.now().strftime('%Y-%m-%d%H.%M.%S')
  len_table = len(soup.findAll('table',attrs={'class':'tableType_01'}))
  # If there is no earthquake, then return
  if len_table == 0:
    print('No Earthquake!')
    return
  table = soup.findAll('table',attrs={'class':'tableType_01'})[0]
  eq_table  = pd.DataFrame(columns=[],index=[0])
  new_table = pd.DataFrame(columns=['EVENT NO','EVENT ID','Date','Time','Epicenter Latitude','Epicenter Longitude','Depth (km)','ML','MD','MS','MW','MB','City / Town','No of sta'],index=[0])
  row_marker = 0
  eq_links = [];
  # Get Results
  for row in table.find_all('tr'):
    column_marker = 0
    columns = row.find_all('td')
    for i, column in enumerate(columns):
      # Get the link of the EVENT ID
      if i == 1:
        href = column.find_all('a', href=True)
        if len(href) >= 1:
          eq_links.append(str('http://kyhdata.deprem.gov.tr/') + href[0]['href'])
      new_table.iat[row_marker,column_marker] = column.get_text()
      column_marker += 1
    eq_table = eq_table.append(new_table, ignore_index=True, sort=False)
  print('Number of Earthquakes: ' + str(len(eq_links)))
  eq_table = eq_table.iloc[2:]

  
  # Check if output_name exist
  if os.path.isdir(output_name):
    print(str(output_name) + ' exists. It is renamed as ' + str(output_name) + '_old')
    if os.path.isdir(str(output_name) + '_old'):
      print(str(output_name) + '_old is also exist. It is deleted.')
      shutil.rmtree(os.path.join(os.getcwd(), str(output_name) + '_old') )
    os.rename(str(output_name), str(output_name) + '_old')
  # Create Search Folder
  os.mkdir(output_name)
  # Save Results to csv file
  if search_result == True:
    eq_table.to_csv(output_name + '/search.csv',index=False)
  # Go Inside Each Earthquake
  for eq_counter, link in enumerate(eq_links):
    # Create Earthquake Folder
    os.mkdir(output_name + '/' + str(eq_table['EVENT ID'][eq_table.first_valid_index() + eq_counter]))
    # Create Empty CSVs
    wfs_table  = pd.DataFrame(columns=[],index=[0])
    new_table = pd.DataFrame(columns=['STATION NO','RECORD FILE','N-S PGA','E-W PGA','U-D PGA','RECORD INFO.','STATION CODE','Station City','Rjb','Rrup','Repi','Rhyp'],index=[0])
    # Open Link
    r = requests.get(link)
    soup = BeautifulSoup(r.content)
    # Find the Table
    table = soup.findAll('table',attrs={'id':'example'})[0] #('table', attrs={'class':'tableType_01 dataTable no-footer'})
    row_marker = 0
    wf_links = [];
    # Get Results
    for row in table.find_all('tr'):
      column_marker = 0
      columns = row.find_all('td')
      for i, column in enumerate(columns):
        # Get the link of the EVENT ID
        if i == 1:
          href = column.find_all('a', href=True)
          if len(href) >= 1:
            wf_links.append(str('http://kyhdata.deprem.gov.tr/') + href[0]['href'])
        new_table.iat[row_marker,column_marker] = column.get_text()
        column_marker += 1
        
      wfs_table = wfs_table.append(new_table, ignore_index=True, sort=False)
    print('Number of Stations in earthquake ' + str(eq_table['EVENT ID'][eq_table.first_valid_index() + eq_counter]) + ' is ' + str(len(wf_links)))
    # Save Results to csv file
    wfs_table = wfs_table.iloc[2:]
    if earthquake_results == True:
      wfs_table.to_csv(output_name + '/' + str(eq_table['EVENT ID'][eq_table.first_valid_index() + eq_counter]) + '/results.csv',index=False)
    
    # Go Inside Each Waveform
    if get_data == True:
      for wf_counter, wf_link in enumerate(wf_links):
        # Find Link
        r = requests.get(wf_link)
        soup = BeautifulSoup(r.content)
        href = soup.find_all('a', href=True)[0]['href'] #('table', attrs={'class':'tableType_01 dataTable no-footer'})
        # Open URL
        urllib.request.urlretrieve('http://kyhdata.deprem.gov.tr/' + href, output_name + '/' + str(eq_table['EVENT ID'][eq_table.first_valid_index() + eq_counter]) + '/' + str(wfs_table['RECORD FILE'][wfs_table.first_valid_index() + wf_counter]) + '.txt')
