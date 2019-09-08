from zeep import Client
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from requests import Session
from zeep.transports import Transport
from zeep.exceptions import Error
from zeep.wsse.username import UsernameToken
from zeep.exceptions import ZeepWarning
import json, string, random, time, threading, sys, math
from configparser import SafeConfigParser
from faker import Faker
import datetime

# python log system library
import logging

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client


class MyLogSystem:
    def __init__(self):
        pass

    @staticmethod
    def start_log():
        http_client.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True


class CardListReader:
    def __init__(self):
        self.change_status_list = []
        self.change_name_list = []
        self.change_address_list = []

    def get_card_status_change_list(self):
        with open("change_status.txt", 'r') as fs:
            try:
                for line in fs:
                    rec_info = line.strip().split(";")
                    if len(rec_info) == 2:
                        self.change_status_list.append({'card_number': rec_info[0], 'status': rec_info[1]})
                    else:
                        print "Missing some of information from change_status.txt file"

            except:  # whatever reader errors you care about
                print "Can not open change_status.txt file"

    def get_card_name_change_list(self):
        with open("change_name.txt", 'r') as fs:
            try:
                for line in fs:
                    rec_info = line.strip().split(";")
                    if len(rec_info) == 3:
                        self.change_name_list.append(
                            {'card_number': rec_info[0], 'first_name': rec_info[1], 'last_name': rec_info[2]})
                    else:
                        print "Missing some of information from change_name.txt file"

            except:  # whatever reader errors you care about
                print "Can not open change_name.txt file"

    def get_card_address_change_list(self):
        with open("change_address.txt", 'r') as fs:
            try:
                for line in fs:
                    rec_info = line.strip().split(";")
                    if len(rec_info) == 5:
                        self.change_address_list.append(
                            {
                                'card_number': rec_info[0],
                                'mailAddress1': rec_info[1],
                                'mailAddress2': rec_info[2],
                                'mailState': rec_info[3],
                                'mailZip': rec_info[4],
                            })
                    else:
                        print "Missing some of information from change_address.txt file"

            except:  # whatever reader errors you care about
                print "Can not open change_name.txt file"


class FleetCard(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.config = SafeConfigParser()
        self.config.read('config.ini')
        self.wsdl_url = self.config.get('setting', 'wsdlURL')
        self.user_name = self.config.get('setting', 'username')
        self.password = self.config.get('setting', 'password')
        self.account_code = self.config.get('setting', 'accountCode')
        self.customer_id = self.config.get('setting', 'customerId')
        self.proxy_server_info = self.config.get('setting', 'proxy_server')

        self.is_use_proxy = True
        self.proxies = {
            'http': ''
        }
        self.sessions = Session()
        self.wsdl_client = None
        self.SERVER_ERROR_MSG = "SERVER_ERROR"
        self.NO_DATA = "NO_DATA"

        self.is_debug = False
        self.operation_mode = "CARD_CREATE"  # "CHANGE_STATUS", "CHANGE_NAME"

        # Following parametes will be used thread run function
        self.cur_card_number = ""
        self.cur_first_name = ""
        self.cur_last_name = ""
        self.cur_card_status = "A"

        self.cur_address_1 = ""
        self.cur_address_2 = ""
        self.cur_state = ""
        self.cur_zip_code = ""

    def setup_proxy(self):

        if self.proxy_server_info == "":
            self.is_use_proxy = False
            return

        server_info = self.proxy_server_info.strip().split(":")
        proxy_server = server_info[2] + ":" + server_info[3] + "@" + server_info[0] + ":" + server_info[1]
        self.proxies = {
            'http': "http://" + proxy_server,
        }

    def setup_client(self):
        if self.is_use_proxy:
            self.sessions.proxies = self.proxies
            self.wsdl_client = Client(self.wsdl_url, wsse=UsernameToken(self.user_name, self.password),
                                      transport=Transport(session=self.sessions))
        else:
            self.wsdl_client = Client(self.wsdl_url, wsse=UsernameToken(self.user_name, self.password))

    def create_card(self):

        fake = Faker('en_US')
        req_data = {
            'accountCode': self.account_code,
            'customerId': self.customer_id,
            'cardStatus': 'A',
            'cardFirstName': fake.first_name(),
            'cardLastName': fake.last_name(),
            'employeeNumber': FleetCard.get_random_alias(16, "0123456789"),
        }
        card_number = self.NO_DATA
        try:
            response = self.wsdl_client.service.addCardV02(req_data)
            if response['responseCode'] == '00000':
                card_number = response['cardNumber']
        except ZeepWarning:
            print "Failed to create card due to the server problem"

        return card_number

    def get_card_details(self, card_number):
        """
        Get card expiration date
        :param card_number:
        :return:
        """

        req_data = {
            'accountCode': self.account_code,
            'customerId': self.customer_id,
            'cardIdentifierType': 'c',
            'cardIdentifier': card_number,
        }
        print "--------Getting Started Card Details---------------------"
        card_details = self.NO_DATA
        try:
            # MyLogSystem.start_log()
            response = self.wsdl_client.service.inquireCardV02(**req_data)
            card_details = response['cardDetails']
            if self.is_debug:
                print "-------XML Response of get_card_details------"
                for attr, value in response.__dict__.iteritems():
                    print attr, value
        except:
            if self.is_debug:
                trace = sys.exc_info()
                print trace
            print "Server Error while getting card information----------"
        print "--------Getting Card Details Done------------------------"
        return card_details

    def get_security_code(self, card_number, exp_date):

        print "--------Getting CVC Number--------------------"
        cvc_number = self.NO_DATA
        try:
            # MyLogSystem.start_log()
            response = self.wsdl_client.service.inquireCardSecurityCode(accountCode=self.account_code,
                                                                        customerId=self.customer_id,
                                                                        empNumCardNumFlag='c',
                                                                        empNumCardNumValue=card_number,
                                                                        cardExpirationDate=exp_date)
            if self.is_debug:
                print "-------XML Response of get_security_code------"
                for attr, value in response.__dict__.iteritems():
                    print attr, value
            cvc_number = response['cardSecurityCode']
        except Error:
            print "Server Error while getting card CVC information"
        return cvc_number

    def get_card_count(self):
        req_data = {
            'maxRows': 1,
            'pageNumber': 1
        }
        print "--------Getting Started Card Details---------------------"
        page_count = 0
        try:
            # MyLogSystem.start_log()
            response = self.wsdl_client.service.cardListing(**req_data)
            page_count = response['pageCount']
        except:
            if self.is_debug:
                trace = sys.exc_info()
                print trace
            print "Server Error while getting card lists---------------"
        print "--------Getting Card List Done------------------------"
        return page_count

    def get_all_card_list(self):

        total_card_count = self.get_card_count()
        print "Total Card Count:" + str(total_card_count)

        page_count = math.ceil(float(total_card_count) / 10000.0)
        print "--------Getting Started Card Details-------------------------"
        max_rows = 10000
        for page_num in range(0, int(page_count)):

            print (page_num + 1)
            req_data = {
                'maxRows': max_rows,
                'pageNumber': page_num + 1
            }
            try:
                # MyLogSystem.start_log()
                response = self.wsdl_client.service.cardListing(**req_data)
                card_list = response['records']['card']
                for i in range(0, len(card_list)):
                    print "******************************Getting Card Information of " + str(
                        page_num * max_rows + i + 1) + "th************************"
                    with open('all_card_list.txt', 'a') as the_file:
                        card_number = card_list[i]['cardNumber']
                        card_details = self.get_card_details(card_number)
                        card_exp_date = card_details['cardExpiration']
                        cvc_number = self.get_security_code(card_number, card_exp_date)
                        card_first_name = card_list[i]['firstName']
                        card_last_name = card_list[i]['lastName']
                        card_employee_number = card_details['employeeNumber']
                        card_status = card_list[i]['cardStatus']
                        card_info = str(card_number) + ";" + str(cvc_number) + ";" + card_exp_date.strftime('%Y-%m-%d')
                        card_info += ";" + str(card_first_name) + "." + str(card_last_name)
                        card_info += ";" + str(card_employee_number) + ";" + str(card_status) + "\n"

                        the_file.write(card_info)
            except:
                trace = sys.exc_info()
                print trace
                print "Server Error while getting card lists---------------"
        print "--------Getting Card List Done------------------------"

    def create_card_full_process(self):
        print "--------------Creating new card---------------"
        start_time = time.time()
        self.setup_proxy()
        self.setup_client()
        # create a card and get card number
        card_number = self.create_card()
        # get expiration date
        card_details = self.get_card_details(card_number)
        card_exp_date = card_details['cardExpiration']
        # get card CVC number
        cvc_number = self.get_security_code(card_number, card_exp_date)
        with open('output.txt', 'a') as the_file:
            card_info = str(card_number) + ";" + str(cvc_number) + ";" + card_exp_date.strftime('%Y-%m-%d') + "\n"
            the_file.write(card_info)
        print ("--- %s seconds ---" % (time.time() - start_time))
        print "--------------Ended Creating Card---------------"

    def get_cvc_number(self, card_number):
        """
        Get CVC Number By Card Number
        :param card_number:
        :return:
        """
        card_details = self.get_card_details(card_number)
        card_exp_date = card_details['cardExpiration']
        cvc_number = self.get_security_code(card_number, card_exp_date)
        return cvc_number

    def change_card_status(self, card_number, card_status):
        """
        Change Card Status
        :param card_number:
        :param card_status: A = active; B = blocked; C = clear
        :return:
        """
        card_details = self.get_card_details(card_number)
        employee_number = card_details['employeeNumber']
        customer_id = card_details['customerId']
        account_code = card_details['accountCode']
        card_exp_date = card_details['cardExpiration'].strftime('%Y-%m-%d')

        try:
            # MyLogSystem.start_log()
            req_data = {
                'cardIdentifierType': 'c',
                'cardIdentifier': card_number,
                'cardDetails': {
                    'accountCode': account_code,
                    'customerId': customer_id,
                    'employeeNumber': employee_number,
                    'cardStatus': card_status,
                    'cardExpiration': card_exp_date,
                }
            }
            response = self.wsdl_client.service.updateCardV02(**req_data)
            if response['responseCode'] == '00000':
                print "Card Status has been changed as " + card_status
            else:
                print "Card Status has been't changed yet...."

        except:
            if self.is_debug:
                trace = sys.exc_info()
                print trace
            print "Server error during the changing card status due to the request error."

    def delete_card(self, card_number):
        pass

    def change_card_name(self, card_number, first_name, last_name):
        """
        Change Card Number
        :param card_number:
        :param first_name:
        :param last_name:
        :return:
        """
        card_details = self.get_card_details(card_number)
        employee_number = card_details['employeeNumber']
        customer_id = card_details['customerId']
        account_code = card_details['accountCode']
        card_exp_date = card_details['cardExpiration'].strftime('%Y-%m-%d')

        try:
            req_data = {
                'cardIdentifierType': 'c',
                'cardIdentifier': card_number,
                'cardDetails': {
                    'accountCode': account_code,
                    'customerId': customer_id,
                    'employeeNumber': employee_number,
                    'cardFirstName': first_name,
                    'cardLastName': last_name,
                    'cardExpiration': card_exp_date,
                }
            }
            response = self.wsdl_client.service.updateCardV02(**req_data)
            if response['responseCode'] == '00000':
                print "Card Name has been changed as " + first_name + "." + last_name
            else:
                print "Card Name has been't changed yet...."

        except:
            print "Server error during the changing card name due to the request error."
        pass

    def change_card_address(self, card_number, address_1, address_2, state, zip_code):
        """
        Change Card Number
        :param card_number:
        :param first_name:
        :param last_name:
        :return:
        """
        card_details = self.get_card_details(card_number)
        employee_number = card_details['employeeNumber']
        customer_id = card_details['customerId']
        account_code = card_details['accountCode']
        card_exp_date = card_details['cardExpiration'].strftime('%Y-%m-%d')

        try:
            req_data = {
                'cardIdentifierType': 'c',
                'cardIdentifier': card_number,
                'cardDetails': {
                    'accountCode': account_code,
                    'customerId': customer_id,
                    'employeeNumber': employee_number,
                    'cardExpiration': card_exp_date
                },
                'mailingDetails': {
                    'mailAddress1': address_1,
                    'mailAddress2': address_2,
                    'mailState': state,
                    'mailZip': zip_code
                }
            }
            response = self.wsdl_client.service.updateCardV02(**req_data)
            if response['responseCode'] == '00000':
                print "Card address has been changed as " + address_1 + "," + address_2 + "," + state + "," + zip_code
            else:
                print "Card address has been't changed yet...."

        except:
            print "Server error during the changing card address due to the request error."
        pass

    def change_card_status_process(self, card_number, card_status):
        """
        A = active; B = blocked; C = clear
        :param card_number:
        :param card_status:
        :return:
        """
        print "--------------Changing Card status ---------------"
        start_time = time.time()
        self.setup_proxy()
        self.setup_client()
        self.change_card_status(card_number, card_status)
        print ("--- %s seconds ---" % (time.time() - start_time))
        print "--------------Ended Changing Card Status-----------"

    def change_card_name_process(self, card_number, first_name, last_name):
        """
        Change Card Name
        :param card_number:
        :param first_name:
        :param last_name:
        :return:
        """
        print "--------------Changing Card Name ---------------"
        start_time = time.time()
        self.setup_proxy()
        self.setup_client()
        self.change_card_name(card_number, first_name, last_name)
        print ("--- %s seconds ---" % (time.time() - start_time))
        print "--------------Ended Changing Card Name-----------"

    def change_card_address_process(self, card_number, address_1, address_2, state, zip_code):
        """
        Change Card Name
        :param card_number:
        :param first_name:
        :param last_name:
        :return:
        """
        print "--------------Changing Card Address ---------------"
        start_time = time.time()
        self.setup_proxy()
        self.setup_client()
        self.change_card_address(card_number, address_1, address_2, state, zip_code)
        print ("--- %s seconds ---" % (time.time() - start_time))
        print "--------------Ended Changing Card Address-----------"

    @staticmethod
    def get_random_alias(name_length, chars=string.ascii_uppercase + string.digits):

        return ''.join(random.choice(chars) for _ in range(name_length))

    def run(self):

        if self.operation_mode == 'CARD_CREATE':
            self.create_card_full_process()
        elif self.operation_mode == "CHANGE_STATUS":
            # print "-----------------------------------CHANGE_STATUS------------------------------------"
            self.change_card_status_process(self.cur_card_number, self.cur_card_status)
        elif self.operation_mode == 'CHANGE_NAME':
            self.change_card_name_process(self.cur_card_number, self.cur_first_name, self.cur_last_name)
        elif self.operation_mode == 'CHANGE_ADDRESS':
            self.change_card_address_process(self.cur_card_number, self.cur_address_1, self.cur_address_2,
                                             self.cur_state,
                                             self.cur_zip_code)
        else:
            pass


def is_int(s):
    """
    Check s is int or not
    :param s:
    :return:
    """
    try:
        int(s)
        return True
    except ValueError:
        return False


def get_card_old_list():
    fleet_api = FleetCard()
    fleet_api.setup_proxy()
    fleet_api.setup_client()
    fleet_api.is_debug = False
    fleet_api.get_all_card_list()


def get_card_details_info(card_number):
    fleet_api = FleetCard()
    fleet_api.setup_proxy()
    fleet_api.setup_client()
    card_details = fleet_api.get_card_details(card_number)
    print "----------------------"
    for attr, value in card_details.__dict__.iteritems():
        print value
    print "----------------------"


def get_card_cvc_number_test(card_number):
    fleet_api = FleetCard()
    fleet_api.setup_proxy()
    fleet_api.setup_client()
    card_cvc = fleet_api.get_cvc_number(card_number)
    print "----------------------"
    print "card cvc number:" + str(card_cvc)
    print "----------------------"


def create_ghost_card(card_count):
    print "will create new card " + str(card_count)

    for num in range(0, card_count):
        try:
            fleet_api_thread = FleetCard()
            fleet_api_thread.operation_mode = 'CARD_CREATE'
            fleet_api_thread.start()
        except:
            print "Found an warning creating new thread..."
            num = num - 1
        time.sleep(2)


def change_ghost_card_status():
    print "will change card status"
    card_list_reader = CardListReader()
    card_list_reader.get_card_status_change_list()
    thread_count = len(card_list_reader.change_status_list)
    for num in range(0, thread_count):
        try:
            fleet_api_thread = FleetCard()
            fleet_api_thread.operation_mode = 'CHANGE_STATUS'
            fleet_api_thread.cur_card_number = card_list_reader.change_status_list[num]['card_number']
            fleet_api_thread.cur_card_status = card_list_reader.change_status_list[num]['status']
            fleet_api_thread.start()
        except:
            print "Found an warning creating new thread..."
            num = num - 1
        time.sleep(2)


def change_ghost_card_name():
    print "will change card name"
    card_list_reader = CardListReader()
    card_list_reader.get_card_name_change_list()
    thread_count = len(card_list_reader.change_name_list)
    for num in range(0, thread_count):
        try:
            fleet_api_thread = FleetCard()
            fleet_api_thread.operation_mode = 'CHANGE_NAME'
            fleet_api_thread.cur_card_number = card_list_reader.change_name_list[num]['card_number']
            fleet_api_thread.cur_first_name = card_list_reader.change_name_list[num]['first_name']
            fleet_api_thread.cur_last_name = card_list_reader.change_name_list[num]['last_name']
            fleet_api_thread.start()
        except:
            print "Found an warning creating new thread..."
            num = num - 1
        time.sleep(2)


def change_ghost_card_address():
    print "will change card Address"
    card_list_reader = CardListReader()
    card_list_reader.get_card_address_change_list()
    thread_count = len(card_list_reader.change_address_list)
    for num in range(0, thread_count):
        try:
            fleet_api_thread = FleetCard()
            fleet_api_thread.operation_mode = 'CHANGE_ADDRESS'
            fleet_api_thread.cur_card_number = card_list_reader.change_address_list[num]['card_number']
            fleet_api_thread.cur_address_1 = card_list_reader.change_address_list[num]['mailAddress1']
            fleet_api_thread.cur_address_2 = card_list_reader.change_address_list[num]['mailAddress2']
            fleet_api_thread.cur_state = card_list_reader.change_address_list[num]['mailState']
            fleet_api_thread.cur_zip_code = card_list_reader.change_address_list[num]['mailZip']
            fleet_api_thread.start()
        except:
            print "Found an warning creating new thread..."
            num = num - 1
        time.sleep(2)


def main():
    sys_argv = sys.argv
    if len(sys_argv) < 2:
        print "\nPlease enter options to adjust cards like following:\n"
        print "-Create Cards                    python main.py -create [count]"
        print "-Change Card Status              python main.py -change-status"
        print "-Change Card Name                python main.py -change-name"
        print "-Change Card Address Info        python main.py -change-address"
        print "-Get Card CVC                    python main.py -get-card-cvc  [cardNumber]"
        print "-Get Card Information            python main.py -get-card-info [cardNumber]"
        print "-Get Card List                   python main.py -get-card-list"
        return
    if sys_argv[1] == '-create':
        print "creating cards..............................."
        if len(sys_argv) == 3:
            card_count = sys_argv[2]
            if not is_int(card_count):
                print "Please enter valid count"
                return
            create_ghost_card(int(float(card_count)))
        else:
            print "Invalid create command."
            print "Please remember <python main.py -create [count]>"
            return
    elif sys_argv[1] == '-change-status':
        change_ghost_card_status()
    elif sys_argv[1] == '-change-name':
        change_ghost_card_name()
    elif sys_argv[1] == '-change-address':
        change_ghost_card_address()
    elif sys_argv[1] == '-get-card-info':
        if len(sys_argv) == 3:
            card_number = sys_argv[2]
            if not is_int(card_number):
                print "Please enter valid card number"
                return
            get_card_details_info(card_number)
        else:
            print "Invalid get card information command."
            print "Please remember <python main.py -get-card-info [card_number]>"
            return
    elif sys_argv[1] == '-get-card-list':
        get_card_old_list()
    elif sys_argv[1] == '-get-card-cvc':
        if len(sys_argv) == 3:
            card_number = sys_argv[2]
            if not is_int(card_number):
                print "Please enter valid card number"
                return
            get_card_cvc_number_test(card_number)
        else:
            print "Invalid Get CVC Number Command."
            print "Please remember <python main.py -get-card-cvc  [cardNumber]"
            return
    else:
        print "Unrecognized command."


if __name__ == "__main__":
    main()
