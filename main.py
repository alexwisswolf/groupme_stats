import requests

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
            print("Failed to get groups")
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
                print(return_code)
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
            if len(message['favorited_by']) >= len(most_liked['favorited_by']):
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
                summary[user]['like_count'] += len(message['favorited_by'])

            except KeyError:
                summary[user] = {
                    "message_count": 0,
                    "like_count": 0
                }
        
        group = self.get_group(group_id)
        nicknames = {}
        for member in group['members']:
            nicknames[member['user_id']] = member['nickname']
        for user in summary.keys():
            summary[user]['nickname'] = nicknames[user]
            summary[user]['likes_per_message'] = summary[user]["like_count"] / summary[user]["message_count"]

        return summary

if __name__ == "__main__":
    import sys
    token = sys.argv[1]
    group_me = GroupMe(token)

    group_name = "https://www.ncpgambling.org"
    #group_name = "Nash New Years"
    group_id = group_me.get_group_id(group_name)

    #messages = group_me.get_messages(group_id)
    #most_liked = group_me.find_most_liked(group_id)
    #print(most_liked)

    most_liked = group_me.find_most_liked(group_id)
    print(most_liked)

    summary = group_me.sum_likes(group_id)
    print(summary)
    for user, info in summary.items():
        print(info)