import json
from http.server import HTTPServer, BaseHTTPRequestHandler

USERS_LIST = [
    {
        "id": 1,
        "username": "theUser",
        "firstName": "John",
        "lastName": "James",
        "email": "john@email.com",
        "password": "12345",
    }
]


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_response(self, status_code=200, body=None):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(body if body else {}).encode('utf-8'))

    def _pars_body(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        return json.loads(self.rfile.read(content_length).decode('utf-8'))  # <--- Gets the data itself

    def do_GET(self):
        if self.path == "/users":
            status = 200
            body = USERS_LIST
            self._set_response(status, body)
        elif self.path.startswith("/user/"):
            username = self.path.split("/")[-1]  # Extract the username from the URL
            user_data = None

            for user in USERS_LIST:
                if user["username"] == username:
                    user_data = user
                    break

            if user_data is not None:
                status = 200
                body = user_data
            else:
                status = 400
                body = {"error": "User not found"}

            self._set_response(status, body)
        elif self.path == "/reset":
            status = 200
            new_users_list = [
                {
                    "id": 1,
                    "username": "theUser",
                    "firstName": "John",
                    "lastName": "James",
                    "email": "john@email.com",
                    "password": "12345",
                }
            ]
            USERS_LIST.clear()  # Clear the existing list
            USERS_LIST.extend(new_users_list)  # Set it to the new data
            body = {"message": "USERS_LIST reset successfully"}
            self._set_response(status, body)
        else:
            self._set_response(418)

    def do_POST(self):
        try:
            request_body = self._pars_body()

            if self.path == "/user":
                if isinstance(request_body, dict):
                    is_valid_user = all(
                        key in request_body for key in ["id", "username", "firstName", "lastName", "email", "password"])
                    if is_valid_user:
                        user_id = request_body["id"]

                        if any(user["id"] == user_id for user in USERS_LIST):
                            self._set_response(400, {})
                        else:
                            USERS_LIST.append(request_body)
                            self._set_response(201, request_body)
                    else:
                        self._set_response(400, {})
                else:
                    self._set_response(400, {})

            elif self.path == "/user/createWithList":
                if isinstance(request_body, list) and all(isinstance(user, dict) and all(
                        key in user for key in ["id", "username", "firstName", "lastName", "email", "password"]) for
                                                          user in request_body):
                    user_ids = {user["id"] for user in request_body}

                    if any(user["id"] in user_ids for user in USERS_LIST):
                        self._set_response(400, {})
                    else:
                        USERS_LIST.extend(request_body)
                        self._set_response(201, request_body)
                else:
                    self._set_response(400, {})
            else:
                self._set_response(418)
        except json.JSONDecodeError:
            self._set_response(400, {})

    def do_PUT(self):
        if self.path.startswith("/user/"):
            user_id = self.path.split("/")[-1]  # Extract the user ID from the URL

            # Find the user with the given ID in USERS_LIST
            user_to_update = None
            for user in USERS_LIST:
                if str(user["id"]) == user_id:
                    user_to_update = user
                    break

            if user_to_update:
                try:
                    request_data = self._pars_body()

                    # Check if the request body has the required structure
                    required_keys = ["username", "firstName", "lastName", "email", "password"]
                    if all(key in request_data for key in required_keys):
                        # Update the user's data
                        user_to_update.update(request_data)
                        self._set_response(200, user_to_update)
                    else:
                        self._set_response(400, {"error": "not valid request data"})
                except json.JSONDecodeError:
                    self._set_response(400, {"error": "not valid request data"})
            else:
                self._set_response(404, {"error": "User not found"})
        else:
            self._set_response(418)

    def do_DELETE(self):
        if self.path.startswith("/user/"):
            user_id = self.path.split("/")[-1]  # Extract the user ID from the URL
            user_to_delete = None

            for user in USERS_LIST:
                if str(user["id"]) == user_id:
                    user_to_delete = user
                    break

            if user_to_delete is not None:
                USERS_LIST.remove(user_to_delete)  # Remove the user from USERS_LIST
                status = 200
                body = {}
            else:
                status = 404
                body = {"error": "User not found"}

            self._set_response(status, body)
        else:
            self._set_response(418)


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, host='localhost', port=8000):
    server_address = (host, port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
