import os, sys, json

#convert bot properties into one json file
def convert_bot_file():
    folder = 'BotResult/'
    files = os.listdir(folder)
    d = {}
    bot_count = 0
    for i, userid in enumerate(files):
        if i % 10000 == 0:
            print(i)

        with open(folder + userid) as f:
            try:
                value = json.load(f)
                if value == 1:
                    bot_count += 1
                d[userid] = value
            except ValueError as e:
                continue

    with open('Network/Data/botresult.json', 'w') as f:
        json.dump(d, f)

    print('bot num : %s / %s'%(bot_count, len(files)))
if __name__ == "__main__":
    convert_bot_file()
