import sys
import math
import time
import grpc

import mailbox_pb2
import mailbox_pb2_grpc

MAILMAN_ADDRESS = '35.231.123.164:50051'

REGISTER_MAILBOX = 'add'
REMOVE_MAILBOX = 'rm'
GET_MAIL = 'get'
SEND_MAIL = 'send'
LIST_MAILBOXES = 'ls'


def print_usage():
    def padd(s):
        return ' ' * (12 - len(s))

    print(f'\n{REGISTER_MAILBOX}{padd(REGISTER_MAILBOX)}register a mailbox')
    print(f'{REMOVE_MAILBOX}{padd(REMOVE_MAILBOX)}remove a mailbox')
    print(f'{GET_MAIL}{padd(GET_MAIL)}get mail')
    print(f'{SEND_MAIL}{padd(SEND_MAIL)}send mail')
    print(f'{LIST_MAILBOXES}{padd(LIST_MAILBOXES)}list mailboxes\n')

    print(f'> {REGISTER_MAILBOX} "mailbox_name"')
    print(f'> {REMOVE_MAILBOX} "mailbox_name" "password"')
    print(f'> {GET_MAIL} "mailbox_name" "password"')
    print(f'> {SEND_MAIL} "source_mailbox_password" "source_mailbox_name" "destination_mailbox_name" "message"')
    print(f'> {LIST_MAILBOXES} "query"\n')


def print_mail(mail):
    print('\n____begin_mail____')
    print(f'timestamp: {mail.timestamp}')
    print(f'source: {mail.source_name}')
    print(f'message: {mail.message}')
    print('____end_mail______\n')


def register_mailbox(name):
    request = mailbox_pb2.RegisterMailboxRequest(name=name)

    with grpc.insecure_channel(MAILMAN_ADDRESS) as channel:
        stub = mailbox_pb2_grpc.MailManStub(channel)
        response = stub.RegisterMailbox(request)

    password = response.password
    error = response.error

    if password: print(f'password for {name} is {password}')
    else: print(error)


def remove_mailbox(name, password):
    request = mailbox_pb2.RemoveMailboxRequest(name=name, password=password)

    with grpc.insecure_channel(MAILMAN_ADDRESS) as channel:
        stub = mailbox_pb2_grpc.MailManStub(channel)
        response = stub.RemoveMailbox(request)

    error = response.error

    if error: print(error)
    else: print(f'{name} has been removed')


def get_mail(name, password):
    request = mailbox_pb2.GetMailRequest(name=name, password=password)

    with grpc.insecure_channel(MAILMAN_ADDRESS) as channel:
        stub = mailbox_pb2_grpc.MailManStub(channel)
        response = stub.GetMail(request)

    error = response.error
    mails = response.mails

    if error: print(error)
    elif len(mails) == 0: print("no mail")
    else:
        print(f'{len(mails)} mails have been removed from {name}')
        for mail in mails: print_mail(mail)


def send_mail(password, source_name, destination_name, message):
    request = mailbox_pb2.SendMailRequest()

    request.password = password
    request.mail.timestamp = math.floor(time.time())
    request.mail.source_name = source_name
    request.mail.destination_name = destination_name
    request.mail.message = message

    with grpc.insecure_channel(MAILMAN_ADDRESS) as channel:
        stub = mailbox_pb2_grpc.MailManStub(channel)
        response = stub.SendMail(request)

    error = response.error
    time_until_pickup = response.time_until_pickup
    mails = response.mails

    if error: print(error)
    else:
        print(f'mail is waiting in {source_name} to be picked up by the mailman')
        print(f'time until pickup: {time_until_pickup} seconds')
        if len(mails) > 0:
            print(f'{len(mails)} units of mail have been removed from {source_name}')
            for mail in mails: print_mail(mail)


def list_mailboxes(query):
    request = mailbox_pb2.ListMailboxesRequest(query=query)

    with grpc.insecure_channel(MAILMAN_ADDRESS) as channel:
        stub = mailbox_pb2_grpc.MailManStub(channel)
        response = stub.ListMailboxes(request)

    names = response.names

    if len(names) > 0:
        for name in names: print(name)


def run():
    try:
        request_type = sys.argv[1]

        if request_type == REGISTER_MAILBOX:
            name = sys.argv[2]
            register_mailbox(name=name)

        elif request_type == REMOVE_MAILBOX:
            name = sys.argv[2]
            password = sys.argv[3]
            remove_mailbox(name=name, password=password)

        elif request_type == GET_MAIL:
            name = sys.argv[2]
            password = sys.argv[3]
            get_mail(name=name, password=password)

        elif request_type == SEND_MAIL:
            password = sys.argv[2]
            source_name = sys.argv[3]
            destination_name = sys.argv[4]
            message = sys.argv[5]
            send_mail(password=password, source_name=source_name, destination_name=destination_name, message=message)

        elif request_type == LIST_MAILBOXES:
            try: query = sys.argv[2]
            except: query = ''
            finally: list_mailboxes(query=query)

        else:
            print_usage()
    except:
        print_usage()


if __name__ == '__main__':
    run()
