

from __future__ import absolute_import
import sys
import os
import time
import json
import copy
import random
import argparse
from multiprocessing import Process
from pathlib import Path

# Add project root to path so we can import openwpm
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parents[4]  # root from .../AB_Testing/training/
sys.path.insert(0, str(project_root))

baseSrcPath = os.path.abspath('../../')
baseHBPath = os.path.abspath('../../../../')
sys.path.append(baseSrcPath)
sys.path.append(baseHBPath)
from HBLogging import HBLogger


# six.moves.range not needed on Py3
from ScriptUtils.scriptUtils import ScriptUtils
from openwpm.command_sequence import CommandSequence
from openwpm.task_manager import TaskManager
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider


class TrainingCrawl:
    def __init__(self, **kwargs):   
        self.trainingParams = {'volume':"",
                          'intent':"",
                          'category':"",
                          'trackers_blocked':"",
                          'training_type':""}
        
        self.NUM_BROWSERS = 1
        self.sites = {}
        # sites = {"1":"http://www.zimbio.com/"}
        self.pbjsUtils = ScriptUtils()
        self.local_done = {}
        self.browsers_open = 0
        self.clear_data = {}


        self.sites_done = {
            "Adult":0,
            "Arts":0,
            "BLOCK":0,
            "Business":0,
            "Computers":0,
            "Games":0,
            "Health":0,
            "Home":0,
            "KidsAndTeens":0,
            "News":0,
            "Recreation":0,
            "Reference":0,
            "Regional":0,
            "Science":0,
            "Shopping":0,
            "Society":0,
            "Sports":0
        }   

        with open('trainingDone.json', 'w') as f:  
            json.dump(self.sites_done, f, indent=4, separators=(',', ':'))


        """load each of the categories into alexaCategorySites
        """
        self.sites_path = os.path.abspath('../sites/')
        self.alexaCategories = []
        self.alexCategorySites = {}
        self.iab_params = {}
        self.ab_managers = {}
        self.ml_managers = {}

        self.timestamp = time.time()
        self.volume = kwargs.pop('volume', 1)
        self.intent = kwargs.pop('intent', False)
        self.category = kwargs.pop('category', '')
        self.trackers_blocked = kwargs.pop('trackers_blocked', '')
        self.training_type = kwargs.pop('training_type', 'AB')
        self.command_sequences = {}
        src = "[TRAINING]"
        logsPath = os.path.abspath('logs')
        self.hblogger = HBLogger.HBLogger(src, logsPath )
        msg = "\nvolume: {}\nintent: {}\ncategory: {}\ntrackers_blocked: {}\ntraining_type: {}".format(self.volume, self.intent, self.category, 
                                                                                                self.trackers_blocked, self.training_type)
        self.hblogger.log(msg)    
        
        #initilization
       
        #select crawl to perform
        

        if self.training_type == "AB":
            sitesToVisit = self.initABCrawSites() 
            for intent in sitesToVisit: 
                numSitesToVisit = 50
                if intent == 'intent':
                    numSitesToVisit = 54
                batch = 10
                counter = 0
                start = counter

                for category in sitesToVisit[intent]: 
                    start = counter
                    for i in list(range(counter, batch+1)):
                        counter+=1
                        print(counter)
                        if (counter %batch) == 0:
                            
                            end = counter+batch
                            print(sitesToVisit[intent][category][start:end])
                        if counter >= numSitesToVisit: 
                            break
                    sitesLeft = (numSitesToVisit - counter)
                    if sitesLeft >  batch: 
                        batch+=10
                    else: 
                        batch+=sitesLeft

                    
                
            
            
                    

        else:
            self.doMLCrawl()

    def newProcess(self, sitesToCrawl, managers):
        p = Process(target=self.crawlSites, args=(sitesToCrawl,managers,))
        p.start()
        return p            


    # print(managers)

    def initConfigParams(self,description=""):
        configBase = os.path.join(baseSrcPath, 'config')
        browserParamsPath = os.path.join(configBase, 'training', 'browser_params.json')
        managerParamsPath = os.path.join(configBase, 'training', 'manager_params.json')
        configParams = {}
        with open(managerParamsPath) as f: 
            prefs = json.load(f)
            manager_params = copy.deepcopy(prefs)

        with open(browserParamsPath) as f: 
            prefs = json.load(f)
            browser_params = [copy.deepcopy(prefs) for i in range(
                0, self.NUM_BROWSERS)]

            try: 
                path = "{}/{}".format(description, self.timestamp)
                configParams.update({"manager_params":copy.deepcopy(manager_params)})
                configParams.update({"browser_params":copy.deepcopy(browser_params)})
                configParams['manager_params']['data_directory'] = "results/data/{}".format(path)
                configParams['manager_params']['log_path'] = "results/logs/{}/openwpm-training-{}.log".format(path, description)
                configParams['manager_params']['database_name'] = "crawl-data-training-{}.sqlite".format(description)
                configParams['browser_params'][0]['profile_archive_dir'] = "profiles/training/{}".format(path)

                #####Enable for mob proxy
                # self.iab_params[iab]['manager_params']['mob_proxy'] = '/mnt/hgfs/archive_save/hars/{}_{}/{}'.format(timestamp,intent, iab)
                # if not os.path.exists('/mnt/hgfs/archive_save/hars/{}_{}'.format(timestamp, intent)):
                #     os.system('mkdir /mnt/hgfs/archive_save/hars/{}_{}'.format(timestamp, intent))
                # if not os.path.exists(self.iab_params[iab]['manager_params']['mob_proxy']):
                #     os.system("mkdir {}".format(self.iab_params[iab]['manager_params']['mob_proxy']))
                # if blocking_profile != "none":
                #     self.iab_params[iab]['browser_params'][0]["ublock-origin"] = True


            except Exception as e:
                msg = "Exception - initConfigParams - {}".format(e)
                self.hblogger.log(msg, level="ERROR")
                raise Exception
        return configParams

    def getManager(self, configParams):

            try:
                manager_d = configParams['manager_params']
                browser_ds = configParams['browser_params']
                # legacy key cleanup + convert
                man_d = dict(manager_d)
                br_list = [dict(b) for b in browser_ds]
                if 'log_directory' in man_d:
                    man_d['log_path'] = man_d.pop('log_directory')
                if 'database_name' in man_d:
                    dbn = man_d.pop('database_name')
                else:
                    dbn = 'crawl-data.sqlite'
                for b in br_list:
                    if 'profile_tar' in b:
                        b['seed_tar'] = b.pop('profile_tar')
                    if 'headless' in b and 'display_mode' not in b:
                        b['display_mode'] = 'headless' if b.pop('headless') else 'native'
                m_params = ManagerParams.from_dict(man_d)
                b_params = [BrowserParams.from_dict(b) for b in br_list]
                if not m_params.data_directory:
                    m_params.data_directory = Path("results/data")
                db_path = Path(m_params.data_directory) / dbn
                provider = SQLiteStorageProvider(str(db_path))
                manager = TaskManager(m_params, b_params, provider, None)
                return manager
            except Exception as e:
                msg = "Exception - init AB managers - {}".format(e)
                self.hblogger.log(msg, level="ERROR")
            
   
    def doCrawl(self, sitesToVisit, managers, num):
        print(sitesToVisit)
        
        process_pool = []
        process_pool.append(self.newProcess(sitesToVisit, managers))
        processes_complete = {}
        complete=False
        
        # while not complete:
        #     for p in process_pool:
        #         pid = p.pid
        #         name = p.name                
        #         p.join(timeout=1)
        #         alive = p.is_alive()
        #         processes_complete[pid] = {'name':name, "alive":alive}
        #         msg = "Process Pool - PID:{} name:{} alive:{}".format(pid, name, alive)
        #         self.hblogger.log(msg)
        #         for p_pid in processes_complete:
        #             complete = complete and not processes_complete[p_pid]['alive']
        #         time.sleep(1)
        return num
                



            
        
        # for i in intentIndexes:
        #     sitesToCrawl = []
        #     categories = []
        #     for category in intentSitesToVisit:
        #         sitesToCrawl.append(intentSitesToVisit[category][i])
        #         categories.append(category)
        #     self.crawlSites(sitesToCrawl, categories)

            

            
            
    # def doMLCrawl(self):
    #     pass
    # def waitUntilAllBrowsersDone(self, category): 
    #     all_done = False
    #     totalSleep = 0
    #     iabs = []
    
    #     #Wait unitil all browsers have finished
    #     while not all_done:  
    #         try:
    #             with open('trainingDone.json') as f: 
    #                 iabs = json.load(f)
    #         except:
    #             time.sleep(1)
    #             with open('trainingDone.json') as f: 
    #                 iabs = json.load(f)
    #         tmp = True
    #         for iab in iabs: 
    #             if iab in self.local_done: 
    #                 self.local_done[iab] = iabs[iab]
    #             msg = 'self.local_done {}'.format( self.local_done)
                
    #             self.hblogger.log(msg)
    #         for category in self.local_done: 
    #             site = self.alexCategorySites[category]
    #             tmp = tmp and bool(self.local_done[category]) 
    #             data = []   
    #             with open('trainingComplete.json') as f: 
    #                 data = json.load(f)
    #                 if bool(self.local_done[category]): 
    #                     key = site
    #                     if key in data:
    #                         if category not in data[key]:
    #                             data[key].append(category) 

    #                     else: 
    #                         data[key] = [category]
    #             with open('trainingComplete.json', 'w') as f: 
    #                 if data != []:      
    #                     json.dump(data, f, sort_keys=True, indent=4, separators =(',',':'))
    #         all_done = tmp 
    #         if all_done: 
    #             break
    #         else: 
    #             time.sleep(5)
    #             totalSleep +=5
    #             if totalSleep >= 60: 
    #                 msg = '[TRAINING WAIT_UNTIL_DONE] - reached timeout waiting for site to load'
                    
    #                 self.hblogger.log(msg)
    #                 break


    #     for i in iabs:  
    #         iabs[i] = 0
    #     with open('trainingDone.json', 'w') as f: 
    #         json.dump(iabs, f, indent=4, separators=(',',':'), sort_keys=True)


    def crawlSites(self, sitesToVisit, managers):
        visitNumber=0
        for index in range(len(managers)):
            manager = managers[index]
            site = sitesToVisit
            print(site)
            visitNumber+=1
            try:          
                command_sequences =  CommandSequence(site)
                            
                ###Uncomment for HAR logging
                # command_sequences.run_custom_function(pbjs.start_proxy, func_args=(site, proxy, server))
                # write = True
                # with open('write_out_har.json', 'w') as f: 
                #     json.dump({'writing':write}, f)
                #     time.sleep(1)

                # Start by visiting the page
                command_sequences.get(sleep=5, timeout=60)

                # dump_profile_cookies removed in current OpenWPM (cookies captured via instrumentation)
                # command_sequences.dump_profile_cookies(60)

                ###Uncomment for HAR logging
                # command_sequences.run_custom_function(pbjs.write_out_har, func_args=(site, timestamp,iab,intent,'ml_training',))

                # command_sequences.run_custom_function(self.pbjsUtils.signalDone,(category, visitNumber) )

                # index='**' synchronizes visits between the three browsers
                manager.execute_command_sequence(command_sequences)
                
 

            except Exception as e:
                msg = "Exception {} occurred, cleaning up and going on to next site".format( e)
                self.hblogger.log(msg,level="ERROR")
            
                with open('trainingDone.json', 'w') as f: 
                    json.dump(self.sites_done, f, indent=4, separators=(',',':'), sort_keys=True)
                pass


if __name__ == '__main__':
    from argparse import ArgumentParser as ap
    trainingParams = ['--volume',
                    '--intent',
                    '--category',
                    '--trackers_blocked',
                    '--training_type',
                    '--sites_to_visit'
                    ]
    parser = ap()                          
    for arg in trainingParams:
        parser.add_argument("{}".format(arg))
    args = parser.parse_args()

    args.volume = 1
    args.intent = False
    args.category = 'News'
    args.trackers_blocked = 'alphabet'
    args.training_type = 'AB'



    trainingCrawl = TrainingCrawl(kwargs=args)
