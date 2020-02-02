from run import gt

def get_stats(date_begin = float("-inf"), date_end = float("inf")):
    '''Function to get statistics of users activity

        arguments:
            date_begin (-infinity by default) -- start of stats period
            date_end (+infinity by default) -- end of stats peroid

        returns dictionary with structure:

        {'overall' (Stats for all users):
            {'overall_size': total size of all files,
             'overall_files_count': total count of all files,
             'overall_folders_count': total count of all folders,
             'tags' : {
                 'tag': how many times this tag was used
                }
            },
         'user' (stats for every user):
            {'files_count': total count of user's files,
             'folders_count': total count of user's folders,
             'total_size': total size of all user's files,
             'tags': {
                 'tag': how many times this tag was used by user
                }
             }
        }

    '''
    # get all users logins
    users = gt.get_users_col().distinct('login')
    # initialize user data dictionary
    data = dict()
    # initialize overall data dictionary
    overall = {'overall_size' : 0, 
                'overall_files_count' : 0, 
                'overall_folders_count' : 0, 
                'tags' : {}}
    for user in users:
        # get user's activity in period
        user_data = gt.search_files(user, data = [date_begin, date_end])
        # count files
        files_count = len([file_data for file_data in user_data if file_data['type'] == 'file'])
        # count folders
        folders_count = len([file_data for file_data in user_data if file_data['type'] == 'folder'])
        # add to overall stats
        overall['overall_files_count'] += files_count
        overall['overall_folders_count'] += folders_count
        # add to user's stats
        data.update({ user: 
                        {'files_count' : files_count,
                         'folders_count': folders_count,
                         'total_size': 0,
                         'tags': {} }})
        # check every file
        for line in user_data:
            # check every tag of file
            for tag in line['tags']:
                if tag in overall['tags'].keys():
                    overall['tags'][tag] += 1  
                else:
                    overall['tags'].update({tag : 1})
                
                if tag in data[user]['tags'].keys():
                    data[user]['tags'][tag] += 1
                else:
                    data[user]['tags'].update({tag : 1})
            # add total size of file
            if line['type'] == 'file':
                data[user]['total_size'] += line['size']
                overall['overall_size'] += line['size']

    return {'overall' : overall, 'users' : data}
