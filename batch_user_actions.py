#!/usr/bin/env python3
#The MIT License (MIT) Copyright (c) 2015 Mahyar

#imports
import json,sys,os.path,uuid
from datetime import datetime, timezone

import praw
from prawoauth2 import PrawOAuth2Server, PrawOAuth2Mini

# constants
dev_name       = "test_throwaway392"
cred_file_path = 'cred.json'
user_agent     = "python:batch_user_actions:v0.0.2 (by /u/%s)" % dev_name
scopes         = ['identity', 'read', 'privatemessages', 'edit']

#you probably want to put this in a seperate file you from keyfile import * 
#keys / users
key_set = {}
app_key = "zMWc9bcUtQ2Y7g"
app_secret = "QJJqqJcdUCZskUwtWKi7kWWOmN4"
refresh_token = ""
access_token  = ""

reddit_client = praw.Reddit(user_agent=user_agent)

#--------------------------  json crap

class CustomObjectEncoder(json.JSONEncoder):
    """Since python's json encoder craps out as soon as it see a non-basic object, this 
    is needed to deal with non-standard object types. """
    def default(self,obj):
        out = '<err>'
        try:
            out = json.JSONEncoder.default(self, obj)
        except:
            try:
                out = str(obj)
            except:
                pass
        return out

#-------------------------- creds

def setupCredentials(user_name):
    loadCredentials()
    if not user_name in key_set:
        getCredentials(user_name)
    setCredentials(user_name)
    saveCredentials()
    print('login as',user_name)

def setCredentials(user_name):
    global refresh_token, access_token
    refresh_token = key_set[user_name]['refresh_token']
    access_token = key_set[user_name]['access_token']

def getCredentials(user_name):
    oauthserver   = PrawOAuth2Server(reddit_client, app_key, app_secret, state=user_agent, scopes=scopes)
    oauthserver.start()
    tokens = oauthserver.get_access_codes()
    print("got credentials for user",user_name)
    key_set[user_name] = tokens #TODO get actual user name
    print

def saveCredentials():
    #TODO yup its not secure to do this
    with open(cred_file_path,'w') as f:
        jout = json.dumps(key_set,indent=4,cls=CustomObjectEncoder)
        f.write(jout)

def loadCredentials():
    if os.path.exists(cred_file_path):
        global key_set
        with open(cred_file_path,'r') as f:
            text = f.read()
            key_set = json.loads(text)
    else:
        with open(cred_file_path,'w') as f:
            f.write('{}')


#-------------------------- get user resource

def collect_user_data(oauth_helper,user_name,resource_name=None):
    after = 7
    count = 0
    output_list = []
    type_name = 'all' if not resource_name else resource_name

    print("collecting '%s' for user '%s'" % (type_name,user_name))
    while after:
        count += 1
        if after == 7: after = None
        try:
            after = user_data_loop(after,oauth_helper,output_list,user_name,resource_name)
        except praw.errors.OAuthInvalidToken:
            print("token expired, refresh 'em!")
            oauth_helper.refresh()

    return output_list

def user_data_loop(after,oauth_helper,out,user_name,resource_name=None):
    oauth_helper.refresh()
    resource_name = '/'+resource_name if resource_name else ''
    url = "https://www.reddit.com/user/%s%s/" % (user_name,resource_name)
    limit = 100
    c = []
    if (after):
        c = reddit_client.get_content(url,limit=limit,params=dict(after=after))
    else:
        c = reddit_client.get_content(url,limit=limit)
    c = list(c)
    if len(c) > 0:
        last = vars(c[-1])
        for i in c:
            itm = i
            out.append(itm)
        if last:
            name = last['name']
            print('last item id:',name,'chunk count:',len(c),'total:',len(out))
            return name
    print('empty result, probably finished')
    return None

#-------------------------- write to json file

def write_output(name,output):
    f_name = "%s.json" % name
    if os.path.exists(f_name):
        noise = uuid.uuid4()
        f_name = "%s__%s.json" % (name, noise)
    with open(f_name,'w') as f:
        time = datetime.now(timezone.utc).astimezone().isoformat()
        dict_to_ouput = dict(name=name,generated_at=time,comments=output)
        json_output = json.dumps(dict_to_ouput,indent=4,cls=CustomObjectEncoder)
        f.write(json_output)
    print("wrote to",f_name)

def write_data_to_json(user_name,reddit_objects):
    print("will save for",user_name)
    vars_out = [vars(i) for i in reddit_objects]
    write_output(user_name,vars_out)

#-------------------------- delete user resources

def delete_editable_objects(reddit_objects):
    "This is a slow operation becasue it's deleting one object at a time."
    num = len(reddit_objects)
    count = 0
    print("deleting",num,"objects")
    for i in reddit_objects:
        count += 1
        print(count,"/",num,"will delete ",i.name,end=" ")
        try:
            resp = i.delete()
        except praw.errors.OAuthInvalidToken:
            oauth_helper.refresh()
            resp = i.delete()
        print("delete resp",resp)
    print("finished deleting")

#--------------------------

def main(for_user_name,as_user_name):
    setupCredentials(as_user_name)

    oauth_helper = PrawOAuth2Mini(reddit_client, scopes=scopes,
        app_key=app_key, app_secret=app_secret, 
        access_token=access_token, refresh_token=refresh_token)

    out = collect_user_data(oauth_helper,for_user_name)
    write_data_to_json(for_user_name,out)
    # if (for_user_name == as_user_name):
        # delete_editable_objects(out)
    print()

def mini_main():
    as_user = 'test_throwaway392'
    for_user = 'karmanaut'
    main(for_user,as_user)

if __name__ == "__main__":
    mini_main() 