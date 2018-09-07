import os , json

def compare():
    #load echo chamber
    with open('Data/intersection_2.json') as f:
        echo1 = json.load(f)

    with open('Data/echo_chamber2.json') as f:
        echo2 = json.load(f)

    common = {}
    diff = echo1.copy()

    for key in echo1.keys():
        if len(echo1[key]) < 2:
            continue

        set1 = set(key.split(','))
        find = False
        for key2 in echo2.keys():
            
            set2 = set(key2.split('_'))
            if len(set1&set2) == 2:
                find = True

        if find:
            del diff[key]
    
    for key in diff.keys():
        print(key)
    
    print(len(diff))

    with open('Data/diff.json', 'w') as f:
        json.dump(diff.keys(), f)



if __name__ == "__main__":
    compare()
