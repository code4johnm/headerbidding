import os
import sys 
import json
import time
import arff
from HBLogger import HBLogger
from pprint import pprint

"""
seed profile trackers detected: 


ml template:
    id, bidder, mediaType, size, trTRCK1, ..., trTRCK20, tstTRCK1, ... , tstTRCK20, cpm

"""
class ml_analysis: 

    def __init__(self): 
        self.start = time.time()
        self.output_path = ""
        self.totalTrainingRounds = 0
        self.totalTestingRounds = 0  
        self.numberOfBidsPlaced = 0
        self.totalCpm = 0.0      
        self.trainingVolume = 0   
        self.fileConter = 0
        self.global_vars = ['self.totalTrainingRounds',
                            'self.totalTestingRounds',
                            'self.totalCpm',
                            'self.numberOfBidsPlaced',
                            'self.trainingVolume',
                            'self.categoryCount',
                            'self.categoryCPM',
                            'self.total_trackers_percentage',
                            'self.total_tracker_count',
                            'self.tracker_count_per_category',
                            'self.bidders_per_category'
                            ]

        self.save_data = {}
        with open('ml_analysis_save.json') as f: 
            self.save_data = json.load(f)

        self.categorys = [  "Adult",
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
                            "BLOCK"]
        self.categoryCount = {  "Adult":0,
                                "Arts":0,
                                "Business":0,
                                "Computers":0,
                                "Games":0,
                                "Health":0,
                                "Home":0,
                                "Kids_and_Teens":0,
                                "News":0,
                                "Recreation":0,
                                "Reference":0,
                                "Regional":0,
                                "Science":0,
                                "Shopping":0,
                                "Society":0,
                                "Sports":0,
                                "BLOCK":0}

        self.categoryCPM = {    "Adult":0.0,
                                "Arts":0.0,
                                "Business":0.0,
                                "Computers":0.0,
                                "Games":0.0,
                                "Health":0.0,
                                "Home":0.0,
                                "Kids_and_Teens":0.0,
                                "News":0.0,
                                "Recreation":0.0,
                                "Reference":0.0,
                                "Regional":0.0,
                                "Science":0.0,
                                "Shopping":0.0,
                                "Society":0.0,
                                "Sports":0.0,
                                "BLOCK":0.0}  



        self.trackers_percentage = {   "alphabet":0.0,
                                        "yandex":0.0,
                                        "oracle":0.0,
                                        "appnexus":0.0,
                                        "verizon":0.0,
                                        "baidu":0.0,
                                        "twitter":0.0,
                                        "facebook":0.0,
                                        "double_verify":0.0,
                                        "adobe_systems":0.0,
                                        "criteo":0.0,
                                        "microsoft":0.0,
                                        "quantcast":0.0,
                                        "pubmatic":0.0,
                                        "automattic":0.0,
                                        "sovrn":0.0,
                                        "integral_ad_science":0.0,
                                        "comscore":0.0,
                                        "exoclick":0.0,
                                        "alibaba": 0.0}
        self.total_trackers_percentage = {   "alphabet":0.0,
                                        "yandex":0.0,
                                        "oracle":0.0,
                                        "appnexus":0.0,
                                        "verizon":0.0,
                                        "baidu":0.0,
                                        "twitter":0.0,
                                        "facebook":0.0,
                                        "double_verify":0.0,
                                        "adobe_systems":0.0,
                                        "criteo":0.0,
                                        "microsoft":0.0,
                                        "quantcast":0.0,
                                        "pubmatic":0.0,
                                        "automattic":0.0,
                                        "sovrn":0.0,
                                        "integral_ad_science":0.0,
                                        "comscore":0.0,
                                        "exoclick":0.0,
                                        "alibaba": 0.0}
      

        self.tracker_count = {  "alphabet":0,
                                "yandex":0,
                                "oracle":0,
                                "appnexus":0,
                                "verizon":0,
                                "baidu":0,
                                "twitter":0,
                                "facebook":0,
                                "double_verify":0,
                                "adobe_systems":0,
                                "criteo":0,
                                "microsoft":0,
                                "quantcast":0,
                                "pubmatic":0,
                                "automattic":0,
                                "sovrn":0,
                                "integral_ad_science":0,
                                "comscore":0,
                                "exoclick":0,
                                "alibaba": 0}
        self.total_tracker_count = {  "alphabet":0,
                                "yandex":0,
                                "oracle":0,
                                "appnexus":0,
                                "verizon":0,
                                "baidu":0,
                                "twitter":0,
                                "facebook":0,
                                "double_verify":0,
                                "adobe_systems":0,
                                "criteo":0,
                                "microsoft":0,
                                "quantcast":0,
                                "pubmatic":0,
                                "automattic":0,
                                "sovrn":0,
                                "integral_ad_science":0,
                                "comscore":0,
                                "exoclick":0,
                                "alibaba": 0}                                

        self.tracker_count_per_category = {}  
        self.bidders_per_category = {}                             

    """
    manifest = {'training_id': "{}_{}".format(trainingRounds, blocking_profile),
                    'timestamp': "{}".format(timestamp),
                    'filter_name': "{}".format(filter_name),
                    'blocking_rules': "{}".format(rules),
                    'category': categoryType,
                    'volume': numberOfSitesToVisit,
                    'entity': entity,
                    'intent' : trainingTypes,
                    'storage_location': ""
                }
    """

    def get_training_manifest_params(self, path, timestamp):
        training_dir = os.path.join(path, 'training')
        training_files = os.listdir(training_dir)
        manifest_file = ""
        for m in training_files:
            if timestamp in m: 
                manifest_file = m
        manifest = []
        with open(os.path.join(training_dir, manifest_file)) as f: 
            manifest = json.load(f)
        return manifest 


    def get_training_category(self, path):
        pass
    def get_cat_headers(self, categories):
        category_output = ""
        category_output+='{}\t{:<14}'.format('\n', '')
        for c in categories:
            category_output+="{:<9}".format(c[0:4])  
        category_output+='{}\t{:<14}'.format('\n', '')
        for c in categories: 
            category_output+="{:<9}".format('-----')
        return category_output

    def get_bids(self, id, timestamp, category, volume, intent, entity, path):
        bids_dir = os.path.join(path, 'testing', 'results', 'bids')
        bid_files = os.listdir(bids_dir)
        all_bids = {id:[]}
        
        for bids_file in bid_files:

            path = os.path.join(bids_dir, bids_file)
            bids = []

            with open(path) as f: 
                bids = json.load(f)
            if bids:
                
                with open('bidcheck/{}_{}'.format(bids_file, self.fileConter), 'w+') as f: 
                    json.dump(bids, f)
                    self.fileConter+=1
            for cat in bids: 
                for site in bids[cat]:
                    for bid_no in bids[cat][site]:
                        for bid in bids[cat][site][bid_no]:
                            try:
                                bidder = bid['bidder']
                                cpm = float(bid['cpm'])
                                size = 'not_included_in_bid'
                                if 'size' in bid['bid']:
                                    size = bid['bid']['size']
                                mediaType = 'not_included_in_bid'
                                if 'mediaType' in bid['bid']:
                                    mediaType = bid['bid']['mediaType']
                                bid_data = {'bidder':bidder, 
                                            'cpm':cpm, 
                                            'size':size, 
                                            'mediaType':mediaType, 
                                            'category':category,
                                            'volume': volume, 
                                            'intent': intent, 
                                            'blocking_entity': entity,
                                            'site':site}
                                if bidder in self.bidders_per_category:
                                    if category in self.bidders_per_category[bidder]:
                                        if 'count' in self.bidders_per_category[bidder][category]:
                                            self.bidders_per_category[bidder][category]['count']+=1
                                        else:
                                            self.bidders_per_category[bidder][category]['count']=1 
                                        if 'cpm' in self.bidders_per_category[bidder][category]:
                                            self.bidders_per_category[bidder][category]['cpm']+=cpm
                                        else:
                                            self.bidders_per_category[bidder][category]['cpm']=cpm                                             
                                    else:
                                        self.bidders_per_category[bidder][category] = {'count':1, 'cpm':cpm}
                                else: 
                                    self.bidders_per_category[bidder] = {category: {'count':1, 'cpm':cpm}}

                                all_bids[id].append(bid_data)
                                self.numberOfBidsPlaced+=1 
                                self.totalCpm+=float(cpm)
                                if category in self.categoryCPM:
                                    self.categoryCPM[category]+=float(cpm)
                                else: 
                                    self.categoryCPM = float(cpm)
                            except Exception as e: 
                                print("Exception {}".format(e))
                                pass
        return all_bids


    def get_trackers(self, path, category, ml_type="training"):
        category_dir = ""

        with open(os.path.join(self.output_path, 'trackers_count.json'), 'w+') as f:
            json.dump({}, f)      
        if ml_type == 'training': 
            category_dir = os.path.join(path, 'training', 'results')
        else: 
            category_dir = os.path.join(path, 'testing', 'results', 'owpm')
        cat = os.listdir(category_dir)[0]
        sqlite_dir = os.listdir(os.path.join(category_dir, cat))
        sqlite_file = ""
        for file in sqlite_dir: 
            if '.sqlite' in file: 
                sqlite_file = file
        sqlite_path = os.path.join(category_dir, cat, sqlite_file)
 


        sys.path.append('./src/measure_tools')
        sys.path.append('./src/measure_tools/crawl_utils')
        os.system('python measure_tools/get_tp_and_owners.py --sqlite_file {} --output {}'.format(sqlite_path, self.output_path))
        tp_files = os.listdir(self.output_path)
        tp_path = ""
        for t in tp_files:
            if 'third_party_requests' in t: 
                tp_path = os.path.join(self.output_path, t)
        
        os.system('python measure_tools/parse_1.py --output {} --tp_file {}'.format(self.output_path, tp_path))
        os.system('python measure_tools/parse_2.py --output {}'.format(self.output_path))
        os.system('python measure_tools/parse_3.py --output {} --ml_type {}'.format(self.output_path, ml_type))
        trackers_seen = []
        tracker_count = {}
        tracker_percentage = {}
        for tracker in self.tracker_count: 
            tracker_count[tracker] = self.tracker_count[tracker] 

        for tracker in self.trackers_percentage: 
            tracker_percentage[tracker] = self.trackers_percentage[tracker]            
        total = 0
        track_count_path = ""
        if ml_type == 'training':
            tracker_count_path = os.path.join(self.output_path, 'training_trackers_count.json')
        else:
            tracker_count_path = os.path.join(self.output_path, 'testing_trackers_count.json')
        with open(tracker_count_path) as f:
            trackers_seen = json.load(f)
        for tracker in trackers_seen: 
            if tracker in self.tracker_count: 
                count = trackers_seen[tracker]
                tracker_count[tracker] = count
                if ml_type in self.tracker_count_per_category:
                    if tracker in self.tracker_count_per_category[ml_type]:
                        if category in self.tracker_count_per_category[ml_type][tracker]:
                            self.tracker_count_per_category[ml_type][tracker][category] += count
                        else: 
                            self.tracker_count_per_category[ml_type][tracker][category] = count
                    else: 
                        self.tracker_count_per_category[ml_type][tracker] = { category: count}
                else: 
                    self.tracker_count_per_category[ml_type] = { tracker: {category: count}}                

        
            total += trackers_seen[tracker]
        for tracker in tracker_count: 
            if total != 0: 
                if tracker in trackers_seen:
                    tracker_percentage[tracker] = float(tracker_count[tracker])/float(total)
             
            # else: 
            #     tracker_percentage[tracker] = 0.0
        return tracker_percentage

    def create_restore_point(self):
        with open('ml_analysis_save.json', 'w+') as f: 
            json.dump(self.save_data, f, indent=4, separators=(',',':'))
        print('[ML ANALYSIS] {} - CREATED RESTORE POINT \n'.format(time.asctime()))

    def restore_global_vars(self):
        if self.save_data:
            if 'global_vars' in self.save_data:
                for g in self.global_vars: 
                    if g not in self.save_data['global_vars']:
                        return False
                for g in self.save_data['global_vars']:
                    # print('[ML ANALYSIS] {} - Restoring {} to {} \n'.format(time.asctime(),g, self.save_data['global_vars'][g]))
                    name = g.split('self.')[1]
                    setattr(self, name, self.save_data['global_vars'][g])

        return True

    def get_features(self):
        ret = self.restore_global_vars()
        all_rows = {'bids':[], 'training':[], 'testing':[]}
        if 'all_rows' in self.save_data:
            if self.save_data['all_rows']:
                all_rows = self.save_data['all_rows']
            else: 
                ret = False
            # print(self.save_data['all_rows']['bids'])
        ml_analysis_path = '/mnt/hgfs/archive_save/ml_testing/ready_for_analysis'
        tmp_path = os.path.join(ml_analysis_path, 'tmp')

        if not os.path.exists(tmp_path):
            os.mkdir(tmp_path)

        self.output_path = os.path.join(tmp_path, 'output')
        os.system('rm -rf {}/*'.format(self.output_path))

        if not os.path.exists(self.output_path):
            os.mkdir(self.output_path)

        if not os.path.exists(os.path.join(self.output_path, 'ent_abp')):
            os.mkdir(os.path.join(self.output_path, 'ent_abp'))

        os.system('cp measure_tools/ent_abp/* {}/ent_abp'.format(self.output_path))
        analysis_tars = os.listdir(ml_analysis_path)

        for tar in analysis_tars: 
            if '.tar' not in tar: 
                analysis_tars.remove(tar)
        total_tars = len(analysis_tars)
        tars_processed = 0
        bidsThisRound = 0
        empty_bids = 0
        total_empty_bids = 0
        for t in analysis_tars: 
            try: 
                # if self.numberOfBidsPlaced > 1: 
                #     break
                if 'tars_processed' in self.save_data:  
                    if self.save_data['tars_processed']:
                        if t in self.save_data['tars_processed']:
                            print('[ML ANALYSIS] {} - SKIPPING TAR {} - {}/{}'.format(time.asctime(), t,tars_processed, total_tars))
                            tars_processed+=1                   
                            continue
                        else: 
                            self.save_data['tars_processed'].append(t)                                                                       
                else: 
                    self.save_data['tars_processed'] = [t]
                if (len(analysis_tars) - tars_processed) < 5: 
                    break
         
                
                os.system('rm -rf {}/*'.format(tmp_path))
                
                if not os.path.exists(self.output_path):
                    os.mkdir(self.output_path)
                
                self.output_path = os.path.join(tmp_path, 'output')

                os.system('rm -rf {}/*'.format(self.output_path))



                if not os.path.exists(os.path.join(self.output_path, 'ent_abp')):
                    os.mkdir(os.path.join(self.output_path, 'ent_abp'))

                print('\n[ML ANALYSIS] {:<20} - PROCESSING {:<20} - {}/{}'.format(time.asctime(), t,tars_processed, total_tars))
                os.system('rm -rf {}/*'.format(self.output_path))
                if not os.path.exists(os.path.join(self.output_path, 'ent_abp')):
                    os.mkdir(os.path.join(self.output_path, 'ent_abp'))
                trackers_in_training = {}
                trackers_in_testing = {}
                bids = {}
                timestamp = t.split('_')[0]
                tar_path = os.path.join(ml_analysis_path, t)
                os.system('tar -xf {} -C {}'.format(tar_path, tmp_path))
                if not os.path.exists(os.path.join(tmp_path,  'training')):
                    tars_processed+=1                   
                    continue

                manifest = self.get_training_manifest_params(tmp_path, timestamp)

                id = manifest['training_id']
                category = manifest['category']
                volume = manifest['volume']
                blocking_entity = manifest['entity']
                training_intent = manifest['intent']
                self.categoryCount[category]+=int(volume)
                self.trainingVolume+=int(volume)

            

                print('[ML ANALYSIS] {} - PROCESSING BIDS'.format(time.asctime()))

                bids = self.get_bids(id, timestamp, category, volume, training_intent, blocking_entity, tmp_path)
                reset = False
                for bid in bids:
                    if not bids[bid]:
                        reset=True
                        break
                if reset:
                    data = []
                    empty_bids = 1
                    
                    with open('numberOfBidslog.json') as f:
                        data = json.load(f)   
                        data[id] = {timestamp:0}
                        if 'empty_bids' in data:
                                data['empty_bids'][timestamp] = empty_bids
                        else: 
                            data['empty_bids'] = {timestamp: empty_bids}

                    with open('numberOfBidslog.json', 'w') as f:
                        json.dump(data, f, indent=4, separators=(',',':'))          
                    print('[ML ANALYSIS] {} - EMPTY BIDS - SKIPPING {}'.format(time.asctime(), t)) 
                    
                    tars_processed+=1                     
                    continue
                bidsThisRound = 0
                for bid in bids: 
                    bidsThisRound+=len(bids[bid])
                print(bidsThisRound)
                all_rows['bids'].append(bids)
                print('[ML ANALYSIS] {:<20} - PROCESSING TRAINING TRACKERS'.format(time.asctime()))
                trackers_in_training = self.get_trackers(tmp_path, category, ml_type = "training")
                all_rows['training'].append(trackers_in_training)

                print('[ML ANALYSIS] {:<20} - PROCESSING TESTING TRACKERS'.format(time.asctime()))
                trackers_in_testing = self.get_trackers(tmp_path,category, ml_type="testing")
        
                all_rows['testing'].append(trackers_in_testing)
                tars_processed+=1
                self.totalTrainingRounds+=1
                self.totalTestingRounds+=1 
                data = []

                with open('numberOfBidslog.json') as f:
                    data = json.load(f)   
                    data[id] =  {timestamp:bidsThisRound}
                    print(timestamp, bidsThisRound)
                with open('numberOfBidslog.json', 'w') as f:
                    json.dump(data, f, indent=4, separators=(',',':'))   
                

                for g in self.global_vars:
                    if 'global_vars' in self.save_data:
                        self.save_data['global_vars'][g] = eval(g)
                    else:
                        self.save_data['global_vars'] = {g: eval(g)}
                self.save_data['all_rows'] = all_rows
                self.create_restore_point()
            # exit()
            # print(all_rows)
            except Exception as e: 
                print('Ecxception {}'.format(e))
        cols = [   
                    "alphabet_training_tracker",
                    "yandex_training_tracker",
                    "oracle_training_tracker",
                    "appnexus_training_tracker",
                    "verizon_training_tracker",
                    "baidu_training_tracker",
                    "twitter_training_tracker",
                    "facebook_training_tracker",
                    "double_verify_training_tracker",
                    "adobe_systems_training_tracker",
                    "criteo_training_tracker",
                    "microsoft_training_tracker",
                    "quantcast_training_tracker",
                    "pubmatic_training_tracker",
                    "automattic_training_tracker",
                    "sovrn_training_tracker",
                    "integral_ad_science_training_tracker",
                    "comscore_training_tracker",
                    "exoclick_training_tracker",
                    "alibaba_training_tracker",
                    "alphabet_testing_tracker",
                    "yandex_testing_tracker",
                    "oracle_testing_tracker",
                    "appnexus_testing_tracker",
                    "verizon_testing_tracker",
                    "baidu_testing_tracker",
                    "twitter_testing_tracker",
                    "facebook_testing_tracker",
                    "double_verify_testing_tracker",
                    "adobe_systems_testing_tracker",
                    "criteo_testing_tracker",
                    "microsoft_testing_tracker",
                    "quantcast_testing_tracker",
                    "pubmatic_testing_tracker",
                    "automattic_testing_tracker",
                    "sovrn_testing_tracker",
                    "integral_ad_science_testing_tracker",
                    "comscore_testing_tracker",
                    "exoclick_testing_tracker",
                    "alibaba_testing_tracker",
                    "cpm"]
            
        tracker_cols = ["alphabet",
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
        
        bid_cols = ['id','category', 'intent','volume','blocking_entity','bidder', 'mediaType', 'size']
        this_row = 0
        last_row = len(all_rows['bids'])-1
        bids = all_rows['bids']
        training = all_rows['training']
        testing = all_rows['testing']
        ids = []
        for i in bids: 
            ids.append(i.keys()[0])
        ids = sorted(ids)
        rows = []
        all_bidders = []
        all_mediaTypes = []
        all_sizes = []
        all_ids = []
        all_blockingEntities = []
        all_categories = []
        while this_row <  last_row:
            for id in bids[this_row]:
                for bid in bids[this_row][id]:
                    row = []
                    all_ids.append(str(id))
                    row.append(id)
                    for col in bid_cols:

                        if 'category' in col: 
                            row.append(bid[col])                            
                        if 'intent' in col: 
                            row.append(bid[col])
                        if 'volume' in col: 
                            row.append(bid[col])        
                        if 'blocking_entity' in col: 
                            row.append(bid[col])      
                            all_blockingEntities.append(bid[col])                                             
                        if 'bidder' in col: 
                            all_bidders.append(bid[col])
                            row.append(bid[col])
                        if 'mediaType' in col: 
                            if bid[col] != None: 
                                all_mediaTypes.append(bid[col])
                            else: 
                                all_mediaTypes.append('not_included_in_bid')
                            row.append(bid[col])
                        if 'size' in col:
                            if bid[col] != None: 
                                all_sizes.append(bid[col])
                            else: 
                                all_sizes.append('not_included_in_bid') 
                            all_sizes.append(bid[col])
                            row.append(bid[col])

                    for train_col in tracker_cols:
                        row.append(training[this_row][train_col])
                    for test_col in tracker_cols:
                        row.append(testing[this_row][test_col])
                    row.append(bid['cpm'])
                this_row+=1

                all_bidders = list(set(all_bidders))
                all_mediaTypes = list(set(all_mediaTypes))
                all_sizes = list(set(all_sizes))
                all_ids = list(set(all_ids))
                all_blockingEntities = list(set(all_blockingEntities))
        self.generate_arff(cols, rows, all_ids, all_bidders, all_mediaTypes, all_blockingEntities, all_sizes)
        # self.print_arff()
        avg_cpm = self.totalCpm / float(self.numberOfBidsPlaced)
        training_avg_vol = self.trainingVolume / self.totalTrainingRounds
        category_output = "-----------\n\n"
        category_output +="{:<19}".format('CAT\t')
        categories = sorted(self.categoryCount.keys())

        for c in categories: 
            category_output+="{:<9}".format(c[0:4])  
        category_output+='{}\t{:<14}'.format('\n', '')

        for c in categories: 
            category_output+="{:<9}".format('-----')
        
        category_output+='{:<20}'.format('\nVOL TRAINING\t')
        total_cpm_per_category = {}

        for c in categories: 
            category_output+="{:<9}".format(self.categoryCount[c]) 
            cpm_total = self.categoryCPM[c]
            total_cpm_per_category[c] = float(cpm_total) 

        category_output+='{:<23}'.format('\nTOT CPM CATEGORY')               

        for c in categories:
            category_output+="{:<9.4f}".format(total_cpm_per_category[c]) 
        totalTrackers= {'training':{}, 'testing':{}}
        totalTrackers_PCT= {'training':{}, 'testing':{}}
        for ml_type in self.tracker_count_per_category: 
            if ml_type == 'training':
                category_output+='{:<23}'.format('\n\n\n\t\t\t\t\t\t\t\tTOTAL TRACKERS DETECTED PER CATEGORY- TRAINING\n')
                category_output+='{:<23}'.format('\t\t\t\t\t\t\t\t----------------------------------------------\n')
                category_output+=self.get_cat_headers(categories)
            else: 
                category_output+='{:<23}'.format('\n\n\n\t\t\t\t\t\t\t\tTOTAL TRACKER DETECTED PER CATEGORY- TESTING\n')
                category_output+='{:<23}'.format('\t\t\t\t\t\t\t\t--------------------------------------------\n')
                category_output+=self.get_cat_headers(categories) 
            for tracker in sorted(self.tracker_count_per_category[ml_type]): 
                category_output+='\n{:<22}'.format(tracker)
                for c in categories:                
                    if c in self.tracker_count_per_category[ml_type][tracker]:
                        category_output+="{:<9}".format(self.tracker_count_per_category[ml_type][tracker][c])
                        if c in totalTrackers[ml_type]:
                            totalTrackers[ml_type][c]+=self.tracker_count_per_category[ml_type][tracker][c]

                        else:
                            totalTrackers[ml_type][c] =  self.tracker_count_per_category[ml_type][tracker][c]
                    else: 
                        category_output+="{:<9}".format(0)  
                
            category_output +="{:<23}".format('\n\nTOT')
        for c in categories: 
            if c in totalTrackers[ml_type]:
                category_output+="{:<9}".format(totalTrackers[ml_type][c])
            else:
                category_output+="{:<9}".format(0) 

        for ml_type in self.tracker_count_per_category: 
            if ml_type == 'training':
                category_output+='{:<23}'.format('\n\n\n\t\t\t\t\t\t\t\tTOTAL TRACKERS DETECTED PCT - TRAINING\n')
                category_output+='{:<23}'.format('\t\t\t\t\t\t\t\t----------------------------------------------\n')
                category_output+=self.get_cat_headers(categories)                

            else: 
                category_output+='{:<23}'.format('\n\n\n\t\t\t\t\t\t\t\tTOTAL TRACKER DETECTED PCT - TESTING\n')
                category_output+='{:<23}'.format('\t\t\t\t\t\t\t\t--------------------------------------------\n')
                category_output+=self.get_cat_headers(categories)                
  
            for tracker in sorted(self.tracker_count_per_category[ml_type]): 
                category_output+='\n{:<22}'.format(tracker)
                for c in categories:                
                    if c in self.tracker_count_per_category[ml_type][tracker]:
                        if c in totalTrackers[ml_type]:
                            if c in totalTrackers_PCT:
                                totalTrackers_PCT[ml_type][c]+=float(self.tracker_count_per_category[ml_type][tracker][c]) / float(totalTrackers[ml_type][c])
                            else:
                                totalTrackers_PCT[ml_type][c] =  float(self.tracker_count_per_category[ml_type][tracker][c]) / float(totalTrackers[ml_type][c])
                
                        else: 
                            totalTrackers_PCT[ml_type][c] = 0
                    else: 
                        totalTrackers_PCT[ml_type][c] = 0
                    category_output+="{:<9.3f}".format(totalTrackers_PCT[ml_type][c])

        category_output+='{:<23}'.format('\n\n\n\t\t\t\t\t\t\t\tBIDS PER CATEGORY\n')
        category_output+='{:<23}'.format('\t\t\t\t\t\t\t\t-----------------\n')
        category_output+=self.get_cat_headers(categories) 
        totalCpmPerBidder = {}
        for bidder in self.bidders_per_category:
            category_output+='\n\n{}'.format(bidder)
            category_output+='\n{}'.format('------------')
            category_output+='\n{:<22}'.format('# BIDS')
            for c in categories: 
                if c in self.bidders_per_category[bidder]:
                    category_output+="{:<9}".format(self.bidders_per_category[bidder][c]['count'])
                    if bidder in totalCpmPerBidder: 
                        if 'count' in totalCpmPerBidder:
                            totalCpmPerBidder[bidder]['count']+=self.bidders_per_category[bidder][c]['count']
                        else: 
                            totalCpmPerBidder[bidder]['count']=self.bidders_per_category[bidder][c]['count']
                    else:
                        totalCpmPerBidder[bidder] = {'count': self.bidders_per_category[bidder][c]['count']}
                else: 
                    category_output+="{:<9}".format(0)
            category_output+='\n{:<22}'.format('TOT CPM / CATEGORY')
            for c in categories:    
                if c in self.bidders_per_category[bidder]:
                    category_output+="{:<9.3f}".format(self.bidders_per_category[bidder][c]['cpm'])
                    if bidder in totalCpmPerBidder: 
                        if 'cpm' in totalCpmPerBidder:
                            totalCpmPerBidder[bidder]['cpm']+=self.bidders_per_category[bidder][c]['cpm']
                        else: 
                            totalCpmPerBidder[bidder]['cpm']=self.bidders_per_category[bidder][c]['cpm']
                    else:
                        totalCpmPerBidder[bidder].update({'cpm': self.bidders_per_category[bidder][c]['cpm']})
                else: 
                    category_output+="{:<9.3f}".format(0.00)
                    totalCpmPerBidder[bidder].update({'cpm': 0.01})
        
        
        category_output+='{:<23}'.format('\n\n\n\n\nBIDDER CPMs and # BIDS PLACED\n')
        category_output+='{:<23}'.format('----------------------------\n')
        for bidder in totalCpmPerBidder:
            category_output+='\n{}'.format(bidder)
            category_output+='\n{}'.format('------------')
            category_output+='\n{:<22}'.format('BIDS #')
            category_output+="{:<9}".format(totalCpmPerBidder[bidder]['count'])
            category_output+='\n{:<21}'.format('TOT CPM')
            category_output+="${:<9.3f}".format(totalCpmPerBidder[bidder]['cpm'])
            category_output+='\n{:<21}'.format('AVG CPM')
            category_output+="${:<9.3f}\n\n".format(float(totalCpmPerBidder[bidder]['cpm']) / float(totalCpmPerBidder[bidder]['count']))


            



           
              
        category_output+='\n'
        total_time = time.time() - self.start
        minutes = int(total_time / 60)
        seconds = int(total_time % 60)
        if seconds < 10: 
            seconds = '0'+str(seconds)
        msg =   '\n\n\nCOMPLETE\n' \
                '   +TAR FILES PROCESSES: {}\n' \
                '   +TOTAL BIDS: {}\n' \
                '   +AVG CPM PER BIDDER: $ {}\n' \
                '   +TRAINING SITE AVG VOL: {}\n' \
                '   +TOTAL TRAINING SITES: {}\n' \
                '   +TOTAL TEST SITES: {}\n' \
                '   +TOTAL CPM ALL BIDS: $ {}\n'\
                '   +TOTAL RUNTIME {}:{}\n' \
                '\nHB STATS\n{}\n'.format( tars_processed, self.numberOfBidsPlaced, avg_cpm, training_avg_vol, self.totalTrainingRounds,
                                           self.totalTestingRounds, self.totalCpm, minutes, seconds, category_output, DBG=0)

        result_run = '\n\n\nCOMPLETE\n' \
                                 '   +TAR FILES PROCESSES: {}\n' \
                                 '   +TOTAL BIDS: {}\n' \
                                 '   +AVG CPM PER BIDDER: $ {}\n' \
                                 '   +TRAINING SITE AVG VOL: {}\n' \
                                 '   +TOTAL TRAINING SITES: {}\n' \
                                 '   +TOTAL TEST SITES: {}\n' \
                                 '   +TOTAL CPM ALL BIDS: $ {}\n'\
                                 '   +TOTAL RUNTIME {}:{}\n' \
                                 '\nHB STATS\n{}\n'.format(tars_processed, self.numberOfBidsPlaced, avg_cpm, training_avg_vol, 
                                                            self.totalTrainingRounds, self.totalTestingRounds, self.totalCpm, minutes, seconds, 
                                                            category_output)  
        with open('ml_analysis_results.txt', 'a+') as f:
            msg = '************************************\n'
            f.write(msg)
            msg = "ML_ANALYSIS RESULTS\nTIME COMPLETE: {}\n".format(time.asctime())
            f.write(msg)
            msg = '************************************\n'
            f.write(msg)
            f.write(result_run)

    def generate_arff(self, cols, rows, ids, bidders, mediaTypes, blockingEntities, sizes):
        attributes = []
        data = []

        id_attr = ('id', ids)
        attributes.append(id_attr)

        category_attr = ('trainingCategory', self.categorys)
        attributes.append(category_attr)

        training_intent_attr = ('trainingIntent', ['INTENT', 'NO_INTENT'])
        attributes.append(training_intent_attr)

        trainingVolume_attr = ('trainingVolume', 'REAL')
        attributes.append(trainingVolume_attr)

        blocking_entity_attr = ('trainingBlocking', blockingEntities)
        attributes.append(blocking_entity_attr)

        bidders_attr = ('bidders', bidders)
        attributes.append(bidders_attr)
        
        mediaTypes_attr = ('mediaTypes', mediaTypes)
        attributes.append(mediaTypes_attr)
        
        sizes_attr = ('size', sizes)
        attributes.append(sizes_attr)

        for col in cols: 
            attr = (col, 'REAL')
            attributes.append(attr)
    
        for r in rows: 
            row = []
            for col in r:
                row.append(col)
            data.append(row)
        arff_obj = {"relation":"HB",
                    'description':"",
                    'attributes': attributes,
                    'data': data
                    }   
     
        with open('features.arff', 'wb') as f:
            arff.dump(arff_obj, f)      
            
    def print_arff(self):
        hb_data = []
        with open('features.arff', 'rb') as f: 
            hb_data = arff.loads(f)
            pprint(hb_data)

 
        

ml_analysis().get_features()