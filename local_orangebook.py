import urllib2, urlparse, os, re
import BeautifulSoup
from zipfile import ZipFile
from time import strftime

def get_orangebook():
    URL = 'http://www.fda.gov/Drugs/InformationOnDrugs/ucm129689.htm'
    page = urllib2.urlopen(URL).read()
    bs = BeautifulSoup.BeautifulSoup(page)

    orangebook = [link for link in bs.findAll('a') if 'Orange Book Data Files (compressed)' in link.renderContents()]

    ob_link = orangebook.pop()
    ob_link = ob_link.get('href')
    download_link = urlparse.urljoin(URL, ob_link)

    #Function to download file
    def dlfile(url):
        # Open our local file for writing
        f = urllib2.urlopen(url)
        with open(os.path.basename(url), "wb") as local_file:
            local_file.write(f.read())
        return local_file.name

    dlfile(download_link)

    zipfiles = dlfile(download_link)
    zf = ZipFile(zipfiles)

    #Using REGEX to find txt file, naming inconsistent, thanks FDA
    match = [target for target in zf.namelist() if re.match(re.compile('[pP]roducts?.txt'),target)]
    
    #Select 1st and only element from list
    products = zf.extract(match.pop())

    date_info = strftime("%Y_%m_%d")

    #Changing the ~ to |
    infile = open(products, 'r')
    outfile = open(date_info + ' products_to_load.csv', 'w')  
    oldtext = infile.read()
    newtext = oldtext.replace('~','|')
    outfile.write(newtext)

    infile.close()
    outfile.close()

get_orangebook()

#Remove unnecessary files
file_list = [x for x in os.listdir('.') if re.match('.*\.zip|.*\.txt',x)]

for f in file_list:
    os.remove(f) 