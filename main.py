from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import publicScrape
import os
import datetime
import json
import googleapiclient.errors


work_dir = '/Users/seanlord/Documents/Project/Evergreens/'
SCOPES = ['https://www.googleapis.com/auth/drive.file']
sheet_range = "A2:J1000"

pickle_path = work_dir + "token.pickle"
cred_path = work_dir + "credentials.json"
no_path = work_dir + "no.txt"
id_path = work_dir + "id.txt"
backup_dir = work_dir + "backups/"

def writeSpreadsheet(id, body, range):
	result = sheets.values().update(spreadsheetId = id, range = range, body = body, valueInputOption = "USER_ENTERED").execute()

def readSpreadsheet(id, range):
	result = sheets.values().get(spreadsheetId = id, range = range).execute()['values']
	return result

def createSpreadsheet():
	body = {'properties':{'title':'Evergreens'}}
	result = sheets.create(body = body, fields = 'spreadsheetId').execute()
	id = result.get('spreadsheetId')
	with open(id_path, "w") as idFile:
		idFile.write(id)
	values = [["Remove", "Title", "Author", "Published", "Description", "URL"]]
	body = {'values':values}
	writeSpreadsheet(id, body, "A1")
	format_data = {'requests':[	{'updateSheetProperties':{'properties':{'gridProperties':{'frozenRowCount':1}},'fields':'gridProperties.frozenRowCount'}},{'repeatCell':{'range':{'endRowIndex':1},'cell':{'userEnteredFormat':{'textFormat':{'bold':True}}},'fields':'UserEnteredFormat.textFormat.bold'}},{'repeatCell':{'range':{'startColumnIndex':3,'endColumnIndex':4,'startRowIndex':1},'cell':{'userEnteredFormat':{'numberFormat':{'type':'DATE','pattern':'mmmm d, yyyy'}}},'fields':'userEnteredFormat.numberFormat'}},{'updateDimensionProperties':{'range':{'dimension':'COLUMNS','startIndex':0,'endIndex':1},'properties':{'pixelSize':60},'fields':'pixelSize'}},{'updateDimensionProperties':{'range':{'dimension':'COLUMNS','startIndex':1,'endIndex':2},'properties':{'pixelSize':700},'fields':'pixelSize'}},{'updateDimensionProperties':{'range':{'dimension':'COLUMNS','startIndex':2,'endIndex':3},'properties':{'pixelSize':150},'fields':'pixelSize'}},{'updateDimensionProperties':{'range':{'dimension':'COLUMNS','startIndex':3,'endIndex':4},'properties':{'pixelSize':120},'fields':'pixelSize'}},{'updateDimensionProperties':{'range':{'dimension':'COLUMNS','startIndex':4,'endIndex':5},'properties':{'pixelSize':1000},'fields':'pixelSize'}},{'updateDimensionProperties':{'range':{'dimension':'COLUMNS','startIndex':5,'endIndex':6},'properties':{'pixelSize':800},'fields':'pixelSize'}}]}
	result = sheets.batchUpdate(spreadsheetId = id, body = format_data).execute()
	return id
	

def clearSpreadsheet(id, range):
	result = sheets.values().clear(spreadsheetId = id, range = range).execute()

def getSheetId():
	with open(id_path, "r") as idFile:
		sheet_id = idFile.read()
	return sheet_id
	
def getNoList():
	if os.path.exists(no_path):
		with open(no_path, 'r') as noFile:
			return noFile.read().split()
	else:
		with open(no_path, 'w') as noFile:
			noFile.write('')
		return ['']

def updateNoList(no_list):
	with open(no_path, 'w') as noFile:
		noFile.write('\n'.join(no_list))

def buildSheets():
	creds = None
	if os.path.exists(pickle_path):
		with open(pickle_path, 'rb') as token:
			creds = pickle.load(token)
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
			creds = flow.run_local_server(port=0)
		with open(pickle_path, 'wb') as token:
			pickle.dump(creds, token)
	global sheets
	sheets = build('sheets', 'v4', credentials=creds).spreadsheets()

def backupSheet(values):
	if not os.path.isdir(backup_dir):
		os.mkdir(backup_dir)
	date_string = datetime.datetime.now().strftime('%m%d%y')
	with open(backup_dir + 'backup' + date_string + '.json', 'w') as backupFile:
		json.dump(values, backupFile)

def main():
	buildSheets()
	try:
		print("Retrieving sheet ID from id.txt")
		sheet_id = getSheetId()
	except FileNotFoundError:
		print("Sheet ID not found -- creating new spreadsheet")
		sheet_id = createSpreadsheet()
	sheet_id = getSheetId()
	current_sheet = [[]]
	try:
		print("Retrieving spreadsheet from Google")
		current_sheet = readSpreadsheet(sheet_id, sheet_range)
		print("Backing up current spreadsheet as JSON")
		backupSheet(current_sheet)
	except KeyError:
		print("Anticipated cells are empty -- proceeding with empty array")
	except googleapiclient.errors.HttpError:
		print("Sheet not found -- creating new spreadsheet")
		sheet_id = createSpreadsheet()
	current_site = publicScrape.getStoriesInfo()
	print("Retrieving the no list from no.txt")
	no_list= getNoList()
	new_list= []
	print("Removing nos and incomplete rows")
	for y in current_sheet:
		if len(y) < 6:
			continue
		elif y[0].lower() == 'x':
			no_list.append(y[5])
		else:
			new_list.append(y)
	add_list = []
	print("Checking for duplicates")
	for x in current_site:
		if x[5] in no_list:
			continue
		alreadyIn = False
		for y in new_list:
			if x[5] == y[5]:
				alreadyIn = True
		if  not alreadyIn:
			add_list.append(x)
	body = {'values':add_list + new_list}
	print("Clearing spreadsheet for formatting")
	clearSpreadsheet(sheet_id, sheet_range)
	print("Updating spreadsheet")
	writeSpreadsheet(sheet_id, body, "A2")
	print("Writing no list to no.txt")
	updateNoList(no_list)

main()
	

