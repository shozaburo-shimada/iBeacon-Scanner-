#http://workpiles.com/2017/04/raspi-spreadsheet-api/

import httplib2
import numpy as np
import privatedb

from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
APPEND_RANGE = 'Sheet1!A1:C1'

class SpreadSheet(object):
    def __init__(self, sheet_id):
        self.sheetId = sheet_id

        credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scopes=SCOPES)
        http_auth = credentials.authorize(httplib2.Http())
        discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?''version=v4')
        self.service = discovery.build('sheets', 'v4', http=http_auth, discoveryServiceUrl=discoveryUrl)

    def append(self, values):
        assert np.array(values).shape==(3,) , "The shape of value %s must be 3" % (np.array(values).shape)
        value_range_body = {'values':[values]}
        result = self.service.spreadsheets().values().append(spreadsheetId=self.sheetId, range=APPEND_RANGE, valueInputOption='USER_ENTERED', body=value_range_body).execute()
        #print(result)

    def write(self, index, values):
        write_range = "A" + str(index)
        assert np.array(values).shape==(3,) , "The shape of value %s must be 3" % (np.array(values).shape)
        data = [{'range':write_range, 'values':[values]}]
        body = {'valueInputOption':'USER_ENTERED', 'data':data}
        result = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.sheetId, body=body).execute()


if __name__ == '__main__':
  sheet = SpreadSheet(privatedb.SHEETID)
  sheet.append(["test", "test", 3])
