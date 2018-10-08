#convert csv to json

import os, sys, csv, json

def convert_csv_to_json():
    files = os.listdir('./')
    
    users = {}
    for postid in files:
        with open(postid, 'r') as f:
            data = csv.reader(f)

            for i, row in enumerate(data):
                if i == 0:
                    continue
                try:
                    users[row[1]] = row[2]
                except IndexError as e:
                    print(e)

    with open('../Data/polarization.json', 'w') as f:
        json.dump(users, f)

if __name__ == "__main__":
    convert_csv_to_json()    
