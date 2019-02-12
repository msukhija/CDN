Implementation of CDN

In this project we implemented CDN(content distribution network.
Basically, In this browser will request to server for some file,
then here proxy server will redirect this request to CDN and the CDN 
will see that this request belongs to its Region and will check the 
file in its content server .if,then it will ask its content server to deliever 
the file.However if the file is not present in its CDN,then CDN will 
route this request to another CDN on basis of distance vector algorithm i.e 
that is looking for shortest path.then that CDN will pull that file from its 
content server and will give back file to requested CDN.
and this CDN will provide the file to browser.

how to run

1.Run proxy server  python3 proxy.py CDN_IP CDN_PORT proxy_port
2.Run CDN server python3 CDN.py CDN_PORT configfile.
For other CDN change the port number.
3.Run content server python3 server.py server_port.
 

For example to run with same configuration

Run all CDN nodes
 1  python3 CDND.py 8082 test.json
 2  python3 CDND.py 8086 testD.json
 3  python3 CDND.py 8081 testB.json
 4  python3 CDND.py 8085 testC.json
 Run proxy server
 1  python3 proxy.py CDN_IP CDN_PORT 8080
 Run content server
 1  python3 contentserver.py 9095
 2  python3 contentserver.py 9091
 3  python3 contentserver.py 9096
 4  python3 contentserver.py 8084



After executing above programms Make arequest from browser like http://africa/file.html
.proxy will make request to CDN and if CDN have the filethen it will redirect it to browser
 via proxy.if it doesnot have it then it will run shortest path algorithm to find out the best 
route other CDN with minimal cost.Here cost are taken as delays



Contact: msukhija@uh.edu



