from views import Hello, SomeParams

routes = [
    [Hello, '/api/hello'],
    [SomeParams, '/api/double/<int:value>']
]