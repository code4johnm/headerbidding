import os
import time
import json
import random
from HBLogger import HBLogger
import tempfile
from threading import Thread
class MLTesting:
    def __init__(self):
        self.training_profiles = {}
        self.hblogger = HBLogger('[ML_TESTING]')
        self.profiles_completed = []
        with open('profiles_completed.json') as f: 
            self.profiles_completed = json.load(f)['profiles_completed']

        # with open('ml_testing_mutex.json', 'w') as f: 
        #     json.dump({'ml_testing_req_control': False}, f)
        trackers = {}


    def archive(self, folder, dst, crawl_type):
        os.system('tar -C {} -cvf /mnt/hgfs/archive_save/ml_testing/ready_for_analysis/{}_{}.tar training testing'.format(folder, dst,crawl_type))
  


    def unpack(self, srcPath, dstPath):
        msg = 'unpacking src {} to {} '.format( srcPath, dstPath)
        
        self.hblogger.log(msg)
        os.system('tar -xvf {} -C {}'.format(srcPath, dstPath))

    
    def get_training_profile_list(self):
        with open('/mnt/hgfs/archive_save/ml_testing/training_manifest.json') as f: 
            self.training_profiles = json.load(f)
    
    def monitor_thread(self):
        msg = 'STARTING MONITOR THREAD '
        
        self.hblogger.log(msg)
        while(1):

            self.get_training_profile_list()
            #DEBUG
            # msg = '{} GOT PROFILE LIST \n{}\n'.format( self.training_profiles)
            # 
            # self.hblogger.log(msg) 

            try: 

                for profile in self.profiles_completed:
                    #DEBUG
                    # msg = '{} REMOVING PROFILE {} from self.training_profiles'.format( profile)
                    # 
                    # self.hblogger.log(msg)
 
                    self.training_profiles.pop(profile)
                msg = 'PROFILE LIST TRIMMED \n{}\n'.format(self.training_profiles)
                
                self.hblogger.log(msg) 
            except Exception as e: 
                msg = 'Exception popping{} '.format( e)
                
                self.hblogger.log(msg) 

            self.tp = sorted(self.training_profiles)
            for profile in self.tp:
                if profile in self.profiles_completed or profile == "": 
                    continue 
                """ 
                make sure ml_training is taking a break, set the testing mutex. 
                The browser commands are modified and launching multiple browsermobproxy
                instances seems to cause the proxy to not write out HARS properly. So 
                just launch testing every so often, complete some profiles, then return 
                crawling to ml_training module. 
                """
         

                ninety_minutes_old = int(self.training_profiles[profile]['timestamp'])+ 5400
                if int(time.time()) > ninety_minutes_old:
                    msg = 'SOME TRAINING PROFILES ARE READY'
                    
                    self.hblogger.log(msg)
                    # ml_training_mutex = []

                    # with open('ml_testing_mutex.json', 'w') as f: 
                    #     json.dump({'ml_testing_req_control': True}, f)

                    # with open('ml_training_mutex.json') as f: 
                    #     ml_training_mutex = json.load(f)
                    
                    # while (not ml_training_mutex['ml_training_released_control']):
                    #     msg = 'MONITOR THREAD - REQUESTED TESTING CONTROL, WAITING FOR ML_TRAINING TO COMPLETE RUN {}'.format( self.tp[-1])
                    #     
                    #     self.hblogger.log(msg)
                    #     time.sleep(1)
                    #     with open('ml_training_mutex.json') as f: 
                    #         ml_training_mutex = json.load(f)

                    retVal = 'fail'
                    retVal = self.run_testing(self.training_profiles[profile])
                    if retVal == 'fail':
                        msg = 'MONITOR THREAD - Training profile folder empty {}'.format( profile)
                        
                        self.hblogger.log(msg)
                    if profile != "":
                        self.profiles_completed.append(profile)
                    with open('profiles_completed.json', 'w') as f: 
                        json.dump({'profiles_completed': self.profiles_completed}, f)
            # with open('ml_testing_mutex.json', 'w') as f: 
            #     json.dump({'ml_testing_req_control': False}, f)      
            msg = 'MONITOR THREAD -  SLEEPING, NO PROFILES MATURE'
            
            self.hblogger.log(msg)

            time.sleep(60)
            msg = 'MONITOR THREAD - WAKING UP '
            
            self.hblogger.log(msg)
        
    def run_testing(self, profile):
        #Brosermobproxy process sticks around, I need to figure out how to gracefully close it
        # os.system('pkill -f java')         
        ranks = []
        with open('pbjs_sites.json') as f: 
            ranks = json.load(f)
            ranks = ranks.keys()
        print(ranks)
        rand_site = ranks[random.randint(0,len(ranks)-1)]
        crawl_type = ""
        timestamp = str(profile['timestamp'])
        if 'NO_INTENT' in profile['storage_location']: 
            crawl_type = 'NO_INTENT'
        else:
            crawl_type = 'INTENT'
        srcUnpack = profile['storage_location']
        dstUnpack = tempfile.mkdtemp()
        self.unpack(srcUnpack, dstUnpack)
        training_profile = os.path.join(dstUnpack, 'profile')
        testing_profile_folder = './profiles/testing/load/'

        msg = 'Copying training profile {} to testing profile folder {} '.format( training_profile+'/*', testing_profile_folder)
        
        self.hblogger.log(msg)

        msg = 'LOADED TRAINING PROFILE {}'.format( profile)
        
        self.hblogger.log(msg)

        testingPath = ""
        os.system('cp -r {} {}'.format(training_profile+'/*', testing_profile_folder))
        category = []
        try:
            category = os.listdir(testing_profile_folder)[0]
        except: 
            pass
        if category == []:
            return 'fail'

        file_name = profile['storage_location'].split('/')[-1].split('.tar')[0].replace('_TRAINING','')
        finalized_path =  os.path.join('/mnt/hgfs/archive_save/ml_testing', 'ready_for_analysis', file_name)
        #/mnt/hgfs/archive_save/ml_testing/ready_for_analysis/timestamp_<INTENT/NO_INTENT>/testing
        testingPath = os.path.join(finalized_path, 'testing') 
        if not os.path.exists(finalized_path): 
            # /mnt/hgfs/archive_save/ml_testing/ready_for_analysis/timestamp_<INTENT/NO_INTENT>
            os.mkdir(finalized_path) 

            #/mnt/hgfs/archive_save/ml_testing/ready_for_analysis/timestamp_<INTENT/NO_INTENT>/testing
            testingPath = os.path.join(finalized_path, 'testing') 

            #/mnt/hgfs/archive_save/ml_testing/ready_for_analysis/timestamp_<INTENT/NO_INTENT>/training
            trainingPath = os.path.join(finalized_path, 'training')
            os.mkdir(testingPath)
            os.mkdir(trainingPath)

            #/mnt/hgfs/archive_save/ml_testing/ready_for_analysis/timestamp_<INTENT/NO_INTENT>/testing/results
            os.mkdir(os.path.join(testingPath, 'results')) 
            
            #/mnt/hgfs/archive_save/ml_testing/ready_for_analysis/timestamp_<INTENT/NO_INTENT>/testing/bids
            os.mkdir(os.path.join(testingPath, 'results', 'bids')) 
            
            #/mnt/hgfs/archive_save/ml_testing/ready_for_analysis/timestamp_<INTENT/NO_INTENT>/testing/owpm
            os.mkdir(os.path.join(testingPath, 'results', 'owpm'))

            #/mnt/hgfs/archive_save/ml_testing/ready_for_analysis/timestamp_<INTENT/NO_INTENT>/testing/har
            # os.mkdir(os.path.join(testingPath, 'hars')) 

            #/tmp/tmpfile/<profile, hars, results> -> #/mnt/hgfs/archive_save/ml_testing/ready_for_analysis/timestamp_<INTENT/NO_INTENT>/training
            os.system('mv {} {}'.format(dstUnpack+'/*', trainingPath))
        else: 
            msg = 'path exists {}'.format( finalized_path)
            
            self.hblogger.log(msg)
        
        try: 
            print(crawl_type)
            site = rand_site
            site_name = json.load(open('pbjs_sites.json'))[site]
            url = site_name.split('://')[1]
            testing_results = os.path.join(testingPath, 'results')
            # new_hars_path = os.path.join(testingPath, 'hars')
            # old_hars_path = '/mnt/hgfs/archive_save/hars/HAR_{}.json'.format(url)

            # print(old_hars_path, new_hars_path)
            # call the testing script
            msg = "timestamp {} crawl_type {}, site {} category {}".format(timestamp, crawl_type, site, category)
            
            self.hblogger.log(msg)   
            os.system('python testingCrawl.py --timestamp {} --crawl_type {} --site {} --category {}'.format(timestamp, crawl_type, site, category))
            #Brosermobproxy process sticks around, I need to figure out how to gracefully close it
            #save off results to ready_for_analysis folder
            bid_folder = ""
            if 'NO_INTENT' in crawl_type: 
                bid_folder = 'bids_no_intent'
            else:
                bid_folder = 'bids_intent'
            site_name = site_name.split('://')[1]
            if '/' in site_name: 
                site_name = site_name.split('/')[0]
            site_name = site_name+'_{}.json'.format(category)  
            #Brosermobproxy process sticks around, I need to figure out how to gracefully close it
            # os.system('pkill -f java')
            testing_bids = os.path.join('./results/{}/'.format(bid_folder), site_name)
            os.system('cat {}'.format(testing_bids))
            
            msg = 'moving testing results {} to finalized results folder {}/bids '.format( testing_bids, testing_results)
            
            self.hblogger.log(msg)
            testing_owpm = './results/owpm/testing/{}/*'.format(timestamp)
            
            #parse the har
            # os.system('python parse_har.py --har {} --output_path {} --ml_type {} --id {}'.format(hars,
            #                                                                                       finalized_path,
            #                                                                                       'testing',
            #                                                                                       profile['id']))

            os.system('mv {} {} '.format(testing_bids, os.path.join(testing_results, 'bids')))
            os.system('mv {} {}'.format(testing_owpm, os.path.join(testing_results, 'owpm')))

            # msg = 'Moving testing HARS {} to finalized testing hars folder {} '.format( old_hars_path, new_hars_path)
            # 
            # self.hblogger.log(msg)
            # os.system('cp {} {}'.format(old_hars_path, new_hars_path))
            # os.system('rm {}'.format(old_hars_path))
            
            # tar up training and testing data
            self.archive(finalized_path, timestamp, crawl_type)
            os.system('rm -rf {}'.format(finalized_path))
            os.system('rm -rf {}/*'.format(testing_profile_folder))
            os.system('rm -rf ./results/owpm/testing/*')
            os.system('rm -rf ./profiles/testing/1*')


            msg = 'Done copying. '
            
            self.hblogger.log(msg)

            #clear out the bids files 
            os.system('python create_bids_files.py')
            msg = 'Cleared Bid files. '
            
            self.hblogger.log(msg)
            os.system('python reindex_prebid.py')
            msg = 'REINDEXED PB SITES. '
            
            self.hblogger.log(msg)

            return 'success'
        except Exception as e:
            msg = 'Exception {} '.format( e)
            
            self.hblogger.log(msg) 

        
        


if __name__ == "__main__":
    print('here')
    mlt = MLTesting()
    mlt.monitor_thread()