import urllib
from urllib import request, parse
from urllib.request import Request, urlopen
from http.server import BaseHTTPRequestHandler, HTTPServer
import http.client
from socketserver import ThreadingMixIn
from collections import defaultdict
from urllib.error import URLError, HTTPError
import threading
import datetime
import time
import sys
import os
import json

jsonfile=sys.argv[2]
tableFlag='False'
Running='True'
cachePolicy=sys.argv[3]

def getConfigFile():
    f = open(jsonfile, 'r')
    data = f.read()
    f.close()
    dict_1 = json.loads(data)
    return dict_1

def get_myNeighbors():
    dict_1 = getConfigFile()
    links= dict_1["links"]

    listt = []
    for i in range(len(links)):
        listt.append([links[i]['geo_tag'], links[i]['node_ip'], links[i]['node_port'], links[i]['link_delay']])
    return listt


def createFlag():
    dictflag='False'
    return dictflag

def loggingFile(logs):
    logFile = getConfigFile()['log_file']
    f = open(logFile, "a+")
    logData = str(datetime.datetime.now())+'\n' + logs +'\n'
    f.write(logData)
    f.close()

def createRoutingTable(addNeighbors):

    print("creating table")
    #print(addNeighbors)
    config = getConfigFile()
    myNodeIp = config['node_ip']
    myNodePort = config['node_port']
    myGeoTag = config['geo_tag']
    #print(myNodeIp)
    #print(myNodePort)
    #print(myGeoTag)
    R={}
    R[myGeoTag]=[myGeoTag, myNodePort,'0',(myNodeIp, myNodePort, myGeoTag)]
    #print(R)
   
    for i in addNeighbors:
            R[i[2]]=[i[2],i[1],i[3],(i[0],i[1],i[2])]
    print(R)      
    file = 'saveTable_' + getConfigFile()["node_name"] + '.txt'
    #print(file)
    f = open(file, "w+")
    f.write(str(R))
    f.close()
    intialFile = 'Intial_' + getConfigFile()["node_name"] + '.txt'
    #print(file)
    f = open(intialFile, "w+")
    f.write(str(R))
    f.close()
    return True

def makingDirectory(fileName):
    #Making Directory
    path = "./"+ getConfigFile()["node_name"]
    if not os.path.isdir(path):
        os.makedirs(path)
        print("making directory")
    else:
        print("Already directory present")
    fullpath = os.path.join(path, fileName)

    return fullpath

   

def sendTable():
    global tableFlag
    print("sendTable")
    print(tableFlag)
    while 1:
        try:
            time.sleep(2)
            if tableFlag=='True':
                #time.sleep(20)
                neighbors = get_myNeighbors()
                info = {'dvr':[]}
                fileName = 'saveTable_' + getConfigFile()["node_name"] + '.txt'
                f=open(fileName,'r')
                dict_1 = eval(f.read())
                f.close()
                print("sending table values")
                #print(dict_1)
                for v in dict_1.values():
                    print("value")
                    info['dvr'].append(v)
                print(info)         
                
                for i in neighbors:
                    url = 'http://' + i[1] + ':' + i[2] + '/' + '.DVR'
                    print(url)
                    req = urllib.request.Request(url, json.dumps(info).encode('utf-8'))
                    next_hop=str((getConfigFile()['node_ip'],getConfigFile()['node_port'],getConfigFile()['geo_tag']))
                    req.add_header('fromNode', next_hop)
                    print(url)
                    res = urllib.request.urlopen(req)
            else:
                print("don't send table")
        except Exception as e:
            print(str(e))

def measureDelay():
    global tableFlag
    neighbors = get_myNeighbors()
    print(neighbors)
    d = defaultdict(list)
    
    
               
    listt=getConfigFile()['links']
    while 1:
        try:
            print("I am in while loop")
            mynode=getConfigFile()['node_name']
            print(mynode)
            delaylist=[]
            for i in neighbors:        
                g=i[0]
                n=i[1]
                m=i[2]
                d1=i[3]
                starttime = time.time()
                      
                time.sleep(int(d1))
                print("url")
                url = "http://" + n + ":" + m + "/" + ".ping"
                req = urllib.request.Request(url)
                req.add_header('ping', getConfigFile()['geo_tag'])
                res = urllib.request.urlopen(req)
                #r = urllib.request.urlopen(url)
                #text=res.read()
                #text=r.read()
                print("Response")
                #print(text)
                print("status")
                print(res.status)
                endtime = time.time()
                totaltime = endtime - starttime
                print('---total-time---', totaltime)
                delaylist.append([n,m,g, int(totaltime)])
                print("**********delayList-3*******")
                print(delaylist)

            
            print("I am creating table")   
            if (createRoutingTable(delaylist)):
                tableFlag='True'
                #time.sleep(20)
                #sendTable()
                print("routing table created")
            else:
                tableFlag='False'
                print("routing table not created")
        except Exception as e:
            print(str(e)) 

class CdnServer(BaseHTTPRequestHandler):
   
    neighbors = get_myNeighbors()
    #port=getMyGeoLoc(geo_loc)
    
    global tableFlag
   

    def do_GET(self):
        try:
           
            config=getConfigFile()
           

            print(self.path)
            
            print("i am in get method of Node D")
            starttime = time.time()
            filename_w_ext = os.path.basename(self.path)
            name, ext = os.path.splitext(filename_w_ext)
            print(ext)
            
            if  self.path.endswith(".html") or self.path.endswith(".jpg") or self.path.endswith(".jpeg"):
                urlist = str(self.path).split('/')
                print(urlist)
                geo_loc = urlist[len(urlist) - 2]
                print("geo-location")
                print(geo_loc)
                #print(getConfigFile()['geo_tag'])
                #print(config['content_ip'])
                #print(config['content_port'])
                #print(filename_w_ext)
                print("*****headers******")
                print(self.headers)
                loggingFile("headers---" +str(self.headers))
                FROM=self.headers['From']
                
                print("******FROM*********")
                if FROM==None:
                    print("*******FROM is none*******")
                    mypath=getConfigFile()['geo_tag']
                else:    
                    mypath=str(FROM) + "-" + getConfigFile()['geo_tag']
                print("*********mypath********")
                print(mypath)
                Mypath=self.headers['Mypath']
                if Mypath==None:
                    finalPath=getConfigFile()['geo_tag']
                else:
                    finalPath=Mypath+ "-" +getConfigFile()['geo_tag']
                
                print("my geo location")
                
                print(getConfigFile()['geo_tag'])
                #making Directory
                fullpath=makingDirectory(filename_w_ext)
                print("*****fullpath***")
                print(cachePolicy)
                print(fullpath)
                if os.path.isfile(fullpath):
                    print("I am in cache")
                    loggingFile("finalPath...." + finalPath + '\n')
                    # Send response code and headers
                    if cachePolicy == '1':
                        self.send_response(200)
                        self.send_header('Content-type','application/x-binary')
                        self.send_header('finalPath', finalPath)
                        self.end_headers()
                        print("Path I have taken--",finalPath)
                    else :
                        self.send_response(200)
                        self.send_header('Content-type','application/x-binary')
                        self.send_header('cacheFlag','True')
                        self.send_header('finalPath', finalPath)
                        self.end_headers()
                        print("Path I have taken--",finalPath)
                    # Send the binary file
                    with open(fullpath,'rb') as f:
                        self.wfile.write(f.read())

                elif geo_loc == getConfigFile()['geo_tag']:
                    print("I am not in cache")
                    loggingFile("finalPath...." + finalPath + '\n')
                    url = "http://" + config['content_ip'] + ":" + config['content_port'] + "/" + filename_w_ext
                    req = urllib.request.Request(url)
                    newresponse = urllib.request.urlopen(req)
                    text=newresponse.read()
                    headers = newresponse.info()
                    loggingFile("requesting...." + url + '\n')
                    #print(text)
                    if cachePolicy == '1':
                        print("I am in cachePolicy 1")
                        self.send_response(200)
                        self.send_header("Content-type", 'text/html')
                        self.send_header("Content-length", headers['Content-Length'])
                        self.send_header('finalPath', finalPath)
                        self.end_headers()
                        print("Path I have taken--",finalPath)
                        self.wfile.write(text)
                    else :
                        print("I am in cachePolicy 2")
                        self.send_response(200)
                        self.send_header("Content-type", 'text/html')
                        self.send_header("Content-length", headers['Content-Length'])
                        self.send_header('cacheFlag','False') 
                        self.send_header('finalPath', finalPath)
                        self.end_headers()
                        print("Path I have taken--",finalPath)
                        self.wfile.write(text)
                    print("Writing file to directory")
                    print(fullpath)
                    f=open(fullpath, 'wb+')
                    f.write(text)
                    f.close()
                    


                else :
                    
                   
                    fileName = 'saveTable_' + getConfigFile()["node_name"] + '.txt'
                    inf=open(fileName,'r')
                    data=inf.read()
                    inf.close()
                    myRoutTable = eval(data)
                    print("searching for port")

                    if geo_loc in myRoutTable:
                        print("yes in my myRoutTable")
                        delayTime=myRoutTable[geo_loc][2]
                        print("my delaytime to go on other CDN--",delayTime)
                    else:
                        time.sleep(2)
                        print("NOT in my myRoutTable")

                    cdnUrl = 'http://' + myRoutTable[geo_loc][3][0] + ':' + myRoutTable[geo_loc][3][1] + '/' + geo_loc + '/' + filename_w_ext
                    print(cdnUrl)
                    loggingFile("requesting...." + cdnUrl + '\n')
                    urlist = str(self.path).split('/')
                    print(urlist)
                    geo_loc = urlist[len(urlist) - 2]
                    print("geo-location of else loop")
                    print(geo_loc)
                    req = urllib.request.Request(cdnUrl)
                    req.add_header('from', getConfigFile()['geo_tag'])
                    
                    req.add_header("mypath", mypath)
                    headers = ''
                    with urllib.request.urlopen(req) as res:
                        text = res.read()
                        headers = res.info()
                        print(res.info())
                    print("*****sleep*****")   
                    time.sleep(delayTime)    
                    finalPath=headers['finalPath']
                    loggingFile("finalPath...." + finalPath + '\n')
                    
                    print("**********finalPath******")
                    print("Path I have taken--",finalPath)   
                    print("******cache************")    
                    cache=headers['cacheFlag']
                    print(cache)
                    if cachePolicy =='2':
                        print("I am in cache policy-2")
                        if cache =='False':
                            print("I have False flag in policy-2  and  I am not caching")
                            self.send_response(200)
                            self.send_header("Content-type", 'text/html')
                            self.send_header('Content-length', headers['Content-length'])
                            self.send_header('cacheFlag','False')
                            self.send_header('finalPath', finalPath)
                            self.end_headers()
                            self.wfile.write(text)
                        else :
                            print("I have True Flag in cache policy-2 and I am caching")
                            self.send_response(200)
                            self.send_header("Content-type", 'text/html')
                            self.send_header('Content-length', headers['Content-length'])
                            self.send_header('cacheFlag','False')
                            self.send_header('finalPath', finalPath)
                            self.end_headers()
                            self.wfile.write(text)
                            print("Writing file to directory")
                            #writing to a file
                            print(fullpath)
                            f=open(fullpath, 'wb+')
                            f.write(text)
                            f.close()
                    else:
                        print("I am in cache policy-1")
                        self.send_response(200)
                        self.send_header("Content-type", 'text/html')
                        self.send_header('Content-length', headers['Content-length'])
                        self.send_header('finalPath', finalPath)
                        self.end_headers()
                        print("Path I have taken--",finalPath)
                        self.wfile.write(text)
                        print("Writing file to directory")
                        #writing to a file
                        print(fullpath)
                        f=open(fullpath, 'wb+')
                        f.write(text)
                        f.close()
           
            if self.path.endswith(".ping"):
                self.send_response(200)
                ping = self.headers['ping']
                print("*****ping******")
                print(ping)
                for i in self.neighbors:
                    if i[0] == ping:
                        print("pong wait... ", i[3])
                        time.sleep(int(i[3]))
                self.end_headers()
                #self.measureDelay()
               
            else:
                self.send_response(404)

        except http.client.HTTPException as e:
            self.send_response(404)
            self.end_headers()

        except URLError as e:
            print(e)

   
    def do_POST(self):
            print(self.path)
            print("I am in post method of D")
            #print(self.rfile.read)
            
            if self.path.endswith(".DVR"):
                content_length = int(self.headers['Content-Length'])
                body = eval(self.rfile.read(content_length))
                print("the json i recieved")
                print(body)
                print("********tableFlag********")
                print(tableFlag)
                if tableFlag=='True':
                    fileName = 'saveTable_' + getConfigFile()["node_name"] + '.txt'
                    inf=open(fileName,'r')
                    data=inf.read()
                    inf.close()
                    myRoutTable = eval(data)
                    print("myRoutTable-1")
                    print(myRoutTable)
              
                    self.send_response(200)
   
                    fromNode = eval(self.headers['fromNode'])
                    print(fromNode)

                    dist=int(myRoutTable[fromNode[2]][2])
                    #dist=my
                    print("dist")
                    print(dist)
                    for v in body.values():
                        for item in v:
                            print("item")
                            geo=item[0]
                            port=item[1]
                            print(port)
                            cost=int(item[2])
                            #check geo locatipn in myRoutTable
                            if geo in myRoutTable:
                                if (dist + cost) < int(myRoutTable[geo][2]):
                                    print("In if condition")
                                    #print(myRoutTable[port][0])
                                    myRoutTable[geo][0]=  geo
                                    myRoutTable[geo][1] = port
                                    #print(myRoutTable[port][1])
                                    myRoutTable[geo][2] = cost + dist
                                    myRoutTable[geo][3] = fromNode
                                    print("Route Updated")
                                    

                            else:
                                print("geo is not in myRoutTable")
                                myRoutTable[geo] = [geo, port, cost + dist, fromNode]
                                
                            #print("myRoutTable-2")
                            #print(myRoutTable)
                    print("updating table")
                    fileName = 'saveTable_' + getConfigFile()["node_name"] + '.txt'
                    f = open(fileName, "w+")
                    f.write(str(myRoutTable))
                    f.close()       
                    print("Route added and Updated")
                    print("I am in the end of post method")
                    #print(myRoutTable)
                    self.end_headers()
                else:
                    print("Flag is False")
                    self.send_response(200)
                    self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """ This class allows to handle requests in separated threads.
        No further content needed, don't touch this. """



def run(server_class=ThreadedHTTPServer, handler_class=CdnServer):
    server_address = ('', cdnport)
    httpd = server_class(server_address, handler_class)
    print('Server running at localhost:', cdnport)
  

    try:

        t = threading.Thread(target=measureDelay)
        t.start()
        #time.sleep(20)
        t1 = threading.Thread(target=sendTable)
        t1.start()
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
    except Exception as e:
        print(str(e))
  
      


if __name__ == "__main__":
    from sys import argv

if len(argv) == 4:
   
    cdnport=int(argv[1])
   
    run()
else:
     print ('Incomplete argument.')
    #run()










