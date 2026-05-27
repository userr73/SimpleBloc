from utils.db import query_one

def get_default_category_id(user_id):
    """Retrieves the user's default category's category ID"""
    sql = '''
        SELECT category_id
        FROM Categories
        WHERE user_id = ? AND category_name = ?
    '''

    data = (
        user_id,
        'No category'
    )

    category = query_one(sql, data)

    return category['category_id']


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


