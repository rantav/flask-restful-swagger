from views import UserResource, UserItemResource

routes = [
    [UserResource, '/api/users'],
    [UserItemResource, '/api/users/<int:user_id>']
]
