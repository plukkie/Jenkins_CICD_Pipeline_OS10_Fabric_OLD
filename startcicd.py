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
    - settingsobject : JSON object

    returns constructed url & httheaders if required

    This function reads cli arguments and reads corresponding settings from json file.
    It constructs the url for the API call & the required http headers.
    With the urls, the receiver starts and stops gns3 projects and ansible tower templates.
    This script is started by the Jenkins pipeline.
    """
    a = sys.argv
    url = ""
    httpheaders = {}
    jtname = ""
    jturl = ""
    jsonobj = {}

    if 'startgns3' in a[1:] or 'stopgns3' in a[1:]: #It is a call to a GNS3 project
        toplevelkey = 'gns3'
        s = settingsobject[toplevelkey] #get gns3 keys from settings
        url = s['prot']+s['serverip']+":"+s['serverport']+"/"+s['projecturi']+"/"
        if 'devstage' in a[2:]: #dev/test stage is specified
            url = url + s['teststageproject']
        elif 'prodstage' in a[2:]: #prod stage is specified
            url = url + s['prodstageproject']
        else:
            print('No Stage specified. Please add "devstage" or "prodstage"')
            sys.exit()

        if 'startgns3' in a[1:]:
            checkurl = url + '/' + s['nodescheck'] #construct gns3 api to check node status
            urltuple = ( checkurl, httpheaders )
            print('Check if nodes in GNS3 are already running...')
            resp = request ( urltuple, 'get' ) #Check status of all nodes in the project
            print(resp)
            if type(resp) == str: resp = json.loads(resp) #From str to json
            stopped = False #used to track if a gns3 node is stopped
            for item in resp: #find all nodes and their status
                status = item['status'].lower()
                if status == 'stopped': #Stopped node, need to start all nodes with API request
                    stopped = True
                    print('There is a stopped node. Will start all nodes now in GNS3')
                    url = url +  "/" + s['nodescheck'] + '/' + s['nodesstarturi']
                    break #exit loop

            if stopped == False: url = "proceed = True" #All nodes already started, jenkins can proceed
  
        #stop all gns3 nodes
        if 'stopgns3' in a[1:]: url = url + "/" + s['nodescheck'] + '/' + s['nodesstopuri']

    elif 'launchawx' in a[1:]: #It is a call to Ansible Tower
        toplevelkey = 'awx'
        s = settingsobject[toplevelkey] #get tower details from settings
        if 'httpheaders' in s: httpheaders = s['httpheaders']

        if 'relaunch' in a[2:]: #their were failed playbook runs and a relaunch was requested
            relaunchsuffix = str(a[3]) #the job relaunch uri of the failed job
            url = s['prot']+s['serverip']+':'+s['serverport'] + relaunchsuffix

        else: #tower find template matched to setting file
            url = s['prot']+s['serverip']+':'+s['serverport']+'/'+s['projecturi']
            urltuple = ( url, httpheaders )
            resp = request ( urltuple, 'get' ) #get all job templates from tower
            if type(resp) == str: resp = json.loads(resp) #From str to json
        
            if 'devstage' in a[2:]: #dev/test stage specified
                if 'configure' in a[3:]:
                    jtname = s['teststage_jobtemplate_name_deploy']
                elif 'test' in a[3:]:
                    jtname = s['teststage_jobtemplate_name_test']
                else:
                    print('No stagefase specified. Please add "configure" or "test"')
                    sys.exit()

            elif 'prodstage' in a[2:]: #prod stage specified
                if 'configure' in a[3:]:
                    jtname = s['prodstage_jobtemplate_name_deploy']
                elif 'test' in a[3:]:
                    jtname = s['prodstage_jobtemplate_name_test']
                else:
                    print('No stagefase specified. Please add "configure" or "test"')
                    sys.exit()
      
            else:
                print('No Stage specified. Please add "devstage" or "prodstage"')
                sys.exit()

            templates = resp['count'] #number of job templates found
        
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
        
            #this is the api url to start the job template
            url = s['prot']+s['serverip']+':'+s['serverport'] + jturl + s['launchsuffix']+"/"
    
    elif 'creategns3project' in a[1:]:
        toplevelkey = 'gns3'
        s = settingsobject[toplevelkey] #get gns3 keys from settings
        url = s['prot']+s['serverip']+":"+s['serverport']+"/"+s['projecturi']
        jsonobj = s['newprojectjson'] 
 

    else: #No cli arguments given
        print('\nusage : ' + sys.argv[0] + ' <option>\n')
        print(' - startgns3 devstage/prodstage : will start GNS3 project')
        print(' - stopgns3 devstage/prodstage : will stop GNS3 project')
        print(' - launchawx devstage: will start job template for test env on Ansible tower')
        print(' - launchawx prodstage: will start job template for prod env on Ansible tower')
        print('=========================================================')
        sys.exit()

    if 'relaunch' in url: #a job relaunch is requested, add failed hosts only
        return url, httpheaders, { "runtype" : toplevelkey }, { "hosts" : "failed" }
    else: #normal job template url
        return url, httpheaders, { "runtype" : toplevelkey }, jsonobj



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
    elif reqtype == 'get':
        r = requests.get ( url[0], headers=url[1], json=jsondata )
    elif reqtype == 'put':
        #print(url[0])
        #print(url[1])
        #print(jsondata)
        r = requests.put ( url[0], headers=url[1], json=jsondata )
    
    obj = r.content.decode('utf-8') #from bytes to dict
    #print(obj)
    
    return obj


def jobstatuschecker ( dataobject ):

    """
    inputs
    - dataobject : json or string object, i.e. returned from API call

    return
    - proceed : string (True, False or relaunch url)

    This function checks the status of an Ansible Tower Job.
    The dataobject is the return object of an previous started API call to start
    a Job Template. The job template starts a job and with the job id
    the jobstatuschecker will poll the status till finished.
    
    """

    status   = ''
    failed   = ''
    finished = ''
    proceed  = "False" #This can be used by Jenkins to determine if pipeline should continue
    st       = 10 #Delay between check requests
    
    if type(dataobject) == str: dataobject = json.loads(dataobject) #From str to json
    #print(dataobject) 
    urisuffix = dataobject['url'] #Catch the job url that was created
    relaunchsuffix = dataobject['related']['relaunch'] #needed if relaunch is needed
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

    while True: #check job status. when finished return status, used by jenkins
    
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
            if finished != None and finished != 'null': #return relaunch task to jenkins
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


def provisiongns3project (jsonobject):

    """
    Build complete GNS3 project.
    """
    try:
        projectid = jsonobject['project_id']
    except:
        projectid = "7eb56e95-0b70-48c8-90bc-fa920e44f599"

    templateid = ""
    httpheaders = {} 
    s = settings['gns3']
    nd = s['nodesdata']
    baseurl = s['prot']+s['serverip']+':'+s['serverport']
    projecturi = s['projecturi']
    templatesuri = s['templatesuri']
    templatedict = nd['templates'] #Data for the Network fabric roles
    url = baseurl + '/' + templatesuri
    urltuple = ( url, httpheaders )
    templates = request ( urltuple, "get" )
    jsondict = json.loads(templates) #All templates found in GNS3 server
    newdict = { "nodes" : {} }
    jsonadd = {}

    for template in templatedict: #Loop through desired templates from settingsfile
        reqname = templatedict[template]['name']
        count   = templatedict[template]['count']
        pos     = templatedict[template]['pos']
        x = pos['x']
        y = pos['y']
        basemac = templatedict[template]['mac']['base']
        macstart = templatedict[template]['mac']['start']
        interlinks = templatedict[template]['interlinks']

        print('Working on role: ' + template)
        print('Start position: ' + str(pos))
        print('provision ' + str(count) + ' amounts.')

        for tn in jsondict: #Loop through available templates in GNS3 and find id
            if tn['name'] == reqname: #Found template matching desired role (i.e. leaf, spine..)  
                tid = tn['template_id'] #VNF Template ID from GNS3
                print('Found template id ' + tid + ' for name ' + reqname)
                newdict[template] = { "name" : reqname, "count" : count, "tid" : tid, "pos" : pos } #Build new key/value dict
                url = baseurl + '/' + projecturi + '/' + projectid + '/templates/' + tid
                #print(url)
                urltuple = ( url, httpheaders )
                port = interlinks['port']
                for loop in range (0, count): #Provision all devices for this role
                    adapter = interlinks['1st_adapter_number']
                    nodename = template + str(loop+1)
                    print('Creating node ' + nodename + '...')
                    jsonadd = { "x" : x, "y" : y }
                    resp = json.loads(request ( urltuple, "post", jsonadd )) #create node in project
                    nodeid = resp['node_id'] #Get nodeid for later usage
                    #print(type(resp))
                    time.sleep(0.5)
                    x += nd['posshift'] #How much to shift next device icon

                    #Build JSON data to build links
                    il = interlinks['linkcount'] #How many interlinks per node
                    ports = { }
                    adapterstep = interlinks['adapterstep']
                    for link in range(0, il): #Add for total nr of links needed the port details
                        linknr = link+1 #Start @1
                        ports[linknr] = { "adapter_number" : adapter, "port" : port }
                        adapter += adapterstep #Next port
                    
                    newdict['nodes'][nodename] = { "nodeid" : nodeid, "interlinks" : ports } #Add nodeid & ports to hostname for later usage

                    
    #Add hostname and mac address to created nodes
    url = baseurl + '/' + projecturi + '/' + projectid
    for obj in newdict['nodes']: #cycle to all nodes and request API call to change values in GNS3 project
        nodeid = newdict['nodes'][obj]['nodeid']
        nodename = obj
        macadd = ":00:01"
        nodeurl = url + '/' + 'nodes/' + nodeid
        macaddress = basemac + str(macstart) + macadd
        jsonadd = { "name" : nodename, "properties" : { "mac_address" : macaddress }  }
        urltuple = ( nodeurl, httpheaders )
        resp = request ( urltuple, "put", jsonadd ) #Update node config
        time.sleep(0.5)
        macstart += 1

    
    #Add links to nodes
    linkurl = url + '/links' #Url to create links

    for nodename in newdict['nodes']:
        obj =  newdict['nodes'][nodename]
        if 'leaf' in nodename:
            nodeid = obj['nodeid']
            linkcnt = len(obj['interlinks'])

            for link in range (linkcnt):
                linknr = link+1
                adapter = obj['interlinks'][linknr]['adapter_number']
                port = obj['interlinks'][linknr]['port']
                spine = 'spine'+str(linknr)
                linkpeerid = newdict['nodes'][spine]['nodeid']
                linkpeerport = newdict['nodes'][spine]['interlinks']




            
            


    #print(newdict)
                

            

    sys.exit()


########################
####  MAIN PROGRAM #####
########################

settings = readsettings ( settingsfile ) #Read settings to JSON object

# Request API call
urltuple = return_url ( settings ) #Return required URL, headers if needed & other option data
#print(urltuple)

if urltuple[0] == 'proceed = True': #GNS3 is already running, Report back to proceed & exit
    print(urltuple[0]) #output used by jenkins
    sys.exit()

response = request ( urltuple, "post") #Request API POST request

if 'creategns3project' in sys.argv[1:]: #Add nodes to project in GNS3
    if 'already exists' in response: #project was already created
        print(json.loads(response)['message'])
        resp = json.loads(request ( urltuple, "get" )) #Query project to find ID
        #print(resp)
        #print(urltuple)
        for obj in resp:
            if obj['name'] == urltuple[3]['name']:
                print('Project ID : ' + obj['project_id'])
                response = json.dumps(obj)
    else:
        print('Project ' + response['project_id'] + ' created.')

    time.sleep(1)
    result = provisiongns3project(json.loads(response))


if 'gns' in urltuple[2]['runtype'] and 'start' in urltuple[0]:
    print('proceed = Wait') #used by jenkins


#If AWX project was launched, check its jobstatus till finished
if 'awx' in urltuple[2]['runtype']:
    checkresult = jobstatuschecker ( response )
    print('proceed =', checkresult) #used by jenkins


