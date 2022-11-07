#!/usr/bin/env python3

import json
import requests
import sys
import time


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
    jtname = ""
    jturl = ""

    if 'startgns3' in a[1:] or 'stopgns3' in a[1:]: #It is a call to a GNS3 project
        toplevelkey = 'gns3'
        s = settingsobject[toplevelkey]
        url = s['prot']+s['serverip']+":"+s['serverport']+"/"+s['projecturi']+"/"
        if 'teststage' in a[2:]:
            url = url + s['teststageproject']
        elif 'prodstage' in a[2:]:
            url = url + s['prodstageproject']
        else:
            print('No Stage specified. Please add "teststage" or "prodstage"')
            sys.exit()

        if 'startgns3' in a[1:]:
            checkurl = url + '/' + s['nodescheck']
            urltuple = ( checkurl, httpheaders )
            print('Check if nodes in GNS3 are already running...')
            resp = request ( urltuple, 'get' ) #Check status of all nodes in the project
            if type(resp) == str: resp = json.loads(resp) #From str to json
            stopped = False
            for item in resp:
                status = item['status'].lower()
                if status == 'stopped': #Stopped node, need to start all nodes with API request
                    stopped = True
                    print('There is a stopped node. Will start all nodes now in GNS3')
                    url = url +  "/" + s['nodescheck'] + '/' + s['nodesstarturi']
                    break

            if stopped == False: url = "proceed = True"

        if 'stopgns3' in a[1:]: url = url + "/" + s['nodescheck'] + '/' + s['nodesstopuri']

    elif 'launchawx' in a[1:]: #It is a call to Ansible Tower
        toplevelkey = 'awx'
        s = settingsobject[toplevelkey]
        if 'httpheaders' in s: httpheaders = s['httpheaders']

        if 'relaunch' in a[2:]:
            relaunchsuffix = str(a[3])
            url = s['prot']+s['serverip']+':'+s['serverport'] + relaunchsuffix

        else:
            url = s['prot']+s['serverip']+':'+s['serverport']+'/'+s['projecturi']
            urltuple = ( url, httpheaders )
            resp = request ( urltuple, 'get' )
            if type(resp) == str: resp = json.loads(resp) #From str to json
        
            if 'teststage' in a[2:]:
                if 'deploy' in a[3:]:
                    jtname = s['teststage_jobtemplate_name_deploy']
                elif 'test' in a[3:]:
                    jtname = s['teststage_jobtemplate_name_test']
                else:
                    print('No stagefase specified. Please add "deploy" or "test"')
                    sys.exit()

            elif 'prodstage' in a[2:]:
                if 'deploy' in a[3:]:
                    jtname = s['prodstage_jobtemplate_name_deploy']
                elif 'test' in a[3:]:
                    jtname = s['prodstage_jobtemplate_name_test']
                else:
                    print('No stagefase specified. Please add "deploy" or "test"')
                    sys.exit()
      
            else:
                print('No Stage specified. Please add "teststage" or "prodstage"')
                sys.exit()

            templates = resp['count']
        
            for jt in resp['results']: #search through available jobtemplates and find the one we need
                #print(jtname)
                #print(jt['name'])
                if jtname == jt['name']: #found match
                    print('Found requested Job Template')
                    jturl = jt['url'] #This uri addon is needed to launch the template
                    jtid = jt['id'] #Job template id
                    print('Job Template ID : ' + str(jtid))
            
            if jturl == "":
                print('No matching Job template found on Ansible Tower for "' + jtname + '".')
                print('Check spelling or the available Job templates on Tower.')
                sys.exit()
        
            url = s['prot']+s['serverip']+':'+s['serverport'] + jturl + s['launchsuffix']+"/"

    else: #No cli arguments given
        print('\nusage : ' + sys.argv[0] + ' <option>\n')
        print(' - startgns3 : will start GNS3 project')
        print(' - stopgns3  : will stop GNS3 project')
        print(' - launchawx teststage: will start job template for test env on Ansible tower')
        print(' - launchawx prodstage: will start job template for prod env on Ansible tower')
        print('=========================================================')
        sys.exit()

    if 'relaunch' in url: 
        return url, httpheaders, { "runtype" : toplevelkey }, { "hosts" : "failed" }
    else:
        return url, httpheaders, { "runtype" : toplevelkey }, {}



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
    try:
        if url[3] != '{}': #there is json data added to url
            jsondata = url[3]
    except:
        pass

    if reqtype == 'post':
        #print(url)
        #print(url[0])
        #print(url[1])
        r = requests.post ( url[0], headers=url[1], json=jsondata )
    elif reqtype == 'get': r = requests.get ( url[0], headers=url[1], json=jsondata )
    obj = r.content.decode('utf-8') #from bytes to dict
    #print(obj)
    
    return obj


def jobstatuschecker ( dataobject ):

    """
    inputs
    - dataobject : json or string object, i.e. returned from API call

    return
    - proceed : string (True, False or Retry)

    This function checks the status of an Ansible Tower Job.
    The dataobject is the return object of an previous started API call to start
    a Job Template. The job template starts a job and with the job id
    the jobstatuschecker will poll the status till finished.
    
    """

    status   = ''
    failed   = ''
    finished = ''
    proceed  = "False" #This can be used by Jenkins to determine if Chain is continuoud
    st       = 10 #Delay between check requests
    
    if type(dataobject) == str: dataobject = json.loads(dataobject) #From str to json
    #print(dataobject) 
    urisuffix = dataobject['url'] #Catch the job url that was created
    relaunchsuffix = dataobject['related']['relaunch']
    #print(relaunchsuffix)
    s = settings['awx']
    url = s['prot']+s['serverip']+":"+s['serverport']+urisuffix #create uri for API call to awx to check job status
    myurltuple = ( url, urltuple[1] ) #Create urltuple with url and headers
   
    # start Loop, get every 10 seconds jobstatus
    #
    # - jobstatus   (can be pending, running, successful, failed)
    # - jobfailed   (can be false, true)
    # - jobfinished (can be null or time, i.e 2022-10-24T14:38:50.009531Z)

    print('\n Starting jobchecker. Waiting till AWX template finishes its job...')

    while True:
    
        response = request ( myurltuple, "get" ) #Request API call
        if type(response) == str: response = json.loads(response) #From str to json
   
        #Get status of three keys available in the job dict
        result = { 
                   "jobstatus"   : response['status'],
                   "jobfailed"   : response['failed'],
                   "jobfinished" : response['finished']
                 }

        status   = result['jobstatus'].lower()
        failed   = result['jobfailed']
        finished = result['jobfinished']
    
        if status == 'successful':
            if failed == 'false' or failed == False:
                print('\n Succesful job finish at ' + finished)
                proceed = "True"
                break
            else:
                print('\n Job finished succesful but with failed result.')
                break
            cont
        elif status == 'failed':
            if finished != None and finished != 'null':
                print('\n Job finished with "failed" status. Check job logs on AWX.')
                print(' Will notify to run job again on failed hosts.')
                proceed = relaunchsuffix
                break
            else:
                print('\n Job finished with "failed" status due to finish errors. Will not proceed.')

        print('  Job status : ' + status + '. Wait ' + str(st) + ' secs till next check..')
        time.sleep(st)

    print()

    return proceed #returns the status of the job that was started

    


########################
##### MAIN PROGRAM #####
########################

settings = readsettings ( settingsfile ) #Read settings to JSON object

# Request API call
urltuple = return_url ( settings ) #Return required URL, headers if needed & other option data
print(urltuple)

if urltuple[0] == 'proceed = True': #GNS3 is already running, Report back to proceed & exit
    print(urltuple[0])
    sys.exit()

response = request ( urltuple, "post") #Request API POST request
#print(response)

if 'gns' in urltuple[2]['runtype'] and 'start' in urltuple[0]:
    print('proceed = Wait')


#If AWX project was launched, check its jobstatus till finished
if 'awx' in urltuple[2]['runtype']:
    checkresult = jobstatuschecker ( response )
    print('proceed =', checkresult)


