from __future__ import annotations

import json
import os
import random
import sys
import time
from subprocess import call

from HBLogger import HBLogger


top_20_trackers = { "alphabet": 1499729,
                    "yandex": 36861,
                    "oracle": 31048,
                    "appnexus": 28511,
                    "verizon": 23956,
                    "baidu": 16613,
                    "twitter": 15519,
                    "facebook": 14313,
                    "double_verify": 12689,
                    "adobe_systems": 10611,
                    "criteo": 10365,
                    "microsoft": 9052,
                    "quantcast": 8071,
                    "pubmatic": 7892,
                    "automattic": 7734,
                    "sovrn": 7346,
                    "integral_ad_science": 7247,
                    "comscore": 7205,
                    "exoclick": 7022,
                    "alibaba": 5840}

timestamp = ""
hblogger = HBLogger("[TRAINING]")

# with open('ml_training_mutex.json','w') as f:
#     json.dump({'ml_training_released_control': False}, f)

top_trackers_per_site = []
with open('top_trackers_per_site.json') as f:
    top_trackers_per_site = json.load(f)
    top_twenty_all_filters = [      "alphabet-all-filter",
                                    "yandex-all-filter",
                                    "oracle-all-filter",
                                    "appnexus-all-filter",
                                    "verizon-all-filter",
                                    "baidu-all-filter",
                                    "twitter-all-filter",
                                    "facebook-all-filter",
                                    "double_verify-all-filter",
                                    "adobe_systems-all-filter",
                                    "criteo-all-filter",
                                    "microsoft-all-filter",
                                    "quantcast-all-filter",
                                    "pubmatic-all-filter",
                                    "automattic-all-filter",
                                    "sovrn-all-filter",
                                    "integral_ad_science-all-filter",
                                    "comscore-all-filter",
                                    "exoclick-all-filter",
                                    "alibaba-all-filter"]


intentTrainingTypes = ['NO_INTENT','INTENT']
# intentTrainingTypes = ['NO_INTENT']

trainingRounds = 0
training_profile_dir = '~/headerBidding/TrackingProject/profiles/training'
results_dir = '~/headerBidding/TrackingProject/results/owpm/training'
archive_dir = '/mnt/hgfs/archive_save/ml_training'



def archive_training(timestamp, category, intent, training_profile_logs):
    msg = "archiving profile and results"
    hblogger.info(msg)
    timestamp = str(timestamp)
    crawl_dir = '{}/{}_{}'.format(archive_dir, timestamp, intent)    
    training_profile_logs['storage_location'] = crawl_dir+'_TRAINING'+'.tar'

    manifest = training_profile_logs

    path = os.path.join(crawl_dir, 'manifest_{}.json'.format(timestamp))
    with open(path,'w') as f: 
        json.dump(manifest, f, separators=(',',':'), indent=4)
     
    if not os.path.exists('{}'.format(crawl_dir)):
        os.system('mkdir {}'.format(crawl_dir))
    
    if os.path.exists('{}'.format(crawl_dir)):
        
        training_profile = os.path.join(training_profile_dir, timestamp, category)
        results_folder = os.path.join(results_dir, timestamp, category)
        
        # msg = "parsing HAR"
        # 
        # hblogger.info(msg)
        # old_hars_path = "/mnt/hgfs/archive_save/hars/{}_{}/{}".format(timestamp, intent, category)
        # new_hars_path = "{}/hars".format(crawl_dir)
        # os.system('python parse_har.py --har {} --output_path {} --ml_type {} --id {}'.format(old_hars_path,
        #                                                                             crawl_dir,
        #                                                                             'training',
        #                                                                             training_profile_logs['training_id']))

        msg = "copied profile and results"
        
        hblogger.info(msg)

        os.system('mv {} {}/profile'.format(training_profile, crawl_dir))
        os.system('mv {} {}/results'.format(results_folder, crawl_dir))
        # os.system('mv {} {}'.format(old_hars_path, new_hars_path))



        msg = "tarring up files"
        
        hblogger.info(msg)

                
        # os.system('tar -C {} -cvf {}_TRAINING.tar hars profile results manifest_{}.json'.format(crawl_dir, crawl_dir, timestamp))
        os.system('tar -C {} -cvf {}_TRAINING.tar profile results manifest_{}.json'.format(crawl_dir, crawl_dir, timestamp))

        os.system('echo {} > trainingComplete.json')
        os.system('rm -rf {}'.format(crawl_dir))
        msg = "removing profile and results"
        
        hblogger.info(msg)
        os.system('rm -rf {}/{}'.format(training_profile_dir,timestamp))
        os.system('rm -rf {}/{}'.format(results_dir,timestamp))
        # os.system('rm -rf /mnt/hgfs/archive_save/hars/{}_{}'.format(timestamp, intent))
        # os.system('rm -rf /mnt/hgfs/archive_save/ml_training/hars/*')

        training_manifest = []
        with open('/mnt/hgfs/archive_save/ml_testing/training_manifest.json') as f: 
            training_manifest = json.load(f)

        training_manifest.update({training_profile_logs['training_id']: manifest})

        with open('/mnt/hgfs/archive_save/ml_testing/training_manifest.json', 'w') as f: 
            json.dump(training_manifest, f, separators=(',',':'), indent=4)

        msg = "archive complete"
        
        hblogger.info(msg)


    else:
        msg = 'file creation error'
        
        hblogger.info(msg)



block_all = []
blocking_profiles = ['all']
# blocking_profiles = ['none']



rounds_complete = []
# ml_training_mutex = []
# ml_testing_mutex = []
training_manifest_file = []
checked_training_rounds = False
skip_block_profile = 0
skip_intent = 0
#TODO need to add random blocking
while trainingRounds < 100000: 
    #pick up where we left off
    if not checked_training_rounds:
        with open('/mnt/hgfs/archive_save/ml_testing/training_manifest.json') as f:
            training_manifest_file = json.load(f)
            for value in training_manifest_file: 
                try: 
                    rounds_complete.append(int(value.split('_')[0]))
                except: 
                    pass
                skip_intent+=1
                skip_block_profile+=1
            if rounds_complete != []:
                rounds_complete = sorted(rounds_complete)
                print(rounds_complete)
                trainingRounds = rounds_complete[-1]
                trainingRounds+=1
        checked_training_rounds = True
        
    #Brosermobproxy process sticks around, I need to figure out how to gracefully close it
    # os.system('pkill -f java')    
    # with open('ml_testing_mutex.json') as f: 
    #     ml_testing_mutex = json.load(f)

    # with open('ml_training_mutex.json','w') as f:
    #     json.dump({'ml_training_released_control': ml_testing_mutex['ml_testing_req_control']}, f)
    
    # while(ml_testing_mutex['ml_testing_req_control']):
    #     msg = "WAITING FOR TESTING TO COMPLETE"
    #     
    #     hblogger.info(msg)
    #     time.sleep(60)
    #     with open('ml_testing_mutex.json') as f: 
    #         ml_testing_mutex = json.load(f)

    # with open('ml_training_mutex.json','w') as f:
    #     json.dump({'ml_training_released_control': False}, f)
    
    numberOfSitesToVisit = random.randint(1,10)
    # numberOfSitesToVisit = 1
    tracker_to_block = random.randint(0,19)
    all_rules = []

    for blocking_profile in blocking_profiles:
        if skip_block_profile > 0:
            skip_block_profile-=1
            msg = "BLOCKING PROFILE {}, skip_block_profile {}".format(blocking_profile, skip_block_profile)
            
            hblogger.info(msg)
        else: 
            msg = "BLOCKING PROFILE {}".format(blocking_profile)
            
            hblogger.info(msg)
            # numberOfSitesToVisit = 50
            tb = ""
            filter_name = ""
            rules = []
            categoryType = categorys[random.randint(0,15)]
            if blocking_profile != "none":
                tb = tracker_to_block

                    
            if blocking_profile == 'all': 
                fn_all = ""
                fn_all = os.path.join('ent_abp', top_twenty_all_filters[tracker_to_block].split('-filter')[0]+'.txt')
                filter_name = top_twenty_all_filters[tracker_to_block]
                with open(fn_all) as f: 
                    rules = f.readlines()
            if filter_name != "": 
                ublock_origin_rules = []
                with open('./firefox_extensions/ublock_origin/storage.js') as f: 
                    ublock_origin_rules = json.load(f)
                    content_url = ublock_origin_rules['availableFilterLists'][filter_name]['contentURL']
                    ublock_origin_rules['selectedFilterLists'] = ['ublock-filters']
                    ublock_origin_rules['availableFilterLists']['ublock-filters']['contentURL'] = content_url
                
                with open('./firefox_extensions/ublock_origin/storage.js','w') as f: 
                    json.dump(ublock_origin_rules, f, separators=(',',':'), indent=4)
                
                with open('./src/ublock_origin-1.14.10/assets/ublock/filters.txt','w') as f: 
                    for r in rules: 
                        f.write(r)
                local_xpi = 'ublock_origin-1.14.10.xpi'
                ublock_folder = "ublock_origin-1.14.10"
                msg = "PACKAGING RULES AND UBLOCK EXTENSION"
                
                hblogger.info(msg)
                extension_folder = "./firefox_extensions/ublock_origin/"
                os.system('cd {}; zip -r -FS ../{} *;cd ../'.format(ublock_folder, local_xpi))
                msg = "COPYING UBLOCK EXTENSION TO FIREFOX"
                
                hblogger.info(msg)
                os.system('cp {} {}'.format(local_xpi, extension_folder))
                msg = "COMPLETED UBLOCK COPY"
                
                hblogger.info(msg)


            entity = "" 
            if tb != "":
                entity = top_twenty_all_filters[tracker_to_block].split('-filter')[0]
            else: 
                entity = 'NOT_BLOCKING'
            # categoryType = categorys[random.randint(0,15)]
            # All crawls have an associatated time stamp. 
            with open('timeStamp.json') as f: 
                data = json.load(f)
                if data['timestamp'] != "":
                    timestamp = data['timestamp']
                else:
                    timestamp = int(time.time())
        
        for trainingTypes in intentTrainingTypes: 
            if skip_intent > 0: 
                msg = "SKIPPING {}, skip_intent {}".format(trainingTypes, skip_intent)
                hblogger.info(msg)                
                skip_intent-=1
                skip_block_profile-=1
                continue

            else: 
                msg = "TRAINING ROUNDS {} BLOCK_PROFILE {},  TRAINING INTENT TYPE {}".format(trainingRounds, blocking_profile, trainingTypes)
                
                hblogger.info(msg) 
                training_profile = {'training_id': "{}_{}".format(trainingRounds, blocking_profile),
                        'timestamp': "{}".format(timestamp),
                        'filter_name': "{}".format(filter_name),
                        'blocking_rules': "{}".format(rules),
                        'category': categoryType,
                        'volume': numberOfSitesToVisit,
                        'entity': entity,
                        'intent' : trainingTypes,
                        'storage_location': ""
                    }
                msg = "PROFILE {}".format(training_profile)
                
                hblogger.info(msg)
                try: 
                    crawl_dir = '{}/{}_{}'.format(archive_dir, timestamp,trainingTypes)
                    if not os.path.exists('{}'.format(crawl_dir)):
                        os.system('mkdir {}'.format(crawl_dir))
                        # os.system('mkdir {}/hars'.format(crawl_dir))
                        os.system('mkdir {}/results'.format(crawl_dir))
                        os.system('mkdir {}/profile'.format(crawl_dir))

                    # os.system('python trainingCrawl.py --intent {} --timestamp {} --volume {} --category {}'.format(trainingTypes, 
                    #                                                                                                 timestamp, 
                    #                                                                                                 numberOfSitesToVisit, 
                    #                                                                                                 categoryType))    
                    os.system('python trainingCrawl.py --intent {} --timestamp {} --volume {} --category {} --blocking {} --tracker_ent {}'.format(trainingTypes, 
                                                                                                                    timestamp, 
                                                                                                                    numberOfSitesToVisit, 
                                                                                                                    categoryType,
                                                                                                                    blocking_profile,
                                                                                                                    entity))      
                    #Brosermobproxy process sticks around, I need to figure out how to gracefully close it
                    # os.system('pkill -f java')

                    archive_training(timestamp, categoryType, trainingTypes, training_profile)
                    # update_block_lists()
                    
                    with open('timeStamp.json', 'w') as f:
                        json.dump({'timestamp':""}, f)

                except Exception as e: 
                    msg = "{}".format(e)
                    
                    hblogger.info(msg)
                    with open('timeStamp.json', 'w') as f:
                        json.dump({'timestamp':timestamp}, f)
                    
                    raise Exception   
                trainingRounds+=1   







