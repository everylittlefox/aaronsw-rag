import json
import sys
import os

if __name__ == "__main__":
    dir_name = sys.argv[1]
   
    if os.path.isfile(dir_name + '/topics.json'):
        with open(dir_name + '/topics.json') as t:
            topics = json.load(t)

        topics = topics.keys()
        tfiles = [dir_name + f'/{"-".join(t.lower().split(' '))}.json' for t in topics]
        tfiles = [tf for tf in tfiles if os.path.isfile(tf)]
        
        data = []
        for tf in tfiles:
            with open(tf) as t:
                data.extend(json.load(t))

        print(f'there are {len(data)} rows in the dataset')