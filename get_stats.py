from run import gt

def get_stats(date_begin = float("-inf"), date_end = float("inf")):
    users = gt.get_users_col().distinct('login')
    data = dict()
    overall = {'overall_size' : 0, 
                'overall_files_count' : 0, 
                'overall_folders_count' : 0, 
                'tags' : {}}
    for user in users:
        user_data = gt.search_files(user, data = [date_begin, date_end])
        files_count = len([file_data for file_data in user_data if file_data['type'] == 'file'])
        folders_count = len([file_data for file_data in user_data if file_data['type'] == 'folder'])

        overall['overall_files_count'] += files_count
        overall['overall_folders_count'] += folders_count

        data.update({ user: 
                        {'files_count' : files_count,
                         'folders_count': folders_count,
                         'avg_size': 0,
                         'tags': {} }})

        for line in user_data:
            for tag in line['tags']:
                if tag in overall['tags'].keys():
                    overall['tags'][tag] += 1  
                else:
                    overall['tags'].update({tag : 1})
                
                if tag in data[user]['tags'].keys():
                    data[user]['tags'][tag] += 1
                else:
                    data[user]['tags'].update({tag : 1})

            if line['type'] == 'file':
                data[user].update({'avg_size' : data[user]['avg_size'] + line['size']})
                overall['overall_size'] += line['size']

    return {'overall' : overall, 'users' : data}
