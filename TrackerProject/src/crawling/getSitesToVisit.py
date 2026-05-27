from __future__ import annotations

import json
import os
from argparse import ArgumentParser
class GetSitesToVisit:
    def __init__(self, **kwargs):    
        kwargs = dict(kwargs['kwargs']._get_kwargs())
        self.category = kwargs.pop('category','')
        self.volume = kwargs.pop('volume','')
        self.crawl_type = kwargs.pop('crawl_type','')
        self.intent = kwargs.pop('intent','')
        self.sitesToVisit = [] 


        self.configBase = os.path.abspath('../../src/config')
        self.trainingSitesBase = os.path.join(self.configBase, 'training', 'sites', 'alexa_top_fifty_per_category')
        self.testingSiteBase = os.path.join(self.configBase, 'testing', 'sites', 'pbjs')
        sites_path = ("", self.trainingSitesBase)["training" in self.crawl_type]
        sites_path = (sites_path, self.testingSiteBase)["testing" in self.crawl_type]

        print(self.volume, self.crawl_type, self.category, self.intent)
        print(sites_path)


        if sites_path: 
            self.getSitesByCategory(sites_path)

    def batch_ab_training(self):
        pass
    def batch_ml_training(self):
        return 
    def batch_ab_testing(self):
        pass
    def batch_ml_testing(self):
        pass


                    
    
    def getSitesByCategory(self,sites_path):
        intent_sites = []
        no_intent_sites = []
        category = os.listdir(sites_path)
        category_path = ""
        for f in category:
            if self.category in f: 
                category_path = os.path.join(sites_path, f)
        intent_site_path = os.path.join(sites_path, 'intent.json')
        with open(intent_site_path) as f:
            intent_sites = json.load(f)
            intent_sites = intent_sites['Intent']

        with open(category_path) as f: 
            data = json.load(f)
            no_intent_sites = data[self.category]
        for site in no_intent_sites: 
            intent_sites.append(site)
        if self.intent == 'no_intent':
            self.sitesToVisit = no_intent_sites
        else:
            self.sitesToVisit = intent_sites
    def getSites(self):
        return self.sitesToVisit

if __name__ == "__main__":
    
    params = ['--volume',
                    '--intent',
                    '--category',
                    '--crawl_type'
                    ]
    parser = ArgumentParser()                          
    for arg in params:
        parser.add_argument("{}".format(arg))
    args = parser.parse_args()
    print(args)
    a = GetSitesToVisit(kwargs=args)

    

