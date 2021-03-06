import praw
import requests
import re
import time

agentstring="/r/spam submission deleter version 1.1 by /u/captainmeta4"
r = praw.Reddit(user_agent=agentstring)
headers = {'User-Agent': agentstring}

print ("log in to reddit")
print ("")

username = input("reddit username: ")

try:
    #Note that the reddit password is never stored to a variable.
    r.login(username, input("reddit password: "))
    print ("")
    print ("login successful")
except:
    print ("")
    print ("login failed. you must log in to use this script.")
    input("press enter to quit.")
    quit()

print ("")


#Load the spam reports
spamreports = r.search("author:"+username, subreddit="spam", sort = "new", limit=None)

print ("List of spam reports loaded.")

#Initialize stuff
alreadychecked = []
nonbannedusers = []
count=0
dupcount=0
sbcount=0
invalidcount=0

print("")
print("delete failed reports in addition to successful ones?")
if "y" in input("yes/no ").lower():
    delete_all = 1
else:
    delete_all = 0

#Check through spam reports
for thing in spamreports:
    #needs to be a try so that we can ignore invalid submissions
    try:
        reporteduser=str(re.search("(?:u(?:ser)?/)([\w-]+)(?:/)?", thing.url).group(1))
          
        #If it's not a duplicate...
        if reporteduser not in alreadychecked:
            #...then check profile
            u = requests.get("http://reddit.com/user/"+reporteduser+"/?limit=1", headers=headers)

            #Deal with any ratelimiting
            while u.status_code==429:
                print ("Too many requests. Waiting 10 seconds")
                time.sleep(10)
                u = requests.get("http://reddit.com/user/"+reporteduser+"/?limit=1")

            #If shadowbanned...
            if u.status_code==404:
                print ("shadowbanned: /u/"+reporteduser)
                #Delete the submission
                thing.delete()
                sbcount+=1
            else:
                print ("not shadowbanned: /u/"+reporteduser)
                nonbannedusers.append(reporteduser)
                if delete_all==1:
                    thing.delete()
                        
            alreadychecked.append(reporteduser)

        #If duplicate...   
        elif reporteduser in alreadychecked:
            print ("duplicate entry: /u/"+reporteduser)
            thing.delete()
            dupcount+=1



    except:
        print ("invalid submission: "+thing.url)
        invalidcount+=1

    count+=1

print ("")

#If there are nonbanned users...
if len(nonbannedusers)!=0:

    #Alphabetize the list
    nonbannedusers.sort()

    print ("assembling message")
    print ("")

    #Put the message together
    message = ("^(This message was automatically generated by /u/captainmeta4's /r/spam review script.)[^( GitHub)](https://github.com/captainmeta4/Spam-Report-Reviewer)\n\n"
               "/u/"+username+" has "+str(count)+" /r/spam reports, of which "+str(dupcount)+ " are duplicates and "+str(invalidcount)+" are invalid submissions that do not link to a userpage.\n\n"
               "Of the "+str(count-dupcount-invalidcount)+" unique users reported, "+str(sbcount)+" have been shadowbanned, leaving the following "+str(len(nonbannedusers))+" non-banned users.\n\n")
    
    for user in nonbannedusers:
        message = message+"* /u/"+user+"\n"

    #Send message to user
    r.send_message(username,"Spam reports",message)
    print ("message successfully sent to /u/"+username+".")

    #send to admins
    r.send_message("/r/spam","Spam reports",message)
    print ("message successfully sent to /r/spam")
     
#else (if there are no nonbanned users)
else:
    print ("/u/"+searchuser+" has no non-banned /r/spam reports.")


    
print ("")

input("press enter to quit")
