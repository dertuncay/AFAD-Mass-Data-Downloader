from utils import *

# Open website
brwsr = mechanize.Browser()
brwsr.open('http://kyhdata.deprem.gov.tr/2K/kyhdata_v4.php?dst=TU9EVUxFX05BTUU9ZWFydGhxdWFrZSZNT0RVTEVfVEFTSz1zZWFyY2g%3D')
brwsr.select_form(nr = 0)

# Load input parameters to website
brwsr = load_input(brwsr, inputs='input.dat')

# Make search results readable
results = readable_results(brwsr)

# Make Search
make_search(results,output_name='TEST',search_result=True,earthquake_results=True,get_data=True)
