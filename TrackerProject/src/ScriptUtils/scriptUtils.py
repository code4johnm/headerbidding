from __future__ import annotations

import json
import logging
import os
import random
import sys
import time
from pathlib import Path
# from browsermobproxy import Server

_SRC = str(Path(__file__).resolve().parents[1])
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
import coord


def load_json_object(path, default):
    """Read a JSON object. A missing or unreadable file returns default."""
    try:
        with open(path, encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, ValueError):
        return default
    if not isinstance(value, type(default)):
        return default
    return value


def dump_json_object(path, value):
    """Write JSON with a real indent. json.dump rejects indent=True."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=4, separators=(",", ":"))
        handle.write("\n")
    os.replace(temporary, path)


class ScriptUtils: 
    def __init__(self): 
        self.allowVisit = 1

        self.available  = True
        self.GET_CPM =  "var output = [];" \
                        "function getCPM()" \
                        "{    " \
                        "    var responses = pbjs.getBidResponses();" \
                        "    var winners = pbjs.getAllWinningBids();" \
                        "    Object.keys(responses).forEach(function(adUnitCode) {" \
                        "    var response = responses[adUnitCode];" \
                        "        response.bids.forEach(function(bid) " \
                        "        {" \
                        "            output.push({" \
                        "            bid: bid," \
                        "            adunit: adUnitCode," \
                        "            adId: bid.adId," \
                        "            bidder: bid.bidder," \
                        "            time: bid.timeToRespond," \
                        "            cpm: bid.cpm," \
                        "            msg: bid.statusMessage," \
                        "            rendered: !!winners.find(function(winner) {" \
                        "                return winner.adId==bid.adId;" \
                        "            })" \
                        "            });" \
                        "        });" \
                        "    });" \
                        "}" \
                        "getCPM();" \
                        "return output;"

        self.PBJS_VERSION = "var version = '';" \
                            "function pbjsVersion() " \
                            "{" \
                            "    try" \
                            "    {" \
                            "        version = pbjs.version;" \
                            "        " \
                            "    }" \
                            "    catch(err)" \
                            "    {" \
                            "        " \
                            "    }" \
                            "}" \
                            "pbjsVersion();" \
                            "return version;"

    def getCpm(self, iab, visit, site, crawl_type, **kwargs):
        driver = kwargs['driver']
        domain = driver.current_url
        print(domain)
        parts = domain.split('//')
        if len(parts) > 1:
            domain = parts[0] + '//' + parts[1].split('/')[0]
        print('[SCRIPT UTILS] getCpm() domain: {} iab: {}'.format(domain, iab))
        output = []
        try:
            output = driver.execute_script(self.GET_CPM)
        except Exception as exc:
            output = ["error: {}".format(exc)]
        if not isinstance(output, list):
            output = ["error: script did not return a list"]
        if output == []:
            msg = '[SCRIPT UTILS] No pbjs bids returned'
            print(msg)
            output.append(msg)
            def _record_no_bid(no_bids):
                entry = no_bids.get(site) if isinstance(no_bids.get(site), dict) else {}
                info = entry.get('crawl_info') if isinstance(entry.get('crawl_info'), list) else []
                info.append({'site': site, 'visit': visit})
                no_bids[site] = {'count': int(entry.get('count') or 0) + 1, 'crawl_info': info}

            coord.update_json('no_bid_sites.json', {}, _record_no_bid)
        site_name = coord.site_slug(site)
        if crawl_type == "NO_INTENT":
            destination = os.path.join('./results/bids_no_intent/', site_name + "_{}.json".format(iab))
        else:
            destination = os.path.join('./results/bids_intent/', site_name + "_{}.json".format(iab))

        def _append_bids(data):
            for item in output:
                slot = data.setdefault(iab, {}).setdefault(domain, {})
                slot.setdefault(visit, []).append(item)

        print('[SCRIPT UTILS] {} writing to {}'.format(iab, destination))
        coord.update_json(destination, {}, _append_bids)

        def _mark_done(done):
            done[iab] = 1

        coord.update_json('testingDone.json', {}, _mark_done)
        print('[SCRIPT UTILS] {} finished. '.format(iab))
        return destination



    
    def pbjsVersion(self, **kwargs): 
        driver = kwargs['driver']
        version = driver.execute_script(self.PBJS_VERSION)
        domain = driver.current_url

        def _store_version(data):
            data[domain] = version

        coord.update_json('./results/pbjs_sites_full.json', {}, _store_version)
       
        try:
            with open('pbjsDone.txt', 'w') as f: 
                f.write('1')
        except:
            pass

    def signalDone(self, iab, **kwargs):
        def _mark(data):
            data[iab] = 1

        data = coord.update_json('trainingDone.json', {}, _mark)
        print(data)


    # def write_out_har(self, url, timestamp, category, intent, ml_type, **kwargs):
    #     try:
    #         url = url.split('://')[1]       
            
    #         old_path = '/mnt/hgfs/archive_save/hars/HAR_{}.json'.format(url)
    #         new_path = ""
    #         intent_url_found= ""

    #         if ml_type == 'ml_training':
    #             new_path = '/mnt/hgfs/archive_save/ml_training/{}_{}/hars/'.format(timestamp, intent)
        
    #             if intent == "INTENT":
    #                 intent_check = ["www.hotels.com/", "www.zales.com/", "www.jamesedition.com/", "www.luxuryrealestate.com/"]
    #                 for intent_url in intent_check:
    #                     if intent_url in url: 
    #                         intent_url_found = intent_url.split('/')[0]
    #                 if intent_url_found != "":    
    #                     os.system('mv /mnt/hgfs/archive_save/hars/*_INTENT_URL.json {}'.format(new_path))                        
        
    #         if ml_type == 'ml_testing':
    #             new_path = '/mnt/hgfs/archive_save/ml_testing/ready_for_analysis/{}_{}/testing/hars/'.format(timestamp, intent)

    #             os.system('mv {} {}'.format(old_path, new_path))

    #         print("[SCRIPT UTILS] {} moving {} to {}".format(time.asctime(), old_path, new_path))

    #     except:
    #         print("[SCRIPT UTILS] {} moving {} to {} HAR file".format(time.asctime(), old_path, new_path))

        