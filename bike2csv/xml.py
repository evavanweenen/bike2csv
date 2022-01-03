import os
import numpy as np
import pandas as pd
import re
import xml.etree.ElementTree as ET

class XML(object):
    def __init__(self, filename, path_in, path_out):
        self.filename = filename
        self.path_in = path_in
        self.path_out = path_out

    def read_data(self, level=0):
        file = ET.parse(os.path.join(self.path_in, self.filename))
        root = file.getroot()
        for l in range(level):
            root = root[0]
        self.data = root
        self.space = re.match(r'{.*}', root.tag).group(0)
        self.name = root.tag.replace(self.space, '')
        self.categories = list(np.unique([cat.tag.replace(self.space, '') for cat in self.data]))

    def get_elements(self, cat):
        elements = self.data.findall(self.space+cat)
        self.categories.remove(cat)
        return elements

    def get_category(self, cat):
        df = pd.DataFrame()
        for i, element in enumerate(self.get_elements(cat)):
            for item in element:
                df.loc[i, item.tag.replace(self.space,'')] = item.text
        return df

    def save_file(self, df, cat):
        if not os.path.exists(os.path.join(self.path_out, cat)):
            os.makedirs(os.path.join(self.path_out, cat))
        df.to_csv(os.path.join(self.path_out, cat, os.path.splitext(self.filename)[0]+'_'+cat+'.csv'))

class PWX(XML):
    def __init__(self, filename, path_in, path_out):
        super().__init__(filename, path_in, path_out)

        self.fitnames = {   'sample'                :'record',
                            'event'                 :'event',
                            'segment'               :'lap',
                            'Bike'                  :'cycling',
                            'make'                  :'manufacturer',
                            'model'                 :'product',
                            'duration'              :'total_elapsed_time',
                            'distance'              :'total_distance',
                            'climbingelevation'     :'total_ascent',
                            'descendingelevation'   :'total_descent',
                            'hr'                    :'heart_rate',
                            'spd'                   :'speed',
                            'pwr'                   :'power',
                            'dist'                  :'distance',
                            'lat'                   :'position_lat',
                            'lon'                   :'position_long',
                            'alt'                   :'altitude',
                            'temp'                  :'temperature',
                            'cad'                   :'cadence',
                            'type'                  :'event_type'}

    def get_header(self):
        df = pd.Series(4*[{}], index=['file_id', 'device_0', 'session', 'sport'])

        # summary data
        if 'summarydata' in self.categories:
            summary = self.get_category('summarydata')
            if not summary.empty:
                df.loc['session'].update(summary.loc[0].to_dict())

        # sport type
        if 'sportType' in self.categories:
            item = self.get_elements('sportType')[0]
            df.loc['session'].update({'sport' : item.text})
            df.loc['sport'].update({'sport' : item.text})

        # device
        if 'device' in self.categories:
            device = self.get_category('device').loc[0].to_dict()
            df.loc['device_0'].update(device)
            df.loc['file_id'].update(device)
        
        # cmt
        if 'cmt' in self.categories:
            item = self.get_elements('cmt')[0]
            df.loc['device_0'].update({'descriptor' : item.text})

        # time
        if 'time' in self.categories:
            item = self.get_elements('time')[0]
            self.start_time = pd.to_datetime(item.text)
            df.loc['session'].update({'start_time' : self.start_time})
            df.loc['file_id'].update({'time_created' : self.start_time})

        # athlete
        if 'athlete' in self.categories:
            item = self.get_elements('athlete')[0][0]
            df.loc['file_id'].update({'athlete' : item.text})

        df = df.apply(pd.Series).stack().rename(index=self.fitnames).replace(self.fitnames)

        if 'beginning' in df['session']:
            df[('session', 'start_time')] += pd.to_timedelta(int(float(df[('session', 'beginning')])), unit='S')
            df = df.drop([('session', 'beginning')])

        if 'durationstopped' in df['session']:
            df[('session', 'total_timer_time')] = float(df[('session', 'total_elapsed_time')]) - float(df[('session', 'durationstopped')])
            df = df.drop([('session', 'durationstopped')])

        self.save_file(df, 'info')
        return df

    def get_laps(self):
        if 'segment' in self.categories:
            df = pd.DataFrame()
            for i, element in enumerate(self.get_elements('segment')): # each segment
                for item in element[1]:
                    df.loc[element[0].text, item.tag.replace(self.space,'')] = item.text
            df = df.rename(columns=self.fitnames)
            
            if 'beginning' in df and 'time' in self.categories:
                df['beginning'] = self.start_time + pd.to_timedelta(df['beginning'].astype(float).astype(int), unit='S')
                df = df.rename(columns={'beginning':'timestamp'})

            if 'durationstopped' in df and 'total_elapsed_time' in df:
                df['total_timer_time'] = df['total_elapsed_time'].astype(float) - df['durationstopped'].astype(float)
                df = df.drop('durationstopped', axis=1)

            self.save_file(df, 'lap')
            return df

    def get_events(self):
        if 'event' in self.categories:
            df = self.get_category('event')
            if 'timeoffset' in df:
                df['timestamp'] = self.start_time + pd.to_timedelta(df['timeoffset'].astype(float), unit='S')
                df = df.drop('timeoffset', axis=1)
                df = df.set_index('timestamp')
            df = df.rename(columns=self.fitnames)
            self.save_file(df, 'event')
            return df

    def get_records(self):
        if 'sample' in self.categories:
            df = self.get_category('sample')
            if 'timeoffset' in df:
                df['timestamp'] = self.start_time + pd.to_timedelta(df['timeoffset'].astype(float), unit='S')
                df = df.drop('timeoffset', axis=1)
                df = df.set_index('timestamp')
            df = df.rename(columns=self.fitnames)

            # convert degrees to semicircles (similar to .fit files)
            if 'position_lat' in df:
                df['position_lat'] = df['position_lat'].astype(float) / (180 / 2**31)
            if 'position_long' in df:
                df['position_long'] = df['position_long'].astype(float) / (180 / 2**31)

            self.save_file(df, 'record')
            return df

    def parse(self):
        self.read_data(level=1)
        self.get_header()
        self.get_laps()
        self.get_events()
        self.get_records()

        if len(self.categories) != 0:
            print("Message types not processed: ", *tuple(self.categories))

class TCX(XML):
    def __init__(self, filename, path_in, path_out):
        super().__init__(filename, path_in, path_out)

        self.fitnames = {'Name'                     : 'product_name',
                         'UnitId'                   : 'serial_number',
                         'ProductID'                : 'product',
                         'Time'                     : 'timestamp',
                         'PositionLatitudeDegrees'  : 'position_lat',
                         'PositionLongitudeDegrees' : 'position_long',
                         'AltitudeMeters'           : 'altitude',
                         'DistanceMeters'           : 'distance',
                         'Cadence'                  : 'cadence',
                         'HeartRateBpm'             : 'heart_rate',
                         'Speed'                    : 'speed',
                         'Watts'                    : 'power',
                         'TotalTimeSeconds'         : 'total_timer_time',
                         'DistanceMeters'           : 'total_distance',
                         'MaximumSpeed'             : 'max_speed',
                         'Calories'                 : 'total_calories',
                         'Intensity'                : 'intensity_factor',
                         'TriggerMethod'            : 'trigger',
                         'MaxBikeCadence'           : 'max_cadence',
                         'AvgSpeed'                 : 'avg_speed',
                         'AvgWatts'                 : 'avg_power',
                         'AverageHeartRateBpm'      : 'avg_heart_rate',
                         'MaxWatts'                 : 'max_power',
                         'MaximumHeartRateBpm'      : 'max_heart_rate'}

    def get_version(self, item):
        version = ''
        for subversion in ('VersionMajor', 'VersionMinor', 'BuildMajor', 'BuildMinor'):
            version += item.findall(self.space+subversion)[0].text + '.'
        return version.rstrip('.')

    def get_extension(self, item):
        df = pd.Series()
        for ext in item:
            space = re.match(r'{.*}', ext.tag).group(0)
            for col in ext:
                df[col.tag.replace(space, '')] = col.text
        return df

    def get_header(self):
        df = pd.Series(3*[{}], index=['file_id', 'device_0', 'session'])

        creator = {}
        # creator
        if 'Creator' in self.categories:
            creator['manufacturer'] = 'Garmin'
            elements = self.get_elements('Creator')[0]
            for item in elements:
                tag = item.tag.replace(self.space, '')
                if tag == 'Version':
                    creator['software_version'] = self.get_version(item)
                else:
                    creator[tag] = item.text
        # extensions
        if 'Extensions' in self.categories:
            extensions = self.get_elements('Extensions')[0]
            if len(extensions) > 0:
                for item in extensions:
                    creator[item.tag] = item.text
        df.loc['file_id'].update(creator)
        df.loc['device_0'].update(creator)

        # time
        if 'Id' in self.categories:
            item = self.get_elements('Id')[0]
            df.loc['file_id'].update({'time_created' : item.text})
            df.loc['session'].update({'start_time' : item.text})
        
        # training
        if 'Training' in self.categories:
            summary = {}
            elements = self.get_elements('Training')[0]
            for element in elements:
                for item in element:
                    if item.text is not None:
                        summary[item.tag.replace(self.space, '')] = item.text
            df.loc['session'].update(summary)

        df = df.apply(pd.Series).stack().rename(index=self.fitnames)
        self.save_file(df, 'info')
        return df

    def get_laps(self):
        df = pd.DataFrame()
        for i, element in enumerate(self.data.findall(self.space+'Lap')):
            for item in element:
                tag = item.tag.replace(self.space,'')
                if tag == 'Extensions':
                    for col, value in self.get_extension(item).iteritems():
                        df.loc[i, col] = value
                elif tag != 'Track':
                    df.loc[i, tag] = item.text
  
        df = df.rename(columns=self.fitnames)
        self.categories.remove('Lap')
        self.save_file(df, 'lap')
        return df

    def get_records(self):
        df = pd.DataFrame()

        c = 0
        for lap in self.data.findall(self.space+'Lap'):
            records = lap.findall(self.space+'Track')[0]

            for i, element in enumerate(records):
                for item in element:
                    tag = item.tag.replace(self.space,'')
                    if tag == 'Position':
                        for pos in item:
                            df.loc[c+i, tag+pos.tag.replace(self.space, '')] = pos.text                        
                    elif tag == 'Extensions':
                        for col, value in self.get_extension(item).iteritems():
                            df.loc[c+i, col] = value                  
                    else:
                        df.loc[c+i, tag] = item.text
            c += i
        
        df = df.rename(columns=self.fitnames)

        # convert degrees to semicircles (similar to .fit files)
        if 'position_lat' in df:
            df['position_lat'] = df['position_lat'].astype(float) / (180 / 2**31)
        if 'position_long' in df:
            df['position_long'] = df['position_long'].astype(float) / (180 / 2**31)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        self.save_file(df, 'record')
        return df

    def parse(self):
        self.read_data(level=2)
        self.get_header()
        self.get_laps()
        self.get_records()

        if len(self.categories) != 0:
            print("Message types not processed: ", *tuple(self.categories))
