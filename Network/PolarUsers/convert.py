import csv
import json

if __name__ == "__main__":
    #convert csv to json 
    d = {}
    with open('all', 'r') as f:
        csvreader = csv.reader(f)

        for row in csvreader:
            d[row[1]] = row[2]

    print(len(d))

    with open('../Data/polarity.json', 'w') as f:
        json.dump(d,f)
