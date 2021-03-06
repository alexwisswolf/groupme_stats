import requests
import csv

class GroupMe(object):
    def __init__(self, token):
        self.base_url = "http://api.groupme.com/v3/"
        self.token = token
        self.messages = []

    def build_url(self, url, params=None):
        url = "{}{}?token={}".format(self.base_url, url, self.token)
        
        if params:
            if type(params) is not dict:
                print("Params argument for URL must be dictionary. Exiting.")
                exit(1)
            for key, val in params.items():
                url = "{}&{}={}".format(url, key, val)
        
        return url
        

    def get_groups(self):
        groups_url = self.build_url("groups")
        resp = requests.get(groups_url)
    
        if resp.status_code == 200:
            return resp.json()['response']
        else:
            print("Failed to get groups.")
            print(response.text)
            exit(1)

    def get_group_id(self, group_name):
        groups = self.get_groups()
        for group in groups:
            if group["name"] == group_name:
                return group["group_id"]
        
        print("Failed to find group with name {}. Exiting".format(group_name))

    def get_group(self, group_id):
        group_url = self.build_url("groups/{}".format(group_id))

        resp = requests.get(group_url)
        if resp.status_code == 200:
            return resp.json()['response']
        else:
            print("Failed to get group {}.".format(group_id))
            print(resp.text)
            exit(1)
        

    def get_all_messages(self, group_id, limit=100):
        return_code = -1
        while return_code != 304:
        #while len(self.messages) < 500:
            if self.messages == []:
                params = {
                    "limit": limit
                }
            else:
                params = {
                    "limit": limit,
                    "before_id": last_message
                }

            message_url = self.build_url("groups/{}/messages".format(group_id), params)

            resp = requests.get(message_url)
            return_code = resp.status_code
            if return_code == 200:
                content = resp.json()['response']
                if self.messages == []:
                    print("Group {} contains {} messages.".format(group_id, content['count']))
                self.messages.extend(content['messages'])
            elif return_code == 304:
                print("Retrieved all messages")
            else:
                print("Failed to get messages for group {}. Exiting.".format(group_id))
                print(resp.text)
                exit(1)
            print("Retrieved {} messages out of {}.".format(len(self.messages), content['count']))
            last_message = self.messages[-1]['id']

        return self.messages
    
    def find_most_liked(self, group_id):
        if self.messages == []:
            messages = self.get_all_messages(group_id)

        most_liked = {
            "favorited_by": []
        }
        for message in self.messages:
            if message.get("text"):
            
                message_text = message["text"].encode("ascii", "ignore").decode("ascii")

                if "270" in message_text:
                    print("Found")
                    print(message)
                
            if len(message['favorited_by']) > len(most_liked['favorited_by']):
                print(most_liked)
                print(len(message['favorited_by']))
                most_liked = message
        
        return most_liked


    def sum_likes(self, group_id):
        if self.messages == []:
            messages = self.get_all_messages(group_id)

        summary = {}
        for message in self.messages:
            try:
                user = message['user_id']
                summary[user]['message_count'] += 1
                summary[user]['likes_received'] += len(message['favorited_by'])
                if user in message['favorited_by']:
                    summary[user]['self_likes'] += 1

                for liker in message['favorited_by']:
                    summary[liker]['likes_sent'] += 1


            except KeyError:
                summary[user] = {
                    "message_count": 0,
                    "likes_received": 0,
                    "self_likes": 0,
                    "likes_sent": 0
                }
        
        group = self.get_group(group_id)
        nicknames = {}
        for member in group['members']:
            nicknames[member['user_id']] = member['nickname']
        for user in summary.keys():
            try:
                summary[user]['nickname'] = nicknames[user]
            except KeyError:
                summary[user]['nickname'] = None
            try:
                summary[user]['likes_per_message'] = summary[user]["likes_received"] / summary[user]["message_count"]
            except ZeroDivisionError:
                summary[user]['likes_per_message'] = None
            try:
                summary[user]['send_receive_ratio'] = summary[user]["likes_sent"] / summary[user]["likes_received"]
            except ZeroDivisionError:
                summary[user]['send_receive_ratio'] = None

        return summary

if __name__ == "__main__":
    import sys
    token = sys.argv[1]
    group_me = GroupMe(token)

    group_name = "NPR Totebags and John Oliver"
    #group_name = "Nash New Years"
    group_id = group_me.get_group_id(group_name)

    #messages = group_me.get_messages(group_id)
    #most_liked = group_me.find_most_liked(group_id)
    #print(most_liked)

    most_liked = group_me.find_most_liked(group_id)
    print(most_liked)

    summary = group_me.sum_likes(group_id)
    print(summary)
    with open('groupme_summary.csv', 'w', newline="\n") as csv_file:
        print(list(summary.keys())[0])
        writer = csv.DictWriter(csv_file, fieldnames=summary[list(summary.keys())[0]].keys())
        writer.writeheader()
        for user, info in summary.items():
            print(info)
            writer.writerow(info)
            

    