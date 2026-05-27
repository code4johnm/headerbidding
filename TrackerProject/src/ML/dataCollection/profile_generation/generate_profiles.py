from __future__ import annotations

import binascii
import hashlib
import json
import sqlite3
import time
from itertools import combinations, product
from random import randint, random
from secrets import SystemRandom

import numpy as np
import pandas as pd
volume = [1,2,3,4,5,6,7,8,9,10]
intent = ['NO_INTENT','INTENT']
category = [   "Adult",
                "Arts",
                "Business",
                "Computers",
                "Games",
                "Health",
                "Home",
                "Kids_and_Teens",
                "News",
                "Recreation",
                "Reference",
                "Regional",
                "Science",
                "Shopping",
                "Society",
                "Sports",
                "Control"]


top_20_trackers = [ "alphabet",
                    "yandex",
                    "oracle",
                    "appnexus",
                    "verizon",
                    "baidu",
                    "twitter",
                    "facebook",
                    "double_verify",
                    "adobe_systems",
                    "criteo",
                    "microsoft",
                    "quantcast",
                    "pubmatic",
                    "automattic",
                    "sovrn",
                    "integral_ad_science",
                    "comscore",
                    "exoclick",
                    "alibaba"]  
                                  

class GenerateProfiles:
    def __init__(self, **kwargs):
        startTime = time.time()
        print("GenerateProfiles started at {}".format(time.asctime()))

        samples_to_generate=10
        print_every = samples_to_generate/10
        hashes = {}

        #Generate 
        profile = pd.DataFrame()
        profiles_completed = print_every
        split_time = time.time()
        
        
        for sample in iter(range(1, samples_to_generate)):           
            get_profile = self.get_profile()
            toHash = get_profile.values
            hashString = str.encode(self.getHashString(toHash))
            profileHash = hashlib.sha256(hashString).hexdigest()
     
            try: 
                while(hashes[profileHash]):
                    print('collision on sample: {}'.format(sample))
                    get_profile = self.get_profile()
                    toHash = get_profile.values
                    hashString = str.encode(self.getHashString(toHash))
                    profileHash = hashlib.sha256(hashString).hexdigest()
            except: 
                hashes[profileHash] = True
            get_profile['hash'] = profileHash
            profile = pd.concat([profile, pd.DataFrame(get_profile)])

            if (sample%print_every == 0):
                print("Gen'd {} profiles in {:.4f} sec. - split time: {:.4f} sec.".format(profiles_completed, time.time() - startTime, time.time()-split_time))
                profiles_completed+=print_every 
                if sample == print_every:
                    profile.to_csv('generatedProfiles.csv', index=False, mode='w')
                profile.to_csv('generatedProfiles.csv', index=False, mode='a', header=False)
                profile = profile.iloc[:]
                split_time = time.time()
        prof = pd.read_csv('generatedProfiles.csv')
        print(prof.shape)
        prof.drop_duplicates()
        prof = prof.drop_duplicates(['hash']).reset_index(drop=True)
        
        print(prof.shape)
        prof.to_csv('generatedProfiles.csv', mode='w', index=False)

        print("Time to generate {} profiles {:.4f} sec.".format(samples_to_generate, time.time() - startTime))


    def getHashString(self, arr):
        hashString = ""
        for v in arr[0]:
            hashString+=str(v)
        return hashString            
    def get_profile(self):
        cols = ["volume", "intent", "category"]

        for t in top_20_trackers:
            cols.append(t)
        v = SystemRandom().sample(volume, 1)
        i = SystemRandom().sample(intent, 1)
        c = SystemRandom().sample(category, 1)
        number_blocking = randint(0,20)
        profile = pd.DataFrame(columns=cols)
        profile["volume"] = hex(v)
        profile["intent"] = (0,1)[i == intent]
        profile["category"] = c

        for t in reversed(top_20_trackers):
            if t in trackers: 
                profile[t] = 1
            else:
                profile[t] = 0
        return profile        

       
        # for i in category: 
        #     all_choices.append()



if __name__ == "__main__":
    a = GenerateProfiles()