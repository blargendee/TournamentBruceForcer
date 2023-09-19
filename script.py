from itertools import combinations

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1MJeaTsofQxSE0JseeyL-SxYUeW9LFCaIKyidZfYeq4M'
RANGE_NAME = 'Sheet1!DataTable'

ZERO_POINTS = 0
BLANK_SCORE = ''
SET_A_INDEX_START = 1
SET_B_INDEX_START = 14
SET_LENGTH = 12
SONG_LEVEL_COL_INDEX = 1
SONG_NAME_COL_INDEX = 2
FREDDIE_SCORE_COL_INDEX = 5
JAKE_SCORE_COL_INDEX = 7
MATT_SCORE_COL_INDEX = 9



def parse(data):
    freddie_scores = [[], []]
    jake_scores = [[], []]
    matt_scores = [[], []]

    score_list_a = data[SET_A_INDEX_START: SET_A_INDEX_START + SET_LENGTH]
    score_list_b = data[SET_B_INDEX_START: SET_B_INDEX_START + SET_LENGTH]
    scores = [score_list_a, score_list_b]
   
    for i, score_list in enumerate(scores):
        for row in score_list:
            f_score = row[FREDDIE_SCORE_COL_INDEX]
            j_score = row[JAKE_SCORE_COL_INDEX]
            m_score = row[MATT_SCORE_COL_INDEX]

            f_score = ZERO_POINTS if f_score == BLANK_SCORE else int(f_score)
            j_score = ZERO_POINTS if j_score == BLANK_SCORE else int(j_score)
            m_score = ZERO_POINTS if m_score == BLANK_SCORE else int(m_score)

            freddie_scores[i].append(f_score)
            jake_scores[i].append(j_score)
            matt_scores[i].append(m_score)

    return (freddie_scores, jake_scores, matt_scores)


def print_best_combos(scores):
    print()
    totals = []

    for i in range(2):
        LIST_SIZE = 12
        FREDDIE_SCORE_INDEX = 0
        JAKE_SCORE_INDEX = 1
        MATT_SCORE_INDEX = 2
        list1 = set(range(LIST_SIZE))
        combos1 = combinations(list1, 2)
        current_max = 0
        max1_index = None
        max2_index = None
        max3_index = None
        
        for freddie_index_1, freddie_index_2 in combos1:
            list2 = set(range(LIST_SIZE))
            list2.remove(freddie_index_1)
            list2.remove(freddie_index_2)
            combos2 = combinations(list2, 2)
        
            for jake_index_1, jake_index_2 in combos2:
                list3 = set(range(LIST_SIZE))
                list3.remove(freddie_index_1)
                list3.remove(freddie_index_2)
                list3.remove(jake_index_1)
                list3.remove(jake_index_2)
                combos3 = combinations(list3, 2)
        
                for matt_index_1, matt_index_2 in combos3:
                    sum1 = scores[FREDDIE_SCORE_INDEX][i][freddie_index_1] + scores[FREDDIE_SCORE_INDEX][i][freddie_index_2]
                    sum2 = scores[JAKE_SCORE_INDEX][i][jake_index_1] + scores[JAKE_SCORE_INDEX][i][jake_index_2]
                    sum3 = scores[MATT_SCORE_INDEX][i][matt_index_1] + scores[MATT_SCORE_INDEX][i][matt_index_2]
        
                    total = sum([sum1, sum2, sum3])
                    if total > current_max:
                        current_max = total
                        max1_index = freddie_index_1, freddie_index_2
                        max2_index = jake_index_1, jake_index_2
                        max3_index = matt_index_1, matt_index_2
        
        print(f"Freddie's Scores: \t{scores[FREDDIE_SCORE_INDEX][i][max1_index[0]]} {scores[FREDDIE_SCORE_INDEX][i][max1_index[1]]}")
        print(f"Jake's Scores: \t\t{scores[JAKE_SCORE_INDEX][i][max2_index[0]]} {scores[JAKE_SCORE_INDEX][i][max2_index[1]]}")
        print(f"Matt's Scores: \t\t{scores[MATT_SCORE_INDEX][i][max3_index[0]]} {scores[MATT_SCORE_INDEX][i][max3_index[1]]}")
        print(f"Total: \t{current_max}")
        print()
        
        totals.append(current_max)

    print()
    print(f"Grand Total: {sum(totals)}")


def get_data():
    """Shows basic usage of the Sheets API.
    Prints data from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=RANGE_NAME).execute()
        fetched_data = result.get('values', [])

        if not fetched_data:
            print('No data found.')
            return

        print('Data:')
        print(fetched_data)
        return fetched_data
    
    except HttpError as err:
        print(err)


if __name__ == '__main__':
    data = get_data()
    scores = parse(data)
    print_best_combos(scores)