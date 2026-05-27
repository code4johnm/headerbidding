

from __future__ import absolute_import
import sys
import os
from pathlib import Path

# Add project root to path so we can import openwpm (and local modules)
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parents[4]  # HB-update root from .../AB_Testing/testing/training/
sys.path.insert(0, str(project_root))
sys.path.append('../../')  # original for local HBLogger etc (relative to cwd when run)

from openwpm.command_sequence import CommandSequence
from openwpm.task_manager import TaskManager
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider

import time
import json
import copy
import random
from HBLogger import HBLogger
import argparse
# six.moves.range not needed on Py3; use range directly




# The list of sites that we wish to crawl
NUM_BROWSERS = 1
sites = [] 
# pbjs_sites = {"1":'http://www.zimbio.com/'}
pbjs = ScriptUtils()
parser = argparse.ArgumentParser()
parser.add_argument('--timestamp', help='timestamp in seconds since epoch')
parser.add_argument('--crawl_type', help='intent or no intent training profile')
parser.add_argument('--site' , help='pbjs site')
parser.add_argument('--category', help="The alexa category of the training crawl")


args = parser.parse_args()

timestamp = args.timestamp
crawl_type = args.crawl_type
category = args.category
pbjs_site  = args.site


recovery_run = False
data = []
with open('restore.json') as f: 
    data = json.load(f)
for i in data: 
    if timestamp == data[i]['timestamp']: 
        crashed = data[i]['crashed']
        completed = data[i]['timestamp']
        if crashed and not completed: 
            recovery_run = True
hblogger = HBLogger("[TESTING]")
msg = "Starting Session: intent {} timestamp {}, category {} pbjs_site {}".format( 
                                                                                               crawl_type,
                                                                                               timestamp, 
                                                                                               category,
                                                                                               pbjs_site)

hblogger.info(msg)   

"""load each of the categories into iab_sites
"""


done = {
    "Adult":0,
    "Arts":0,
    "BLOCK":0,
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
    "Sports":0
}   

with open('testingDone.json', 'w') as f:  
    json.dump(done, f, indent=4, separators=(',',':'), sort_keys=True)
iab_files = []
iab_files = os.listdir('sites/')
iab_files.append("BLOCK")
pbjs_sites = {}
iab_params = {}
managers = {}
command_sequences = {}
local_done = {}

def wait_until_done(site, visit, category, rank): 
    all_done = False
    totalSleep = 0
    iabs = []
    
    #Wait until all browsers have finished
    while not all_done:  
        try:
            with open('testingDone.json') as f: 
                iabs = json.load(f)
        except:
            with open('testingDone.json') as f: 
                iabs = json.load(f)
        tmp = True
        for iab in iabs: 
            if iab in local_done: 
                local_done[iab] = iabs[iab]
                msg = 'local_done {}'.format( local_done)
                
                hblogger.info(msg)
        for category in local_done: 
            site = pbjs_sites[rank]
            tmp = tmp and bool(local_done[category]) 
            data = []   
            with open('testingComplete.json') as f: 
                data = json.load(f)
                if bool(local_done[category]): 
                    key = rank+'_'+site
                    if key in data:
                        if category not in data[key]:
                            data[key].append(category) 

                    else: 
                        data[key] = [category]
            with open('testingComplete.json', 'w') as f: 
                if data != []:      
                    json.dump(data, f, sort_keys=True, indent=4, separators =(',',':'))
        all_done = tmp 
        if not all_done:
            time.sleep(5)
            totalSleep +=5
            no_bids = []            
            if totalSleep >= 70: 
                msg = 'WAIT_UNTIL_DONE - reached timeout waiting for site to load'
                
                hblogger.log(msg,level="ERROR")

                with open('no_bid_sites.json') as f: 
                    no_bids = json.load(f)
                if site in no_bids: 
                    no_bids[site]['count'] +=1
                    no_bids[site]['crawl_info'].append({'site':site, 'visit':visit})
                else: 
                    no_bids[site] = {'crawl_info': [{'site':site, 'visit':visit}]}
                    no_bids[site] = {'count': 1}
                with open('no_bid_sites.json', 'w') as f: 
                    json.dump(no_bids, f, separators=(',', ':'), indent=4)
                    break
    msg = 'Rank: {} Total Time: {}'.format(rank, time.time() - start)
    
    hblogger.info(msg)

    with open('testingDone.json', 'w') as f: 
        json.dump(done, f, indent=4, separators=(',',':'), sort_keys=True)
        

with open('pbjs_sites.json') as f: 
    pbjs_sites = json.load(f)

    if pbjs_site !=None: 
        pbjs_sites = {pbjs_site:pbjs_sites[pbjs_site]}
print(pbjs_sites)
for iab in iab_files: 
    if iab =='intent.json':
        continue    
    iabString = iab.split('.')[0]
    if category != None: 
        if iabString != category: 
            continue    
    command_sequences.update({iabString:''})
    managers.update({iabString:''})
    iab_params.update({iabString:{}})

with open('./config/testing/allow_manager_params.json') as f: 
    prefs = json.load(f)
    allow_manager_params = copy.deepcopy(prefs)
with open('./config/testing/allow_browser_params.json') as f: 
    prefs = json.load(f)
    allow_browser_params = [copy.deepcopy(prefs) for i in range(
        0, NUM_BROWSERS)]

with open('./config/testing/block_manager_params.json') as f: 
    prefs = json.load(f)
    block_manager_params = copy.deepcopy(prefs)
with open('./config/testing/block_browser_params.json') as f: 
    prefs = json.load(f)
    block_browser_params = [copy.deepcopy(prefs) for i in range(
        0, NUM_BROWSERS)]


block_params = {}


# Instantiates the measurement platform
# Commands time out by default after 60 seconds

intent = crawl_type
completed = []
skip = -1
# if pbjs_site == None: 
#     with open('testingComplete.json') as f: 
#         completed = json.load(f)
#     for key in completed:
#         rank = int(key.split('_')[0])
#         if skip < rank: 
#             skip = rank
#             msg = "Skipping {} sites already visited".format( key)
#             
#             hblogger.info(msg)
# Visits the sites with all browsers simultaneously
load_path = './profiles/testing/load'
profile_folder = os.listdir('./profiles/testing/load/')[0]
profile_path = os.path.join(load_path, profile_folder)
for iab in iab_params: 
    try:
        if iab != "BLOCK":
            iab_params[iab].update({"manager_params":copy.deepcopy(allow_manager_params)})
            iab_params[iab].update({"browser_params":copy.deepcopy(allow_browser_params)})
            data_dir = "./results/owpm/testing/{}/{}/".format(timestamp, iab)
            iab_params[iab]['manager_params']['data_directory'] = data_dir
            iab_params[iab]['manager_params']['log_path'] = data_dir + "openwpm-testing-{}.log".format(iab)
            iab_params[iab]['browser_params'][0]['seed_tar'] = "{}".format(profile_path)
            iab_params[iab]['browser_params'][0]['profile_archive_dir'] = "./profiles/testing/{}/{}/".format(timestamp,iab)
        else: 
            iab_params[iab].update({"manager_params":copy.deepcopy(block_manager_params)})
            iab_params[iab].update({"browser_params":copy.deepcopy(block_browser_params)})
            data_dir = "./results/owpm/testing/{}/{}/".format(timestamp, iab)
            iab_params[iab]['manager_params']['data_directory'] = data_dir
            iab_params[iab]['manager_params']['log_path'] = data_dir + "openwpm-testing-{}.log".format(iab)
            iab_params[iab]['browser_params'][0]['profile_archive_dir'] = "./profiles/testing/{}/{}/".format(timestamp,iab)
    except Exception as e:
        msg = "Exception - Config - {}".format( e)
        
        hblogger.log(msg, level="ERROR")
        raise Exception
 
def _to_taskmanager(man_d, br_d_list, db_basename):
    """Convert legacy dict config to new OpenWPM objects + storage provider."""
    man_d = dict(man_d)  # copy
    br_list = [dict(b) for b in br_d_list]
    # legacy key mappings
    if 'log_directory' in man_d:
        man_d.setdefault('log_path', man_d.pop('log_directory'))
    if 'database_name' in man_d:
        man_d.pop('database_name', None)
    for b in br_list:
        if 'profile_tar' in b:
            b['seed_tar'] = b.pop('profile_tar')
        if 'headless' in b and 'display_mode' not in b:
            b['display_mode'] = 'headless' if b.pop('headless') else 'native'
    m_params = ManagerParams.from_dict(man_d)
    b_params = [BrowserParams.from_dict(b) for b in br_list]
    # ensure dirs
    if not m_params.data_directory or str(m_params.data_directory) == "":
        m_params.data_directory = Path("./datadir")
    logp = m_params.log_path
    if not logp or str(logp) == "":
        logp = Path(m_params.data_directory) / db_basename.replace('.sqlite','.log')
        m_params.log_path = logp
    db_path = Path(m_params.data_directory) / db_basename
    provider = SQLiteStorageProvider(str(db_path))
    return m_params, b_params, provider

for iab in managers: 
    try:
        msg = "loading category {} into manager".format( iab)
        
        hblogger.info(msg)
        manager_d = iab_params[iab]['manager_params']
        browser_ds = iab_params[iab]['browser_params']
        db_name = "crawl-data-testing-{}.sqlite".format(iab)
        m_p, b_ps, prov = _to_taskmanager(manager_d, browser_ds, db_name)
        managers[iab] = TaskManager(m_p, b_ps, prov, None)
    except Exception as e:
        msg = "Exception - manager params - {}".format( e)
        
        hblogger.log(msg, level="ERROR")
        pass

for rank in pbjs_sites:
    try:
        if rank < skip: 
            msg = "skipping site allready visited {}".format( pbjs_sites[rank])
            
            hblogger.info(msg)
            continue
        startRound = time.time()
        msg = "ROUND STARTED {}".format( startRound)
        
        hblogger.info(msg)
        #Initialize manager     
        manager_count = 0            
        data = []
        for visit in [1]:
            start = time.time()
            msg = "VISIT STARTED {}".format( start)
            
            hblogger.info(msg)

            for iab in managers:
                local_done[iab] = 0

                site = pbjs_sites[rank]
                msg = "[TESTING] {}, VISITING SITE: {} RANK: {}, IAB: {}".format(site, rank, iab)
                
                hblogger.info(msg)
 
                # with open('write_out_har.json', 'w') as f: 
                #     json.dump({'writing':True}, f)
                #     time.sleep(1)
                command_sequences[iab] = CommandSequence(site)
                command_sequences[iab].get(sleep=5, timeout=90)
                # NOTE: run_custom_function removed in modern OpenWPM; implement via custom BaseCommand
                # command_sequences[iab].append_command( CustomGetCpmCommand(...) )
                # For now the bid collection logic in pbjs.getCpm is not auto-executed.
                # command_sequences[iab].dump_profile_cookies(60)  # removed; use cookie_instrument + profile dump if needed
                time.sleep(5)
               
                # index='**' synchronizes visits between the three browsers
                managers[iab].execute_command_sequence(command_sequences[iab])
                msg = 'managers completed {}'.format( manager_count)
                
                hblogger.info(msg)
                manager_count+=1
                if (manager_count % 6) == 0 or manager_count == len(managers): 
                    msg = 'waiting for {} managers'.format( manager_count)
                    
                    hblogger.info(msg)
                    wait_until_done(site,visit, iab, rank)
                    msg = 'done waiting for managers: {}'.format( manager_count)
                    
                    hblogger.info(msg)
                    local_done = {}

            with open('testingDone.json') as f: 
                iabs = json.load(f) 
                msg = "Done: {}".format( iabs)  
                
                hblogger.info(msg)
                 
       
            with open('testingDone.json', 'w') as f: 
                json.dump(done, f, indent=4, separators=(',',':'), sort_keys=True)
            msg = "VISIT TOTAL TIME: {}".format(time.time() - start)
            
            hblogger.info(msg)
            # sys.exit()
    except Exception as e:
        msg = "Exception {} occurred, cleaning up and going on to next site".format( e)
        
        hblogger.log(msg, level="ERROR")
        with open('testingDone.json') as f: 
            iabs = json.load(f)    
    
        with open('testingDone.json', 'w') as f: 
            json.dump(done, f, indent=4, separators=(',',':'), sort_keys=True)
        pass
for iab in managers: 
    # os.system('pkill -f java')
    if managers[iab] != "":
        managers[iab].close()
        managers[iab] = ""
