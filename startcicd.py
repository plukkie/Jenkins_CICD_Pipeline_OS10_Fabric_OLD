#!/usr/bin/env python3

import json
import requests
import sys


settingsfile    = 'settings.json'


## Functions

def return_url ( settingsobject ):
    
    """
    input:
    - settingsobject : JSOn object

    returns constructed url & httheaders if required

    This function reads cli arguments and reads corresponding settings from json file.
    It constructs the url for the API call & the required http headers.
    """
    a = sys.argv
    url = ""
    httpheaders = {}

    if 'startgns3' in a[1:] or 'stopgns3' in a[1:]: #It is a call to a GNS3 project
        toplevelkey = 'gns3'
        s = settingsobject[toplevelkey]
        url = s['prot']+s['serverip']+":"+s['serverport']+"/"+s['projecturi']+"/"+s['project']
        if 'startgns3' in a[1:]: url = url+"/"+s['nodesstarturi']
        if 'stopgns3' in a[1:]: url = url+"/"+s['nodesstopuri']
    elif 'launchawx' in a[1:]: #It is a call to Ansible Tower
        toplevelkey = 'awx'
        s = settingsobject[toplevelkey]
        url = s['prot']+s['serverip']+":"+s['serverport']+"/"+s['projecturi']+"/"+s['jobtemplateid']+"/"+s['launchsuffix']+"/"
    
    else: #No cli arguments given
        print('\nusage : ' + sys.argv[0] + ' <option>\n')
        print(' - startgns3 : will start GNS3 project')
        print(' - stopgns3  : will stop GNS3 project')
        print(' - launchawx : will start job template on Ansible tower')
        print('=========================================================')
        sys.exit()

    if 'httpheaders' in s: httpheaders = s['httpheaders']

    return url, httpheaders, { "runtype" : toplevelkey }


def readsettings ( jsonfile ):

    """
    input
    - jsonfile : json file with all settings

    return
    - json object with all settings
    """

    try:
        f       = open(jsonfile)
        data    = json.load(f)

    except:
        result  = { "tryerror" : "Error reading settings file " + jsonfile }

    else:
        result = data
    
    f.close()
    return result


def request ( url, reqtype, jsondata={} ):
    
    """
    input
    - url : array object with url and headers
    
    return
    - http request result

    This function requests an api call to the url endpoint.
    """
    
    if reqtype == 'post': r = requests.post (url[0], headers=url[1], data=jsondata )
    obj = json.loads(r.content.decode('utf-8')) #from bytes to dict

    return obj


def finishchecker ( jsonobject):
    print(jsonobject)


########################
##### MAIN PROGRAM #####
########################

settings = readsettings ( settingsfile ) #Read settings to JSON object

# Request API call
urltuple = return_url ( settings ) #Return required URL and headers if needed
response = request ( urltuple, "post") #Request API POST request


if 'awx' in urltuple[2]['runtype']: finishchecker( response['url'] )


#print(response)
#print(urltuple)
