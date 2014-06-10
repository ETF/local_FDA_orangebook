"""
Pull Latest DMF in prep for SQL loading
"""

import requests
import urlparse
from BeautifulSoup import BeautifulSoup
from zipfile import ZipFile
from time import strftime
import os
import pandas as pd

def get_dmf():
    """Downloads DMF, convert to CSV for SQL"""

    URL = """http://www.fda.gov/drugs/developmentapprovalprocess/
                formssubmissionrequirements/drugmasterfilesdmfs/default.htm"""
    bs = BeautifulSoup(requests.get(URL).content)

    dmf = [link for link in bs.findAll('a')
                if 'DMF zip file' in link.renderContents()]

    ob_link = dmf.pop()
    ob_link = ob_link.get('href')
    download_link = urlparse.urljoin(URL, ob_link)

    def dlfile(url):
        f = requests.get(url)
        with open(os.path.basename(url), "wb") as local_file:
            local_file.write(f.content)
        return local_file.name

    dlfile(download_link)

    zipfiles = dlfile(download_link)
    zf = ZipFile(zipfiles)

    zip_contents = zf.namelist()
    match = [target for target in zip_contents if target.endswith('.xls')]
    filename = str(match[0])

    zf.extract(match.pop())
    master = (pd.read_excel(filename, sheetname='Sheet1',
                    skiprows=1, index_col='DMF#', encoding='UTF-8'))

    nameoutput = 'dmf_to_load_' + strftime('%Y%m%d')
    master.to_csv(nameoutput + '.csv', encoding='UTF-8', sep='|')

get_dmf()
