from utils.db import query_one

def get_user_profile(user_id):
    """Retrieve the user's email"""
    sql = '''
        SELECT email 
        FROM Users 
        WHERE user_id = ?
    '''

    data = (user_id,)

    email = query_one(sql, data)

    return email['email']


