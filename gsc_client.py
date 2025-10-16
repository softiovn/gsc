import pandas as pd
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from PySide6.QtCore import QObject, pyqtSignal
from data_models import GSCDataPoint

class GSCClient(QObject):
    data_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, credentials):
        super().__init__()
        self.credentials = credentials
        self.service = build('searchconsole', 'v1', credentials=credentials)
        self.sites = []
    
    def get_sites(self):
        """Get list of available sites"""
        try:
            site_list = self.service.sites().list().execute()
            self.sites = [site for site in site_list.get('siteEntry', []) 
                         if site.get('permissionLevel') in ['siteOwner', 'siteFullUser']]
            return self.sites
        except Exception as e:
            self.error_occurred.emit(f"Failed to fetch sites: {str(e)}")
            return []
    
    def fetch_search_analytics(self, site_url, start_date, end_date, dimensions=None, row_limit=25000):
        """Fetch search analytics data from GSC"""
        try:
            if dimensions is None:
                dimensions = ['date', 'query', 'page', 'country', 'device']
            
            request = {
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': end_date.strftime('%Y-%m-%d'),
                'dimensions': dimensions,
                'rowLimit': row_limit,
                'dataState': 'all'
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=site_url, body=request
            ).execute()
            
            data_points = self._parse_response(response, dimensions)
            self.data_loaded.emit(data_points)
            return data_points
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to fetch data: {str(e)}")
            return []
    
    def _parse_response(self, response, dimensions):
        """Parse GSC API response into GSCDataPoint objects"""
        data_points = []
        
        if 'rows' not in response:
            return data_points
        
        for row in response['rows']:
            # Extract keys based on dimensions
            keys = row.get('keys', [])
            dimension_dict = dict(zip(dimensions, keys))
            
            data_point = GSCDataPoint(
                date=datetime.strptime(dimension_dict.get('date', ''), '%Y-%m-%d').date(),
                clicks=row.get('clicks', 0),
                impressions=row.get('impressions', 0),
                ctr=row.get('ctr', 0),
                position=row.get('position', 0),
                query=dimension_dict.get('query', ''),
                page=dimension_dict.get('page', ''),
                country=dimension_dict.get('country', ''),
                device=dimension_dict.get('device', '')
            )
            data_points.append(data_point)
        
        return data_points