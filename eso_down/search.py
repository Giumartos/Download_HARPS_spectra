import numpy as np
import os
import astroquery
from sys import maxsize, stdout
np.set_printoptions(threshold = maxsize)
from astropy.time import Time
from datetime import datetime
from starsearch.core import Eso
from starsearch.utils import HMS2deg
from astroquery.simbad import Simbad
Simbad.add_votable_fields('flux(V)')
import eso_down.angle as tt
import requests
from bs4 import BeautifulSoup

class ESOquery:
    """
    ESO query class
    
    Parameters
    ----------
    user: str
        User name used for ESO website login
    store_password : bool
        Optional, stores the password securely in your keyring
        Default: store_password = False
        
    Returns
    -------
    """
    def __init__(self, user='', store_password=False):
        super(ESOquery, self).__init__()
        #user name
        self.user = user
        #login to ESO
        self.eso = Eso()
        if store_password:
            self.eso.login(self.user, store_password=True)
        else:
            self.eso.login(self.user)
        #unlimited number of search results = -1
        self.eso.ROW_LIMIT = -1
        #list of available surveys
        self.surveys = self.eso.list_surveys()
        #default instruments for our package
        self.instruments = np.array(['FEROS', 'HARPS', 'ESPRESSO'])
        #In the future we might include UVES
        self.UVES = np.array(['UVES'])



    def searchStarbef(self, star, instrument = None, date = None, SNRmin = None,SNRmax=None, dist = None, R=None):
        """star, instrument = None, date = None, SNRmin = None,SNRmax=None, dist = None)
        Return phase 3 ESO query for selected star. 
        Includes other options such as instrument, date, and signal-to-noise.
        
        Parameters
        ----------
        star: str
            Name of the star
        instrument: str
            Name of the instrument
            If None: Uses our default instruments
        date: str
            Date to search for obvervation ('YYYY-MM-DD')
            If None: date = '2015-06-03' (date of HARPS upgrade)
        SNRmin: float
            Minimal signal to noise ratio. 
            If None: SNRmin = 1
        SNRmax: float
            Maximum signal to noise
            IF None: SNRmax = 500
        dist: float
            Maximum distance (in arcsec) from RA and DEC
            If None: dist = 30
        R: float
            The resolution
            If None: R = 115000
        
            
        Returns
        -------
        search: table
            Result of the query on ESO arquive
        """
        if not date: 
            date = Time('2015-06-03')
        date = Time(date)
        if not SNRmin: 
            SNRmin = 1
        if not SNRmax:
            SNRmax=500
        if not dist:
            dist=30
        if not R:
            R=115000
        if instrument:
            search = self.eso.query_surveys(surveys=instrument,target=star)
        else:
            search = self.eso.query_surveys(surveys = list(self.instruments), 
                                            target = star)
        
        sSearch=Simbad.query_object(star)
        RAref = tt.ra(sSearch['RA'][0][0:2],sSearch['RA'][0][3:5],sSearch['RA'][0][6:len(sSearch['RA'][0])])    
        RAmin = (RAref - dist)/3600
        RAmax = (RAref+dist)/3600
        decRef = tt.dec(sSearch['DEC'][0][0:3],sSearch['DEC'][0][3:6],sSearch['DEC'][0][6:len(sSearch['DEC'][0])])
        decMin = (decRef-dist)/3600
        decMax = (decRef+dist)/3600

        try:
            search.remove_rows(Time(search['Date Obs']) > date) #Date criteria
            search.remove_rows(search['SNR (spectra)'] < SNRmin) #SNR critetia
            search.remove_rows(search['SNR (spectra)'] > SNRmax) #SNR critetia
            search.remove_rows(search['RA'] < RAmin)
            search.remove_rows(search['RA'] > RAmax)
            search.remove_rows(search['DEC'] < decMin)
            search.remove_rows(search['DEC'] > decMax)
            search.remove_rows(search['R (&lambda;/&delta;&lambda;)'] != R)



        except:
            pass
        return search

    def searchStaraft(self, star, instrument = None, date = None, SNRmin = None,SNRmax=None, dist = None,R=None):
        """star, instrument = None, date = None, SNRmin = None,SNRmax=None, dist = None)
        Return phase 3 ESO query for selected star. 
        Includes other options such as instrument, date, and signal-to-noise.
        
        Parameters
        ----------
        star: str
            Name of the star
        instrument: str
            Name of the instrument
            If None: Uses our default instruments
        date: str
            Date to search for obvervation ('YYYY-MM-DD')
            If None: date = '2015-06-03' (date of HARPS upgrade)
        SNRmin: float
            Minimal signal to noise ratio. 
            If None: SNRmin = 1
        SNRmax: float
            Maximum signal to noise
            IF None: SNRmax = 500
        dist: float
            Maximum distance (in arcsec) from RA and DEC
            If None: dist = 30
        R: float
            The resolution
            If None: R = 115000
        
            
        Returns
        -------
        search: table
            Result of the query on ESO arquive
        """
        if not date: 
            date = Time('2015-06-03')
        date = Time(date)
        if not SNRmin: 
            SNRmin = 1
        if not SNRmax:
            SNRmax=500
        if not dist:
            dist=30
        if not R:
            R=115000
        if instrument:
            search = self.eso.query_surveys(surveys=instrument, target=star)
        else:
            search = self.eso.query_surveys(surveys = list(self.instruments), 
                                            target = star)
        
        sSearch=Simbad.query_object(star)
        RAref = tt.ra(sSearch['RA'][0][0:2],sSearch['RA'][0][3:5],sSearch['RA'][0][6:len(sSearch['RA'][0])])    
        RAmin = (RAref - dist)/3600
        RAmax = (RAref+dist)/3600
        decRef = tt.dec(sSearch['DEC'][0][0:3],sSearch['DEC'][0][3:6],sSearch['DEC'][0][6:len(sSearch['DEC'][0])])
        decMin = (decRef-dist)/3600
        decMax = (decRef+dist)/3600

        try:
            search.remove_rows(Time(search['Date Obs']) < date) #Date criteria
            search.remove_rows(search['SNR (spectra)'] < SNRmin) #SNR critetia
            search.remove_rows(search['SNR (spectra)'] > SNRmax) #SNR critetia
            search.remove_rows(search['RA'] < RAmin)
            search.remove_rows(search['RA'] > RAmax)
            search.remove_rows(search['DEC'] < decMin)
            search.remove_rows(search['DEC'] > decMax)
            search.remove_rows(search['R (&lambda;/&delta;&lambda;)'] != R)



        except:
            pass
        return search

    def searchStar(self, star, instrument = None, date = None, SNR = None):
        """
        Return phase 3 ESO query for selected star. 
        Includes other options such as instrument, date, and signal-to-noise.
        
        Parameters
        ----------
        star: str
            Name of the star
        instrument: str
            Name of the instrument
            If None: Uses our default instruments
        date: str
            Date to search for obvervation ('YYYY-MM-DD')
            If None: date = '1990-01-23'
        SNR: float
            Signal to noise ratio. 
            If None: SNR = 1
            
        Returns
        -------
        search: table
            Result of the query on ESO arquive
        """
        if not date: 
            date = Time('1990-01-23')
        date = Time(date)
        if not SNR: 
            SNR = 1
        if instrument:
            search = self.eso.query_surveys(surveys=instrument, target=star)
        else:
            search = self.eso.query_surveys(surveys = list(self.instruments), 
                                            target = star)
        try:
            search.remove_rows(Time(search['Date Obs']) < date) #Date criteria
            search.remove_rows(search['SNR (spectra)'] < SNR) #SNR critetia
        except:
            pass
        return search
    
    def _searchAndDownload(self, star, instrument, downloadPath, date, SNR):
            """
            Auxiliary function to search and downlaod spectra
            
            Parameters
            ----------
            star: str
                Name of the star
            instrument: str
                Name of the instrument
            downloadPath: str
                Adress where to download data
            date: str
                Download only the data younger than a certain date
                
            Returns
            -------
            Downloaded spectra
            """
            starARCFILE = np.array(self.searchStar(star, instrument, 
                                                date, SNR)['ARCFILE'])
            if downloadPath:
                self.eso.retrieve_data(datasets = starARCFILE, 
                                    destination = downloadPath)
            else:
                self.eso.retrieve_data(datasets = starARCFILE)
    
    def arqDownload(self,arq,downloadPath=None):
        """
        Download the files of ESO

        Parameters
        -----------------------------
        arq: table
            table from ESO with the espectra
        downloadPath: str
            Adress where to download data

        Returns
        ------------
        Downloaded spectra
        """
        starArcfile= np.array((arq['ARCFILE']))
        if downloadPath:
            self.eso.retrieve_data(datasets = starArcfile, 
                                   destination = downloadPath,
                                   with_calib='processed')
        else:
            self.eso.retrieve_data(datasets = starArcfile,with_calib='processed')

    def baixar_arquivo(self,url, endereco):
        """
        Download a file with the url

        Parameters
        -----------------------------
        url: str
            the url to download
        endereco: str
            adress where to download with the name and type of the final file
        """
        resposta = requests.get(url)
        if resposta.status_code == requests.codes.OK:
            with open(endereco, 'wb') as novo_arquivo:
                    novo_arquivo.write(resposta.content)
            print("Download done. file saved in: {}".format(endereco))
        else:
            resposta.raise_for_status()

    def ANCILLARYdown(self,arq,downloadPath):
        """
        Download the ancillary files from ESO

        Parameters
        --------------------------
        arq: table
            table from ESO with the spectra
        downloadPath: str
            adress where to download
        """
        arcbef=np.array(arq['ARCFILE'])
        arqname=[]
        for i in range(0,len(arcbef)):
            id = arcbef[i]+'&RESPONSEFORMAT=json'
            rq = requests.get('http://archive.eso.org/datalink/links?ID=ivo://eso.org/ID?'+id)
            soup = BeautifulSoup(rq.content, 'html.parser')
            strsoup = str(soup)
            arqname.append(strsoup[2116:2143])
        link_pri='https://dataportal.eso.org/dataPortal/file/'
        tar='.tar'
        for i in range(0,len(arqname)):
            self.baixar_arquivo(link_pri+str(arqname[i]),str(downloadPath)+'/'+str(arqname[i])+tar)
        
