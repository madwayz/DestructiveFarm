import socket

from server import app
from server.models import FlagStatus, SubmitResult
from server import app, config as config_module
from server import reloader



RESPONSES = {
    FlagStatus.QUEUED: ['timeout', 'game not started', 'try again later', 'game over', 'is not up',
                        'no such flag'],
    FlagStatus.ACCEPTED: ['accepted', 'congrat'],
    FlagStatus.REJECTED: ['bad', 'wrong', 'expired', 'unknown', 'your own',
                          'too old', 'not in database', 'already submitted', 'invalid flag'],
}
# The RuCTF checksystem adds a signature to all correct flags. It returns
# "invalid flag" verdict if the signature is invalid and "no such flag" verdict if
# the signature is correct but the flag was not found in the checksystem database.
#
# The latter situation happens if a checker puts the flag to the service before putting it
# to the checksystem database. We should resent the flag later in this case.

READ_TIMEOUT = 5
APPEND_TIMEOUT = 0.05
BUFSIZE = 4096


def recvall(sock):
    sock.settimeout(READ_TIMEOUT)
    chunks = [sock.recv(BUFSIZE)]

    sock.settimeout(APPEND_TIMEOUT)
    while True:
        try:
            chunk = sock.recv(BUFSIZE)
            if not chunk:
                break

            chunks.append(chunk)
        except socket.timeout:
            break

    sock.settimeout(READ_TIMEOUT)
    return b''.join(chunks) # TODO: Удалить перевод в байты

def sendall(sock, text):
    sock.sendall(text.encode() + b'\n')


def submit_flags(flags, config):
    sock = socket.create_connection((config['SYSTEM_HOST'], config['SYSTEM_PORT']),
                                    READ_TIMEOUT)

    greeting = recvall(sock)
    # print('ENABLE_TOKEN_SUBMIT:', config['ENABLE_TOKEN_SUBMIT'])
    if config['ENABLE_TOKEN_SUBMIT']:
        if config['TOKEN_SUBMIT_MESSAGE'] not in greeting.decode():
            raise Exception('Tokensystem does not greet us: {}'.format(greeting))

        # print('TOKEN_SUBMIT:', config["TOKEN_SUBMIT"])
        sendall(sock, config["TOKEN_SUBMIT"])

    greeting = recvall(sock)
    if config['ENTER_FLAGS_MESSAGE'] not in greeting.decode():
        raise Exception('Checksystem does not greet us: {}'.format(greeting))

    unknown_responses = set()
    for item in flags:
        #print('item.flag:', item.flag)
        sendall(sock, item.flag)
        response = recvall(sock).decode().strip()
        if response:
            response = response.splitlines()[0]
        response = response.replace('[{}] '.format(item.flag), '')

        response_lower = response.lower()
        for status, substrings in RESPONSES.items():
            if any(s in response_lower for s in substrings):
                found_status = status
                break
        else:
            found_status = FlagStatus.QUEUED
            if response not in unknown_responses:
                unknown_responses.add(response)
                app.logger.warning('Unknown checksystem response (flag will be resent): %s', response)

        yield SubmitResult(item.flag, found_status, response)

    sock.close()
