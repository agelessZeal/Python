import traceback

import requests
import json, string, random, time, threading, sys
from configparser import SafeConfigParser


class ProxyFileManage:
    def __init__(self):
        self.proxy_list = []
        self.delete_list = []

    def get_proxies(self):
        """
        Init proxy list
        :return:
        """
        with open("proxy_list.txt", 'r') as fs:
            try:
                for line in fs:
                    serverInfo = line.strip().split(":")
                    if len(serverInfo) == 4:
                        proxy_str = serverInfo[2] + ":" + serverInfo[3] + "@" + serverInfo[0] + ":" + serverInfo[1]
                        self.proxy_list.append(proxy_str)
                    else:
                        print "Missing some of information at proxy_list file"

            except:  # whatever reader errors you care about
                print "Can not proxy_list.txt file"

    def get_random_proxy(self):
        """
        Get random proxy from proxy list
        :return:
        """
        tmp_proxy_list = ""
        if len(self.proxy_list) > 0:
            tmp_proxy_list = random.choice(self.proxy_list)
        return tmp_proxy_list

    def get_card_count(self):

        safe_conf = SafeConfigParser()
        safe_conf.read('config.ini')
        card_count = safe_conf.get('setting', 'cardNum')
        return int(card_count)

    def get_delete_card_list(self):
        """
        Function is to return delete card list
        :return: delete card list
        """
        with open("delete_list.txt", 'r') as fs:
            try:
                for line in fs:
                    card_id = line.strip()
                    self.delete_list.append(card_id)
            except:  # whatever reader errors you care about
                print "Can not find delete_list.txt file"


class BentoVCard(threading.Thread):
    def __init__(self):

        threading.Thread.__init__(self)

        self.access_token = ""

        self.config = SafeConfigParser()
        self.config.read('config.ini')

        self.access_key = self.config.get('setting', 'accessKey')
        self.secret_key = self.config.get('setting', 'secretKey')
        self.base_api_url = self.config.get('setting', 'baseURL')

        self.expiration = self.config.get('setting', 'expiration')  # 5 month and 22 years

        self.amount = 5000  # this is maximum of amount we can set...,,, max amount  = 25000

        self.proxy_list = []

        self.rand_proxy_server = ""
        self.card_pan = ""

        self.proxies = {
            'http': '',
        }

        self.reqs = requests.Session()

        self.tested_exp = ""

        self.is_use_proxy = 1

        self.card_number = ""

        # get default billing address
        self.addressType = self.config.get('billing_address', 'addressType')
        self.city = self.config.get('billing_address', 'city')
        self.state = self.config.get('billing_address', 'state')
        self.street = self.config.get('billing_address', 'street')
        self.zipCode = self.config.get('billing_address', 'zipCode')

        self.NOTE_MESSAGE = "it may take up to 5 minutes for the card billing address to take effect once you change " \
                            "it in the API. Please give it sufficient time after it is set before attempting to make " \
                            "purchases with the billing address you have set. Otherwise, your purchase may decline due " \
                            "to address mismatch."

        self.SERVER_ERROR_MSG = "SERVER_ERROR"

    def setup_proxies(self, proxy_server):

        self.proxies = {
            'http': "http://" + proxy_server,
        }

        self.reqs.proxies = self.proxies

    def get_access_token(self):
        """Generates a Bearer token that must be passed through any authenticated routes.
        This is valid for one hour and must be renewed to prevent 401 - Unauthorized errors.
        https://apidocs.bentoforbusiness.com/?python#login
        :return:
        """

        headers = {
            'Content-Type': 'application/json'
        }
        params = {
            "accessKey": self.access_key,
            "secretKey": self.secret_key
        }
        post_url = self.base_api_url + "/sessions"

        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.post(post_url, data=json.dumps(params), headers=headers)
            else:
                resp = requests.post(post_url, data=json.dumps(params), headers=headers)
            if resp.status_code == 200:  # server works correctly...
                self.access_token = resp.headers['Authorization']
            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 403 or resp.status_code == 404:
                print "Failed to get_access_token due to the invalid request parameter"
                self.access_token = self.SERVER_ERROR_MSG
            if resp.status_code == 500:
                print "SERVER ERROR" + "at get_access_token function"
                self.access_token = self.SERVER_ERROR_MSG
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print e
            # catastrophic error. bail.
            # print e ## maybe proxy server error, therefore we will change proxy server....
            self.is_use_proxy = 0
            print "Request Error at the during get_access_token"
            print "Proxy not working well, so we will use local machine"

    def create_virtual_card(self):
        """ Creates a new card object
        https://apidocs.bentoforbusiness.com/?python#create-a-new-card
        :return:
        """
        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return self.SERVER_ERROR_MSG

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.access_token,
        }

        spendinglimit = {
            "active": "true",
            "amount": self.amount,
            "period": "Day",
        }
        params = {
            "type": "CategoryCard",
            "alias": BentoVCard.get_random_alias(5),
            # "lifecycleStatus": "ACTIVATED",
            # "status": "TURNED_ON",
            "virtualCard": "true",
            "allowedDaysActive": "true",
            "expiration": self.expiration,
            "spendingLimit": spendinglimit
        }

        print "Creating Card Id......"
        post_url = self.base_api_url + "/cards"
        card_id = "NO_DATA"
        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.post(post_url, data=json.dumps(params), headers=headers)
            else:
                resp = requests.post(post_url, data=json.dumps(params), headers=headers)
            if resp.status_code == 201 or resp.status_code == 200:
                json_load = resp.json()
                card_id = json_load["cardId"]
            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 404:  # bad request
                json_load = resp.json()
                print "Failed to create card due to the invalid request parameter"
                print json_load["message"]
            if resp.status_code == 500:
                print self.SERVER_ERROR_MSG + " at create_virtual_card function"
                card_id = self.SERVER_ERROR_MSG

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            print "Request Error at the during of create_virtual_card function"

        return card_id

    def update_virtual_card(self, card_id, expiration="0522"):
        """
        Updates the specified card by setting the value of the parameters passed.
        This request accepts the same arguments as the card creation and get card calls.
        :param card_id:
        :param expiration:
        :return:
        """
        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.access_token,
        }

        spendinglimit = {
            "active": "true",
            "amount": self.amount,
            "period": "Day",
        }
        params = {
            "type": "CategoryCard",
            "alias": BentoVCard.get_random_alias(5),
            # "lifecycleStatus": "ACTIVATED",
            # "status": "TURNED_ON",
            "virtualCard": "true",
            "allowedDaysActive": "true",
            "expiration": expiration,
            "spendingLimit": spendinglimit
        }

        print "Updating Card Information......"
        put_url = self.base_api_url + "/cards/" + str(card_id)
        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.put(put_url, data=json.dumps(params), headers=headers, proxies=self.proxies)
            else:
                resp = requests.put(put_url, data=json.dumps(params), headers=headers)
            print params
            if resp.status_code == 201 or resp.status_code == 200:
                json_load = resp.json()
                for keys in json_load.iterkeys():
                    if keys == u"expiration":
                        print "Card expiration updated"
                        print json_load[keys]
            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 403 or resp.status_code == 404:
                json_load = resp.json()
                print "Failed to update card due to the invalid request parameter"
                print json_load["message"]
            if resp.status_code == 500:
                print self.SERVER_ERROR_MSG + " at update_virtual_card function"
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            print "Request Error at the during of update_virtual_card function"

    def get_card_status(self, card_id):
        """
        Get card status (lifecycleStatus ->NOT_ISSUED_YET->NEVER_ACTIVATED)
        :param card_id:
        :return:
        """
        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return self.SERVER_ERROR_MSG

        headers = {
            'Authorization': self.access_token
        }

        time.sleep(3)

        life_status = ""
        get_url = self.base_api_url + "/cards/" + str(card_id)
        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.get(get_url, headers=headers)
            else:
                resp = requests.get(get_url, headers=headers)
            if resp.status_code == 200:
                json_load = resp.json()
                life_status = json_load["lifecycleStatus"]
                for keys in json_load.iterkeys():
                    if keys == u"expiration":
                        self.expiration = json_load[keys]

            if resp.status_code == 500:
                life_status = self.SERVER_ERROR_MSG

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            life_status = self.SERVER_ERROR_MSG
            print "Request Error at the during of get_card_status function"

        return life_status

    def get_card_full_info(self, card_id):
        """
        Get card full Info
        :param card_id:
        :return:
        """
        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return self.SERVER_ERROR_MSG

        headers = {
            'Authorization': self.access_token
        }

        card_full_info = "NO_DATA"
        get_url = self.base_api_url + "/cards/" + str(card_id)
        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.get(get_url, headers=headers)
            else:
                resp = requests.get(get_url, headers=headers)
            if resp.status_code == 200:
                json_load = resp.json()
                card_full_info = ""
                for keys in json_load.iterkeys():
                    card_full_info += "\n" + str(keys) + ":" + str(json_load[keys])

            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 403 or resp.status_code == 404:
                print "Failed to get_card_full_info  due to the invalid request parameter"
                print resp.content.decode()
            if resp.status_code == 500:
                card_full_info = self.SERVER_ERROR_MSG

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            print "Request Error at the during of get_card_status function"

        return card_full_info

    def activate_card(self, card_id):
        """
        You must first activate the card before you can start to use this card. Activation is a one-time operation
        https://apidocs.bentoforbusiness.com/?python#activate-a-card
        :param card_id:
        :return:
        """
        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return
        card_str = str(card_id)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.access_token,
        }
        params = {
            "lastFour": self.card_pan[-4:]
        }

        print "Activating Card Id......"
        post_url = self.base_api_url + "/cards/" + card_str + "/activation"

        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.post(post_url, data=json.dumps(params), headers=headers)
            else:
                resp = requests.post(post_url, data=json.dumps(params), headers=headers)
            if resp.status_code == 201 or resp.status_code == 200:
                print "Processing of Activation..."
            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 403 or resp.status_code == 404:
                json_load = resp.json()
                print "Failed to get_card_full_info  due to the invalid request parameter"
                print json_load
            if resp.status_code == 500:
                print self.SERVER_ERROR_MSG + " at activate_card function"
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            print "Request Error at the during of activate_card function"

    def delete_card(self, card_id):
        """Permanently deletes the specified card from our system and
        card can no longer be used. It cannot be und
        NowNone.
        https://apidocs.bentoforbusiness.com/?python#delete-a-card
        :param card_id:
        :return:
        """
        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return

        card_str = str(card_id)
        headers = {
            'Authorization': self.access_token,
        }

        print "Deleting Card Id......"
        post_url = self.base_api_url + "/cards/" + card_str

        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.delete(post_url, headers=headers)
            else:
                resp = requests.delete(post_url, headers=headers)

            if resp.status_code == 201 or resp.status_code == 200:
                print "Processing of Deleting..."
                print "Done Processing of Deleting"
            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 403 or resp.status_code == 404:
                json_load = resp.json()
                print "Failed to delete_card  due to the invalid request parameter"
                print json_load
            if resp.status_code == 500:
                print self.SERVER_ERROR_MSG + " at delete_card function"
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            print "Request Error at the during of delete_card function"

    def get_card_list(self):
        """Returns a server-side page of cards from the current business.
        """
        pass

    def get_billing_address(self, card_id):
        """Retrieves the billing address for the specified card.
        https://apidocs.bentoforbusiness.com/?python#retrieve-a-card-39-s-billing-address
        :param card_id:
        :return:
        """
        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return self.SERVER_ERROR_MSG
        card_str = str(card_id)
        headers = {
            'Authorization': self.access_token,
        }
        params = {
        }

        print "Retrieving Billing Address of Card Id......"
        get_url = self.base_api_url + "/cards/" + card_str + "/billingaddress"
        billing_address = "NO_DATA"
        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.get(get_url, data=json.dumps(params), headers=headers)
            else:
                resp = requests.get(get_url, data=json.dumps(params), headers=headers)
            print self.access_token
            if resp.status_code == 201 or resp.status_code == 200:
                print "Processing of Retrieving..."
                load_json = resp.json()
                key_order = 0
                for key, value in load_json.items():
                    if key_order == 0:
                        billing_address += key + ":" + str(value)
                        key_order = 1
                    else:
                        billing_address += ";" + key + ":" + str(value)

                print "Done Processing of Retrieving..."
            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 403 or resp.status_code == 404:
                json_load = resp.json()
                print "Failed to get_billing_address  due to the invalid request parameter"
                print json_load
            if resp.status_code == 500:
                billing_address = self.SERVER_ERROR_MSG

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            print "Request Error at the during of retrieving of billing information function"
        return billing_address

    def create_billing_address(self, card_id, is_create=True, b_city="San Francisco", b_state="CA",
                               b_street="123 Main Street", b_zipcode="94123"):
        """ Creates a new billing address for the specified card
        https://apidocs.bentoforbusiness.com/?python#create-a-card-39-s-billing-address
        Please note: it may take up to 5 minutes for the card billing address to take effect once you change it
        in the API.  Please give it sufficient time after it is set before attempting to make purchases with the
        billing address you have set. Otherwise, your purchase may decline due to address mismatch.
        :param card_id:
        :return:
        """
        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return self.SERVER_ERROR_MSG

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.access_token
        }

        if is_create:
            params = {
                "active": "true",
                "addressType": b_city,
                "city": self.city,
                # "id": 1,
                "state": self.state,
                "street": self.street,
                "zipCode": self.zipCode
            }
        else:
            params = {
                "active": "true",
                "addressType": self.addressType,
                "city": b_city,
                # "id": 1,
                "state": b_state,
                "street": b_street,
                "zipCode": b_zipcode
            }
        post_url = self.base_api_url + "/cards/" + str(card_id) + "/billingaddress"
        billing_address = "NO_DATA"
        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.post(post_url, data=json.dumps(params), headers=headers)
            else:
                resp = requests.post(post_url, data=json.dumps(params), headers=headers)
            if resp.status_code == 200:
                json_load = resp.json()
                print "Creating Billing Address.."
                print self.NOTE_MESSAGE
                key_order = 0
                for key, value in json_load.items():
                    if key_order == 0:
                        billing_address += key + ":" + str(value)
                        key_order = 1
                    else:
                        billing_address += ";" + key + ":" + str(value)
            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 403 or resp.status_code == 404:
                print "Failed Creating Billing Address due to the invalid request"
            if resp.status_code == 500:
                billing_address = self.SERVER_ERROR_MSG

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            print "Request Error at the during of create_billing_address function"
        return billing_address

    def update_billing_address(self, card_id, b_city, b_state, b_street, b_zipcode):
        """ Updates the card's existing billing address if one exists
        https://apidocs.bentoforbusiness.com/?python#create-a-card-39-s-billing-address
        :param card_id:
        :return:
        """
        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return self.SERVER_ERROR_MSG

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.access_token
        }

        params = {
            "active": "true",
            "addressType": self.addressType,
            "city": b_city,
            # "id": 1,
            "state": b_state,
            "street": b_street,
            "zipCode": b_zipcode
        }

        put_url = self.base_api_url + "/cards/" + str(card_id) + "/billingaddress"

        billing_address = "NO_DATA"
        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.put(put_url, data=json.dumps(params), headers=headers)
            else:
                resp = requests.put(put_url, data=json.dumps(params), headers=headers)
            if resp.status_code == 200:
                json_load = resp.json()
                # print json_load
                print "Updating Billing Address.."
                print self.NOTE_MESSAGE
                key_order = 0
                for key, value in json_load.items():
                    if key_order == 0:
                        billing_address += key + ":" + str(value)
                        key_order = 1
                    else:
                        billing_address += ";" + key + ":" + str(value)
            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 403 or resp.status_code == 404:
                print "Failed Updating Billing Address due to the invalid request parameter"
            if resp.status_code == 500:
                billing_address = self.SERVER_ERROR_MSG

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            print "Request Error at the during of update_billing_address function"
        return billing_address

    def get_cvc_number(self, card_id):  # Retrieves the specified card's Primary Account Number (PAN) and CVV.

        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return self.SERVER_ERROR_MSG
        headers = {
            'Authorization': self.access_token
        }

        cvv = "NO_DATA"
        get_url = self.base_api_url + "/cards/" + str(card_id) + "/pan"
        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.get(get_url, headers=headers)
            else:
                resp = requests.get(get_url, headers=headers)
            if resp.status_code == 200:
                json_load = resp.json()
                cvv = json_load["cvv"]
                self.card_pan = json_load["pan"]
                self.card_number = json_load["pan"]
            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 403 or resp.status_code == 404:
                print "Failed to get_cvc_number due to the invalid request parameter"
            if resp.status_code == 500:
                cvv = self.SERVER_ERROR_MSG
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            print "Request Error at the during of get_cvc_number function"
        return cvv

    def run(self):

        print "----------------------Started-----------------------------"
        start_time = time.time()
        self.get_access_token()
        time.sleep(7)
        card_id = self.create_virtual_card()

        if card_id == "NO_DATA" or card_id == self.SERVER_ERROR_MSG:
            return

        # checking card validation to cvc
        life_status = "NOT_ISSUED_YET"
        while life_status == "NOT_ISSUED_YET":
            life_status = self.get_card_status(card_id)

        if life_status == self.SERVER_ERROR_MSG:
            print "API didn't changed card status from NOT_ISSUED_YET to NEVER_ACTIVATED! due to the some reason."
            print "Please contact server support about that."
            return

        cvc = ""
        while cvc == "":
            cvc = self.get_cvc_number(card_id)
            if cvc == self.SERVER_ERROR_MSG:
                return
        print ("--- %s seconds ---" % (time.time() - start_time))

        # Activation of Card
        self.activate_card(card_id)

        billing_address = self.create_billing_address(card_id)
        if billing_address == self.SERVER_ERROR_MSG:
            return

        with open('output.txt', 'a') as the_file:
            card_info = str(card_id) + ";" + str(self.card_number) + ";" + cvc + ";" + self.convert_expiration() + "\n"
            the_file.write(card_info)
        print "----------------------Ended-----------------------------"

    def convert_expiration(self):
        tmp_str = list(self.expiration)
        return "20" + tmp_str[2] + tmp_str[3] + ":" + tmp_str[0] + tmp_str[1]

    @staticmethod
    def get_random_alias(name_length, chars=string.ascii_uppercase + string.digits):

        return ''.join(random.choice(chars) for _ in range(name_length))


class BentoVCardDelete(threading.Thread):
    def __init__(self):

        threading.Thread.__init__(self)

        self.access_token = ""

        self.config = SafeConfigParser()
        self.config.read('config.ini')

        self.access_key = self.config.get('setting', 'accessKey')
        self.secret_key = self.config.get('setting', 'secretKey')
        self.base_api_url = self.config.get('setting', 'baseURL')

        self.proxy_list = []

        self.rand_proxy_server = ""

        self.proxies = {
            'http': '',
        }

        self.reqs = requests.Session()

        self.is_use_proxy = 1

        self.SERVER_ERROR_MSG = "SERVER_ERROR"

        self.delete_card_id = ""

    def setup_proxies(self, proxy_server):

        self.proxies = {
            'http': "http://" + proxy_server,
        }

        self.reqs.proxies = self.proxies

    def get_access_token(self):
        """Generates a Bearer token that must be passed through any authenticated routes.
        This is valid for one hour and must be renewed to prevent 401 - Unauthorized errors.
        https://apidocs.bentoforbusiness.com/?python#login
        :return:
        """

        headers = {
            'Content-Type': 'application/json'
        }
        params = {
            "accessKey": self.access_key,
            "secretKey": self.secret_key
        }
        post_url = self.base_api_url + "/sessions"

        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.post(post_url, data=json.dumps(params), headers=headers)
            else:
                resp = requests.post(post_url, data=json.dumps(params), headers=headers)
            if resp.status_code == 200:  # server works correctly...
                self.access_token = resp.headers['Authorization']
            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 403 or resp.status_code == 404:
                print "Failed to get_access_token due to the invalid request parameter"
                self.access_token = self.SERVER_ERROR_MSG
            if resp.status_code == 500:
                print "SERVER ERROR" + "at get_access_token function"
                self.access_token = self.SERVER_ERROR_MSG
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print e
            # catastrophic error. bail.
            # print e ## maybe proxy server error, therefore we will change proxy server....
            self.is_use_proxy = 0
            print "Request Error at the during get_access_token"
            print "Proxy not working well, so we will use local machine"

    def get_card_status(self, card_id):
        """
        Get card status (lifecycleStatus ->NOT_ISSUED_YET->NEVER_ACTIVATED)
        :param card_id:
        :return:
        """
        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return self.SERVER_ERROR_MSG

        headers = {
            'Authorization': self.access_token
        }

        life_status = ""
        get_url = self.base_api_url + "/cards/" + str(card_id)
        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.get(get_url, headers=headers)
            else:
                resp = requests.get(get_url, headers=headers)
            if resp.status_code == 200:
                json_load = resp.json()
                life_status = json_load["lifecycleStatus"]
            if resp.status_code == 500:
                life_status = self.SERVER_ERROR_MSG

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            print "Request Error at the during of get_card_status function"

        return life_status

    def get_card_full_info(self, card_id):
        """
        Get card full Info
        :param card_id:
        :return:
        """
        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return self.SERVER_ERROR_MSG

        headers = {
            'Authorization': self.access_token
        }

        card_full_info = "NO_DATA"
        get_url = self.base_api_url + "/cards/" + str(card_id)
        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.get(get_url, headers=headers)
            else:
                resp = requests.get(get_url, headers=headers)
            if resp.status_code == 200:
                json_load = resp.json()
                for keys in json_load.iterkeys():
                    card_full_info += "\n" + str(keys) + ":" + str(json_load[keys])
            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 403 or resp.status_code == 404:
                print "Failed to get_card_full_info  due to the invalid request parameter"
            if resp.status_code == 500:
                card_full_info = self.SERVER_ERROR_MSG

        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            print "Request Error at the during of get_card_status function"

        return card_full_info

    def delete_card(self, card_id):
        """Permanently deletes the specified card from our system and
        card can no longer be used. It cannot be und
        NowNone.
        https://apidocs.bentoforbusiness.com/?python#delete-a-card
        :param card_id:
        :return:
        """
        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return

        card_str = str(card_id)
        headers = {
            'Authorization': self.access_token,
        }

        print "Deleting Card Id......"
        post_url = self.base_api_url + "/cards/" + card_str

        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.delete(post_url, headers=headers)
            else:
                resp = requests.delete(post_url, headers=headers)

            if resp.status_code == 201 or resp.status_code == 200:
                print "Processing of Deleting..."
                print "Done Processing of Deleting"
            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 403 or resp.status_code == 404:
                json_load = resp.json()
                print "Failed to delete_card  due to the invalid request parameter"
                print json_load
            if resp.status_code == 500:
                print self.SERVER_ERROR_MSG + " at delete_card function"
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            print "Request Error at the during of delete_card function"

    def get_card_list(self):
        """Returns a server-side page of cards from the current business.
        """
        pass

    def get_cvc_number(self, card_id):  # Retrieves the specified card's Primary Account Number (PAN) and CVV.

        if self.access_token == "" or self.access_token == self.SERVER_ERROR_MSG:
            print "Access Token Invalid"
            return self.SERVER_ERROR_MSG
        headers = {
            'Authorization': self.access_token
        }

        cvv = "NO_DATA"
        get_url = self.base_api_url + "/cards/" + str(card_id) + "/pan"
        try:
            if self.is_use_proxy == 1:
                resp = self.reqs.get(get_url, headers=headers)
            else:
                resp = requests.get(get_url, headers=headers)
            if resp.status_code == 200:
                json_load = resp.json()
                cvv = json_load["cvv"]
                self.card_pan = json_load["pan"]
                self.card_number = json_load["pan"]
            if resp.status_code == 400 or resp.status_code == 401 or resp.status_code == 403 or resp.status_code == 404:
                print "Failed to get_cvc_number due to the invalid request parameter"
            if resp.status_code == 500:
                cvv = self.SERVER_ERROR_MSG
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            # catastrophic error. bail.
            print "Request Error at the during of get_cvc_number function"
        return cvv

    def run(self):

        print "----------------------Deleting Started-----------------------------"
        start_time = time.time()
        self.get_access_token()
        time.sleep(7)
        self.delete_card(self.delete_card_id)
        print ("--- %s seconds ---" % (time.time() - start_time))
        print "----------------------Deleting Ended-----------------------------"


def create_card_test():
    threads = []
    prx_manage = ProxyFileManage()
    thread_count = prx_manage.get_card_count()
    prx_manage.get_proxies()
    for num in range(0, thread_count):
        try:
            bento_api_thread = BentoVCard()
            print "Starting API Thread"
            tmp_proxy = ""
            if len(prx_manage.proxy_list) == 0:
                bento_api_thread.is_use_proxy = 0
            else:
                tmp_proxy = prx_manage.get_random_proxy()
                bento_api_thread.setup_proxies(tmp_proxy)
                bento_api_thread.is_use_proxy = 1

            if len(tmp_proxy) != 0:
                prx_manage.proxy_list.remove(tmp_proxy)
                print len(prx_manage.proxy_list)
            bento_api_thread.start()
            threads.append(bento_api_thread)
            time.sleep(5)
        except:
            thread_count = thread_count + 1


def delete_card_test(card_id):
    bento_api_thread = BentoVCard()
    bento_api_thread.is_use_proxy = 0
    bento_api_thread.get_access_token()
    bento_api_thread.delete_card(card_id)


def delete_card_list_test():
    threads = []
    prx_manage = ProxyFileManage()
    prx_manage.get_delete_card_list()
    thread_count = len(prx_manage.delete_list)
    print thread_count
    prx_manage.get_proxies()

    prev_delete_status = True
    for num in range(0, thread_count):
        try:
            bento_api_thread = BentoVCardDelete()
            print "Starting API Thread to delect Card"
            tmp_proxy = ""
            if len(prx_manage.proxy_list) == 0:
                bento_api_thread.is_use_proxy = 0
            else:
                tmp_proxy = prx_manage.get_random_proxy()
                bento_api_thread.setup_proxies(tmp_proxy)
                bento_api_thread.is_use_proxy = 1

            if len(tmp_proxy) != 0:
                prx_manage.proxy_list.remove(tmp_proxy)
                print len(prx_manage.proxy_list)
            time.sleep(5)
            if prev_delete_status:
                bento_api_thread.delete_card_id = prx_manage.delete_list[num]
            else:
                bento_api_thread.delete_card_id = prx_manage.delete_list[num - 1]
            bento_api_thread.start()
            threads.append(bento_api_thread)
            prev_delete_status = True
        except:
            thread_count = thread_count + 1
            prev_delete_status = False


def get_card_info_test(card_id):
    bento_api_thread = BentoVCard()
    bento_api_thread.is_use_proxy = 0
    bento_api_thread.get_access_token()
    card_full_info = bento_api_thread.get_card_full_info(card_id)
    print card_full_info


def update_card_expiration_test(card_id, expiration):
    bento_api_thread = BentoVCard()
    bento_api_thread.is_use_proxy = 0
    bento_api_thread.get_access_token()
    bento_api_thread.update_virtual_card(card_id, expiration)


def get_billing_address_test(card_id):
    bento_api_thread = BentoVCard()
    bento_api_thread.is_use_proxy = 0
    bento_api_thread.get_access_token()
    billing_address = bento_api_thread.get_billing_address(card_id)
    print billing_address


def create_billing_address_test(card_id):
    bento_api_thread = BentoVCard()
    bento_api_thread.is_use_proxy = 0
    bento_api_thread.get_access_token()
    bento_api_thread.create_billing_address(card_id)


def update_billing_address_test(card_id, b_city="San Francisco", b_state="CA", b_street="123 Main Street",
                                b_zipcode="94123"):
    bento_api_thread = BentoVCard()
    bento_api_thread.is_use_proxy = 0
    bento_api_thread.get_access_token()
    billing_address = bento_api_thread.get_billing_address(card_id)
    if billing_address != "NO_DATA":
        api_res = bento_api_thread.update_billing_address(card_id, b_city, b_state, b_street, b_zipcode)
        print "Updated address is " + api_res

    else:
        api_res = bento_api_thread.create_billing_address(card_id, False, b_city, b_state, b_street, b_zipcode)
        print "Created address is " + api_res


def active_card_test(card_id):
    bento_api_thread = BentoVCard()
    bento_api_thread.is_use_proxy = 0
    bento_api_thread.get_access_token()
    bento_api_thread.get_cvc_number(card_id)
    bento_api_thread.activate_card(card_id)


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


def is_expiration_date(s):
    """
    Check validation of expiration date
    :param s:
    :return:
    """
    if len(s) != 4 or (not s.isdigit()):
        return False
    mm = int(s[:2])
    yy = int(s[-2:])
    if mm > 12 or yy < 18:
        return False
    return True


def main():
    sys_argv = sys.argv

    if len(sys_argv) < 2:
        print "\nPlease enter options to adjust cards like following:\n"
        print "-Create cards          python main.py -create"
        print "-Delete card           python main.py -delete [cardId]"
        print "-Change expiration     python main.py -change-expiration [cardId] [ExpirationDate(Format is MMYY)]"
        print "-Change billing        python main.py -change-billing [cardId] [city] [state] [street] [zipcode]"
        print "-Delete card list      python main.py -delete-card-list"
        return
    if sys_argv[1] == '-create':
        print "creating cards..............................."
        create_card_test()

    elif sys_argv[1] == '-delete':

        if len(sys_argv) == 3:
            card_id = sys_argv[2]
            if not is_int(card_id):
                print "Please enter valid card Id"
                return
            delete_card_test(card_id)
        else:
            print "Invalid delete command."
            print "Please remember <main.py -delete [cardId]>"
            return

    elif sys_argv[1] == '-change-expiration':
        if len(sys_argv) == 4:
            card_id = sys_argv[2]
            exp_date = sys_argv[3]
            if not is_int(card_id):
                print "Please enter valid cardId"
                return
            if not is_expiration_date(exp_date):
                print "Please enter valid expiration date, expiration date is MMYY."
                return
            print "changing expiration date........................."
            update_card_expiration_test(card_id, exp_date)
        else:
            print "Invalid -change-expiration command."
            print "Please remember <main.py -change-expiration [cardId] [ExpirationDate(Format is MMYY)]>"
            return
    elif sys_argv[1] == '-change-billing':
        if len(sys_argv) == 7:
            card_id = sys_argv[2]
            if not is_int(card_id):
                print "Please enter valid cardId"
                return
            city = sys_argv[3]
            state = sys_argv[4]
            street = sys_argv[5]
            zipcode = sys_argv[6]
            if len(city) == 0 or len(state) == 0 or len(street) == 0 or (not zipcode.isdigit()):
                print "Some parameters is invalid value"
                return
            print "changing billing information......................"
            update_billing_address_test(card_id, city, state, street, zipcode)
        else:
            print "Invalid -change-billing command."
            print "Please remember <main.py -change-billing [cardId] [city] [state] [street] [zipcode]>"
            return
    elif sys_argv[1] == "-get-billing-info":
        if len(sys_argv) == 3:
            card_id = sys_argv[2]
            if not is_int(card_id):
                print "Please enter valid card Id"
                return
            get_billing_address_test(card_id)  # 6252
        else:
            print "Invalid get-billing-info command."
            return
    elif sys_argv[1] == '-get-card-info':
        if len(sys_argv) == 3:
            card_id = sys_argv[2]
            if not is_int(card_id):
                print "Please enter valid card Id"
                return
            get_card_info_test(card_id)  # 6252
        else:
            print "Invalid get-card-info command."
            return
    elif sys_argv[1] == '-delete-card-list':
        delete_card_list_test()
    else:
        print "Unrecognized commands"


# active_card_test(9250) #,8636, 6252,
# create_billing_address_test(6252)
# get_billing_address_test(6252)
# update_billing_address_test(9250, "NewYork")



if __name__ == "__main__":
    main()
