"""Game client for TicTacToe"""
import json
import requests
import sys
import time
from requests import ConnectionError
from decorators import (logger, execution_time_measurer,
                        safe_execution, dec_all_methods)


class UserException(Exception):
    pass


@dec_all_methods(logger(filename="cal.txt"))
@dec_all_methods(execution_time_measurer(filename="executio.txt"))
class Session(object):
    """Implements a game session"""

    def __init__(self, user, passw):
        self.username = user
        self.password = passw
        self.board = ""
        self.auth = (user, passw)
        self.match_id = None
        self.token = None

    def _get_token(self):
        """Get a token for auth"""
        url = "http://127.0.0.1:5000/api/token"
        req = requests.get(url, auth=(self.username, self.password))
        if req.status_code == requests.codes.ok:
            return req.json()['token']
        else:
            return None

    def _create_user(self):
        """Create user if it doesn't exist"""
        url = "http://127.0.0.1:5000/api/users"
        headers = {'content-type': 'application/json'}
        payload = {'username': self.username, 'password': self.password}
        req = requests.post(url, data=json.dumps(payload), headers=headers)
        if req.status_code != 201:
            raise UserException("Could not create user")

    @safe_execution(defaultValue=0)
    def login(self):
        """Get an auth

        Either get a token for the auth if users exists
        Or create a new user if one doesn't exist
        """
        self.token = self._get_token()
        if not self.token:
            self._create_user()
            self.token = self._get_token()
        self.auth = (self.token, None)

    @safe_execution(defaultValue=0)
    def get_match_id(self):
        """Get a match id from the server"""
        url = "http://127.0.0.1:5000/api/getmatch"
        req = requests.get(url, auth=self.auth)
        self.match_id = req.json()["match_id"]
        return self.match_id

    def _get_move(self):
        """Get player input for the next move"""
        move = raw_input("Choose a cell: ")
        if move not in self.board:
            print "Invalid move"
            return self._get_move()
        else:
            return move

    def _make_move(self):
        """Send the information about the move to the server"""
        url = "http://127.0.0.1:5000/api/match/" + str(self.match_id)
        headers = {'content-type': 'application/json'}
        move = self._get_move()
        payload = {'move': int(move)}
        req = requests.post(url, data=json.dumps(payload), headers=headers,
                            auth=self.auth)
        if req.status_code != 200:
            print req.text
            return self._make_move()

    @safe_execution(defaultValue=0)
    def play(self):
        """Main function for playing the game

        Gets the board from the server
        If it's a new board replaces the old one and prints the new one
        Then based on information received from the server decides if it's your
        turn, gets your input and sends it to the server
        If the server gives information about a winner it displays it and exits
        """
        url = "http://127.0.0.1:5000/api/match/" + str(self.match_id)
        while True:
            time.sleep(0.5)
            req = requests.get(url, auth=self.auth)
            if req.status_code == requests.codes.ok:
                response = req.json()
                new_board = response["Board"]
                if new_board != self.board:
                    self.board = new_board
                    print self.board
                    print "You are: " + response["XO"]
                    if response["Win"]:
                        print "Winner is: " + response["Win"]
                        break
                    if response["Move"]:
                        print "You move"
                        self._make_move()
                    else:
                        print "Your opponent moves"

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Expected input format: python client.py <user> <password>"
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        s = Session(username, password)
        try:
            s.login()
            s.get_match_id()
            s.play()
        except ConnectionError:
            print "Connection Error: Check if server is up"
