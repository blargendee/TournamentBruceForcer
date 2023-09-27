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
SPREADSHEET_ID = '1CLjLuUOYOmuGPJyDzG_k5AthZQsgiyP1NW3F_rOPGz8'
RANGE_NAME = 'Scores!Data'

JOBS = 'AMEX', 'PAYPAL'
BLANK_SCORE = ''
ZERO_POINTS = 0


def parse(data):
    score_sets = dict()

    it = iter(data)
    column_names = next(it)
    for entry in it:
        new_dict = dict()
        key = entry[0]
        for i, label in enumerate(column_names):
            new_dict[label] = entry[i]

        score_sets[key] = new_dict

    for value in score_sets.values():
        value['Freddie'] = ZERO_POINTS if value['Freddie'] == BLANK_SCORE else int(value['Freddie'])
        value['Jake'] = ZERO_POINTS if value['Jake'] == BLANK_SCORE else int(value['Jake'])
        value['Matt'] = ZERO_POINTS if value['Matt'] == BLANK_SCORE else int(value['Matt'])

    return score_sets


def get_best_combos(splits):
    totals = []

    for song_map in splits:
        maximum = 0
        max_entries = None
        song_pool = set(song_map)

        freddie_combos = combinations(song_pool, 2)
        for a, b in freddie_combos:
            song_pool.remove(a)
            song_pool.remove(b)
            jake_combos = combinations(song_pool, 2)
            for c, d in jake_combos:
                song_pool.remove(c)
                song_pool.remove(d)
                matt_combos = combinations(song_pool, 2)
                for e, f in matt_combos:
                    cumulative_scores = []
                    cumulative_scores.append(song_map[a]['Freddie'])
                    cumulative_scores.append(song_map[b]['Freddie'])
                    cumulative_scores.append(song_map[c]['Jake'])
                    cumulative_scores.append(song_map[d]['Jake'])
                    cumulative_scores.append(song_map[e]['Matt'])
                    cumulative_scores.append(song_map[f]['Matt'])

                    total = sum(cumulative_scores)
                    if total > maximum:
                        maximum = total
                        max_entries = dict(zip(['a', 'b', 'c', 'd', 'e', 'f'], [a, b, c, d, e, f]))

                song_pool.update((c, d))

            song_pool.update((a, b))

        print()
        song_a = max_entries['a']
        song_a_score = song_map[song_a]['Freddie']
        song_b = max_entries['b']
        song_b_score = song_map[song_b]['Freddie']
        song_c = max_entries['c']
        song_c_score = song_map[song_c]['Jake']
        song_d = max_entries['d']
        song_d_score = song_map[song_d]['Jake']
        song_e = max_entries['e']
        song_e_score = song_map[song_e]['Matt']
        song_f = max_entries['f']
        song_f_score = song_map[song_f]['Matt']
        subtotal = sum([song_a_score, song_b_score, song_c_score, song_d_score, song_e_score, song_f_score])
        totals.append(subtotal)

        print(f"Freddie's Songs: {song_a} [{song_a_score}] | {song_b} [{song_b_score}]")
        print(f"Jake's Songs: {song_c} [{song_c_score}] | {song_d} [{song_d_score}]")
        print(f"Matt's Songs: {song_e} [{song_e_score}] | {song_f} [{song_f_score}]")
        print(f"Subtotal: {subtotal}")

    print()
    print(f"Grand Total: {sum(totals)}")


def split_scores(scores):
    set_a = dict()
    set_b = dict()

    print(scores)

    for song_name, fields in scores.items():
        song_set = fields['Set']
        if song_set == 'A':
            set_a[song_name] = fields
        else:
            set_b[song_name] = fields

    return (set_a, set_b)
            

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
    splits = split_scores(scores)
    get_best_combos(splits)