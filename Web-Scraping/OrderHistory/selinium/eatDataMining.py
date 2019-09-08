from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from threading import Timer
from configparser import SafeConfigParser
from random import randint
import thread
import pymysql as pm
import random, string
import os, fnmatch, sys, time, csv, urllib2, math
import datetime as dt

from Tkinter import *
import Tkinter
from tkintertable import TableCanvas, TableModel

for testIndexII in range(0, 4):
    print ("this is test range" + str(testIndexII))

#
# web scraping code*****************************************************************************************************
#
# Read config.ini

# ********************************************database manage*****************************************************#
pm.install_as_MySQLdb()

conn = None

try:
    conn = pm.connect(host='127.0.0.1', user='root', passwd='root', db='webscraping')
    print("Database Connected")
except:
    print("I am unable to connect to the database")


def deleteOrderFromDB(query):
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()


def saveOrderToDB(order_no,
                  order_date, order_time, paid_status,
                  total_pdt, total_price,
                  restaurant_name, description,
                  comments, customer_name, customer_address):
    insertQuery = 'UPDATE orders SET '

    insertQuery = insertQuery + 'order_date = "' + order_date + '", '
    insertQuery = insertQuery + 'order_time = "' + order_time + '", '
    insertQuery = insertQuery + 'paid_status = "' + paid_status + '", '
    insertQuery = insertQuery + 'total_pdt = ' + str(total_pdt) + ', '
    insertQuery = insertQuery + 'total_price = ' + str(total_price) + ', '
    insertQuery = insertQuery + 'restaurant_name = "' + restaurant_name + '", '
    insertQuery = insertQuery + 'comments = "' + comments + '", '
    insertQuery = insertQuery + 'customer_name = "' + customer_name + '", '
    insertQuery = insertQuery + 'customer_address = "' + customer_address + '" '
    insertQuery = insertQuery + 'WHERE ' + ' order_no = "' + order_no + '"'

    print (insertQuery)

    cur = conn.cursor()
    cur.execute(insertQuery)
    conn.commit()


def getOrdersFromDB(query):

    cur = conn.cursor()
    cur.execute(query)
    queryData = cur.fetchall()
    return queryData


def insertOrderToDB(order_no,
                    order_date, order_time, paid_status,
                    total_pdt, total_price,
                    restaurant_name, description,
                    comments, customer_name, customer_address):
    countQuery = 'SELECT COUNT(*) FROM orders WHERE order_no = "' + order_no + '" AND restaurant_name = "' + restaurant_name + '"'

    cur = conn.cursor()
    cur.execute(countQuery)
    orderCount = cur.fetchone()

    recOrderCount = int(orderCount[0])

    if recOrderCount == 0:
        insertQuery = 'INSERT INTO orders '
        insertQuery = insertQuery + '( order_no, order_date, order_time, '
        insertQuery = insertQuery + 'paid_status, total_pdt, total_price, '
        insertQuery = insertQuery + 'restaurant_name, description, comments, '
        insertQuery = insertQuery + 'customer_name, customer_address ) VALUES '

        insertQuery = insertQuery + '( "' + order_no + '", "' + order_date + '", "' + order_time + '", "' + paid_status
        insertQuery = insertQuery + '", "' + total_pdt + '", ' + str(total_price) + ', "' + restaurant_name + '", "'
        insertQuery = insertQuery + description + '", "' + comments + '", "' + customer_name + '", "' + customer_address + '")'

        print (insertQuery)

        cur.execute(insertQuery)
        conn.commit()


def getOrderPrices(queryType):
    cur = conn.cursor()
    if queryType == 'Total':
        sumQuery = "SELECT SUM(total_price) FROM orders"
        cur.execute(sumQuery)
        orderCount = cur.fetchone()
        return float(orderCount[0])

    if queryType == 'Paid':
        sumQuery = 'SELECT SUM(total_price) FROM orders WHERE paid_status = "Paid"'
        cur.execute(sumQuery)
        orderCount = cur.fetchone()
        return float(orderCount[0])

    if queryType == 'Cash':
        sumQuery = 'SELECT SUM(total_price) FROM orders WHERE paid_status = "Cash"'
        cur.execute(sumQuery)
        orderCount = cur.fetchone()
        return float(orderCount[0])

        pass


def getTodayOrderNumber(shopName):
    # shopTypes
    # "Chicko's":             0  # CHICKOS shop
    # "Special One":          1, # SPECIAL ONE shop
    # "Nom Nom Kitchen":      2, # NOM NOM KITCHEN shop
    # "Punjab Catering":      3, # PUNJAB CATERING shop
    # "Punjab Catering Leeds":4
    # "Chicko's Fast Food":   5
    # "Punjab Catering Leeds":6

    todayRealDate = dt.datetime.today().strftime("%Y-%m-%d")
    todayRealDate = todayRealDate + " 00:00:00"
    countQuery = 'SELECT COUNT(*) FROM orders WHERE order_date = "' + todayRealDate + '" AND restaurant_name = "' + shopName + '"'

    cur = conn.cursor()
    cur.execute(countQuery)
    orderCount = cur.fetchone()

    return int(orderCount[0])


# ********************************************database manage*****************************************************#

# ********************************************Web scraping codes**************************************************#
# todayDateURL = "02-01-2018"
# todayDate = "02/01/2018"
class EatOrderScraping:
    def __init__(self):

        self.driver1 = None
        self.driver2 = None
        self.driver3 = None
        self.driver4 = None

        self.refreshTimeIntVal = 5

        self.config = SafeConfigParser()
        self.config.read('config.ini')

        self.username1 = self.config.get('main', 'username1')
        self.userpass1 = self.config.get('main', 'password1')

        self.username2 = self.config.get('main', 'username2')
        self.userpass2 = self.config.get('main', 'password2')

        self.username3 = self.config.get('main', 'username3')
        self.userpass3 = self.config.get('main', 'password3')

        self.username4 = self.config.get('main', 'username4')
        self.userpass4 = self.config.get('main', 'password4')

        self.siteurl1 = self.config.get('main', 'firstSite')
        self.siteurl2 = self.config.get('main', 'secondSite')

        self.chrome_path = os.path.join(os.path.dirname(__file__), 'driver', 'chromedriver')
        self.chrome_options = Options()
        self.chrome_options.add_argument("--enable-save-password-bubble=false")

        self.todayDateURL = dt.datetime.today().strftime("%d-%m-%Y")
        self.todayDate = dt.datetime.today().strftime("%d/%m/%Y")
        self.todayRealDate = dt.datetime.today().strftime("%Y-%m-%d")

    def remove_non_ascii_2(self, text):
        return re.sub(r'[^\x00-\x7F]+', ' ', text)

    def remove_non_ascii_1(self, text):
        return ''.join([i if ord(i) < 128 else ' ' for i in text])

    def remove_all_spaces(self, text):

        tmpText = text.strip()
        tmpText = tmpText.replace(" ", "")
        tmpText = re.sub(' +', ' ', tmpText)

        return tmpText

    def initScrapParams(self):

        self.driver1 = webdriver.Chrome(executable_path=self.chrome_path, chrome_options=self.chrome_options)
        self.driver2 = webdriver.Chrome(executable_path=self.chrome_path, chrome_options=self.chrome_options)
        # self.driver3 = webdriver.Chrome(executable_path=self.chrome_path, chrome_options=self.chrome_options)
        self.driver4 = webdriver.Chrome(executable_path=self.chrome_path, chrome_options=self.chrome_options)

    def calcRealDate(self):

        nowTime = dt.datetime.now()

        today12AM = nowTime.replace(hour=12, minute=0, second=0, microsecond=0)
        today7AM = nowTime.replace(hour=7, minute=0, second=0, microsecond=0)

        global todayDate, todayDateURL
        if nowTime < today12AM and nowTime > today7AM:
            changedDate = dt.date.today() + dt.timedelta(days=1)
            self.todayDate = changedDate.strftime("%d/%m/%Y")
            self.todayDateURL = changedDate.strftime("%d-%m-%Y")
            return False

        print ("today date url is " + self.todayDateURL)
        print ("today date  is " + self.todayDate)
        return True

    def openSite(self, siteurl1, siteurl2):

        self.driver1.get(siteurl1)
        self.driver2.get(siteurl1)
        # self.driver3.get(siteurl1)
        self.driver4.get(siteurl2)

    def login1(self, useremail, userpass):

        inputemail = self.driver1.find_element_by_id('username')
        inputemail.click()
        inputemail.send_keys(useremail)

        inputpass = self.driver1.find_element_by_id('password')
        time.sleep(3)
        inputpass.click()

        inputpass.send_keys(userpass)
        time.sleep(3)
        btnlogin = self.driver1.find_element_by_id("continue")
        btnlogin.click()

    def login2(self, useremail, userpass):

        inputemail = self.driver2.find_element_by_id('username')
        inputemail.click()

        inputemail.send_keys(useremail)
        inputpass = self.driver2.find_element_by_id('password')
        time.sleep(3)
        inputpass.click()

        inputpass.send_keys(userpass)
        time.sleep(3)
        btnlogin = self.driver2.find_element_by_id("continue")
        btnlogin.click()

    def login3(self, useremail, userpass):
        inputemail = self.driver3.find_element_by_id('username')
        inputemail.click()

        inputemail.send_keys(useremail)
        inputpass = self.driver3.find_element_by_id('password')
        time.sleep(3)
        inputpass.click()

        inputpass.send_keys(userpass)
        time.sleep(3)
        btnlogin = self.driver3.find_element_by_id("continue")
        btnlogin.click()

    def login4(self, useremail, userpass):

        inputemail = self.driver4.find_element_by_name('username')
        inputemail.click()

        inputemail.send_keys(useremail)
        inputpass = self.driver4.find_element_by_name('password')
        time.sleep(3)
        inputpass.click()

        inputpass.send_keys(userpass)
        time.sleep(3)
        btnlogin = self.driver4.find_element_by_css_selector("button")
        btnlogin.click()

    def openOrderPage1(self):
        time.sleep(3)
        orderMenu1 = self.driver1.find_element_by_class_name('orders')
        orderMenu1.click()

        time.sleep(1)
        orderHistory1 = self.driver1.find_element_by_id('OrdersHistoryLink')
        orderHistory1.click()

    def openOrderPage2(self):

        time.sleep(3)
        orderMenu2 = self.driver2.find_element_by_class_name('orders')
        orderMenu2.click()

        time.sleep(1)
        orderHistory2 = self.driver2.find_element_by_id('OrdersHistoryLink')
        orderHistory2.click()

    def openOrderPage3(self):

        time.sleep(3)
        orderMenu2 = self.driver3.find_element_by_class_name('orders')
        orderMenu2.click()

        time.sleep(1)
        orderHistory2 = self.driver3.find_element_by_id('OrdersHistoryLink')
        orderHistory2.click()

    def searchTodayOrder1(self):

        try:
            time.sleep(2)
            todayTimeTag1 = self.driver1.find_element_by_id('OrderFromTextBox')

            todayTimeTag1.clear()
            time.sleep(1)

            todayTimeTag1.send_keys(self.todayDate)
            time.sleep(1)

            listOrdersBtn1 = self.driver1.find_element_by_id("ListOrdersButton")
            listOrdersBtn1.click()
        except NoSuchElementException:
            time.sleep(3)
            self.driver1.get(self.siteurl1 + "Orders/History/")

    def searchTodayOrder2(self):

        try:
            time.sleep(2)
            todayTimeTag2 = self.driver2.find_element_by_id('OrderFromTextBox')

            todayTimeTag2.clear()
            time.sleep(1)

            todayTimeTag2.send_keys(self.todayDate)
            time.sleep(1)

            listOrdersBtn2 = self.driver2.find_element_by_id("ListOrdersButton")
            listOrdersBtn2.click()
        except NoSuchElementException:
            time.sleep(3)
            self.driver2.get(self.siteurl1 + "Orders/History/")

    def searchTodayOrder3(self):

        try:
            time.sleep(2)
            todayTimeTag2 = self.driver3.find_element_by_id('OrderFromTextBox')

            todayTimeTag2.clear()
            time.sleep(1)

            todayTimeTag2.send_keys(self.todayDate)
            time.sleep(1)

            listOrdersBtn2 = self.driver3.find_element_by_id("ListOrdersButton")
            listOrdersBtn2.click()
        except NoSuchElementException:
            time.sleep(3)
            self.driver1.get(self.siteurl1 + "Orders/History/")

    def execScraping1(self):

        shopState = self.calcRealDate()

        print ("Current Time is"+repr(self.todayDate))

        if shopState:
            self.searchTodayOrder1()
            time.sleep(2)

            try:

                self.driver1.refresh()

                orderCnt = 0
                orderCntText = self.driver1.find_element_by_css_selector('#PageInfo').text

                orderTotalStrList = orderCntText.split()
                if orderTotalStrList[2] != "":
                    totalOrderCNT = float(orderTotalStrList[2])
                    orderCnt = int(math.ceil(totalOrderCNT))

                orderTotalStrList = orderCntText.split()
                if orderTotalStrList[2] != "":
                    totalOrderCNT = float(orderTotalStrList[2])
                    orderCnt = int(totalOrderCNT)

                print ("page count is " + repr(orderCnt))

                print ("Scraping Just Eat Web site-----------------------------------------------------------------")

                currentOrders = getTodayOrderNumber('Punjab Catering Leeds')

                print (
                    "Scraping Just Eat Web site-----------------------------------------------------------------" + str(
                        currentOrders))

                # calculate pagination index

                print ("Order count in Database is****************************** :" + repr(currentOrders))
                print ("Order current Count  is********************************* :" + repr(orderCnt))

                startPaginationIndex = int(math.ceil(orderCnt / 15))

                # pagination Loop
                for pageIndex in range(startPaginationIndex + 1):
                    paginationURL = self.siteurl1 + "Orders/OrdersBetweenDates/" + self.todayDateURL + "/1d?pageIndex=%i" % pageIndex
                    self.driver1.get(paginationURL)

                    orderList = self.driver1.find_elements_by_css_selector('#OrderHistoryTable tbody tr')
                    orderHiddenList = self.driver1.find_elements_by_css_selector('.orderDetailLink')

                    length1 = orderList.__len__()

                    orderItemNo = 0
                    # search page
                    for index in range(length1 / 2):

                        orderItem = orderList[index * 2]
                        print ("order item number:*****************" + repr(orderItemNo))

                        orderItemClass = orderItem.get_attribute('className')

                        if orderItemClass.find('orderDetailsRow') == -1:

                            # get order simple information
                            orderInfoTag = orderItem.find_elements_by_css_selector('td')
                            orderDateValue = orderInfoTag[0].text
                            orderTimeValue = orderInfoTag[1].text
                            orderIDValue = orderInfoTag[2].text
                            orderTotalValue = orderInfoTag[3].text

                            orderTotalValue = float(orderTotalValue[1:])

                            orderCollectionValue = 1

                            orderPaymentType = ""

                            orderCollectionValueHtml = urllib2.unquote(orderInfoTag[5].text)
                            orderCardValueHtml = urllib2.unquote(orderInfoTag[6].get_attribute('innerHTML'))
                            orderCashValueHtml = urllib2.unquote(orderInfoTag[7].get_attribute('innerHTML'))

                            orderCashValueHtml = self.remove_all_spaces(orderCashValueHtml)
                            orderCardValueHtml = self.remove_all_spaces(orderCardValueHtml)

                            if orderCollectionValueHtml.strip() == "":
                                orderCollectionValue = 0

                            if orderCardValueHtml.strip() == "":
                                orderPaymentType = "Cash"

                            if orderCashValueHtml.strip() == "":
                                orderPaymentType = "Paid"

                            # cash and card payment detection
                            print (
                                'This is card HTML : ' + repr(
                                    orderCardValueHtml) + "********************************************")
                            print (
                                'This is cash HTML : ' + repr(
                                    orderCashValueHtml) + "*******************************************")
                            # cash and card payment detection
                            time.sleep(2)
                            # get order details information
                            orderInfoTag[2].click()
                            time.sleep(3)
                            orderDetailViewTag = orderList[index * 2 + 1].find_element_by_css_selector(
                                'td div a')

                            orderDetailViewTag.click()

                            # get order details information
                            restaurentName = self.driver1.find_element_by_css_selector('.rest-name').text

                            tblList = self.driver1.find_elements_by_css_selector('table')

                            orderDetailsTbTrTags = tblList[1].find_elements_by_css_selector('tbody tr')
                            orderDetailTableTrLength = orderDetailsTbTrTags.__len__()
                            customerInfoTableTrLength = tblList[2].find_elements_by_css_selector('tbody tr').__len__()

                            # get order details information
                            totalOrderPcs = 0
                            for orderitemIndex in range(2, orderDetailTableTrLength - customerInfoTableTrLength - 9):
                                orderDetailRowData = orderDetailsTbTrTags[orderitemIndex].find_elements_by_css_selector(
                                    'td')
                                if orderDetailRowData.__len__() == 5:
                                    orderPcs = orderDetailRowData[0].text.strip()

                                    orderPdtName = orderDetailRowData[1].text
                                    orderPdtDescription = orderDetailRowData[2].text
                                    orderPdtUnitPrice = orderDetailRowData[3].text
                                    orderPdtTotalPrice = orderDetailRowData[4].text

                                    orderPdtName = self.remove_non_ascii_1(orderPdtName)
                                    orderPdtDescription = self.remove_non_ascii_1(orderPdtDescription)

                                    if orderPcs != "":
                                        totalOrderPcs = totalOrderPcs + int(orderPcs)

                                    print (
                                        "Pcs: " + orderPcs + " Name: " + orderPdtName + " Description: " + orderPdtDescription + " UnitPirce: " + orderPdtUnitPrice + " Total: " + orderPdtTotalPrice)

                            commentInfoText = orderDetailsTbTrTags[
                                orderDetailTableTrLength - customerInfoTableTrLength - 4].find_element_by_css_selector(
                                'td').text
                            tmpCommStrLen = len('Comments:')
                            commentInfoText = commentInfoText[tmpCommStrLen:]
                            commentInfoText = self.remove_non_ascii_1(commentInfoText)
                            print ("comments inforamtion is " + commentInfoText)

                            # get customer information
                            customerDetailTble = tblList[2]
                            customerInfoTrTags = customerDetailTble.find_elements_by_css_selector('tbody tr')
                            customerAddress1 = customerInfoTrTags[1].find_elements_by_css_selector('td')[1].text
                            customerAddress2 = customerInfoTrTags[2].find_elements_by_css_selector('td')[1].text

                            customerName = customerInfoTrTags[0].find_elements_by_css_selector('td')[1].text
                            customerAddress = customerAddress1 + customerAddress2

                            print ("current customer name is " + repr(customerName))
                            print ("current customerAddress1 is " + repr(customerAddress1))
                            print ("current customerAddress2 is " + repr(customerAddress2))
                            print ("current customerAddress is " + repr(customerAddress))

                            orderTimeValue = orderTimeValue + ":00"
                            orderStatusType = "Paid"

                            commentInfoText = self.remove_non_ascii_1(commentInfoText)
                            customerName = self.remove_non_ascii_1(customerName)
                            customerAddress = self.remove_non_ascii_1(customerAddress)

                            insertOrderToDB(orderIDValue,
                                            self.todayRealDate, ("00-00-00 " + orderTimeValue),
                                            orderPaymentType,
                                            repr(totalOrderPcs), orderTotalValue, "Punjab Catering Leeds",
                                            "", commentInfoText, customerName, customerAddress)

                            # return history page
                            time.sleep(2)
                            self.driver1.back()
                            time.sleep(2)

                        orderItemNo = orderItemNo + 1
                        orderList = self.driver1.find_elements_by_css_selector('#OrderHistoryTable tbody tr')
            except NoSuchElementException:
                self.driver1.get(self.siteurl1 + "Orders/History/")
                pass
        else:
            pass
        Timer(self.refreshTimeIntVal, self.execScraping1, ()).start()

    def execScraping2(self):

        shopState = self.calcRealDate()
        if shopState:
            self.searchTodayOrder2()
            time.sleep(2)

            try:

                self.driver2.refresh()

                orderCnt = 0
                orderCntText = self.driver2.find_element_by_css_selector('#PageInfo').text

                orderTotalStrList = orderCntText.split()
                if orderTotalStrList[2] != "":
                    totalOrderCNT = float(orderTotalStrList[2])
                    orderCnt = int(math.ceil(totalOrderCNT))

                orderTotalStrList = orderCntText.split()
                if orderTotalStrList[2] != "":
                    totalOrderCNT = float(orderTotalStrList[2])
                    orderCnt = int(totalOrderCNT)

                print ("page count is " + repr(orderCnt))

                print ("Scraping Just Eat Web site-----------------------------------------------------------------")

                currentOrders = getTodayOrderNumber("Chicko's Fast Food")

                print (
                    "Scraping Just Eat Web site-----------------------------------------------------------------" + str(
                        currentOrders))

                # calculate pagination index

                print ("Order count in Database is****************************** :" + repr(currentOrders))
                print ("Order current Count  is********************************* :" + repr(orderCnt))

                startPaginationIndex = int(math.ceil(orderCnt / 15))

                # pagination Loop
                for pageIndex in range(startPaginationIndex + 1):
                    paginationURL = self.siteurl1 + "Orders/OrdersBetweenDates/" + self.todayDateURL + "/1d?pageIndex=%i" % pageIndex
                    self.driver2.get(paginationURL)

                    orderList = self.driver2.find_elements_by_css_selector('#OrderHistoryTable tbody tr')
                    orderHiddenList = self.driver2.find_elements_by_css_selector('.orderDetailLink')

                    length1 = orderList.__len__()

                    orderItemNo = 0
                    # search page
                    for index in range(length1 / 2):

                        orderItem = orderList[index * 2]
                        print ("order item number:*****************" + repr(orderItemNo))

                        orderItemClass = orderItem.get_attribute('className')

                        if orderItemClass.find('orderDetailsRow') == -1:

                            # get order simple information
                            orderInfoTag = orderItem.find_elements_by_css_selector('td')
                            orderDateValue = orderInfoTag[0].text
                            orderTimeValue = orderInfoTag[1].text
                            orderIDValue = orderInfoTag[2].text
                            orderTotalValue = orderInfoTag[3].text

                            orderTotalValue = float(orderTotalValue[1:])

                            orderCollectionValue = 1

                            orderPaymentType = ""

                            orderCollectionValueHtml = urllib2.unquote(orderInfoTag[5].text)
                            orderCardValueHtml = urllib2.unquote(orderInfoTag[6].get_attribute('innerHTML'))
                            orderCashValueHtml = urllib2.unquote(orderInfoTag[7].get_attribute('innerHTML'))

                            orderCashValueHtml = self.remove_all_spaces(orderCashValueHtml)
                            orderCardValueHtml = self.remove_all_spaces(orderCardValueHtml)

                            if orderCollectionValueHtml.strip() == "":
                                orderCollectionValue = 0

                            if orderCardValueHtml.strip() == "":
                                orderPaymentType = "Cash"

                            if orderCashValueHtml.strip() == "":
                                orderPaymentType = "Paid"

                            # cash and card payment detection
                            print (
                                'This is card HTML : ' + repr(
                                    orderCardValueHtml) + "********************************************")
                            print (
                                'This is cash HTML : ' + repr(
                                    orderCashValueHtml) + "*******************************************")
                            # cash and card payment detection
                            time.sleep(2)
                            # get order details information
                            orderInfoTag[2].click()
                            time.sleep(3)
                            orderDetailViewTag = orderList[index * 2 + 1].find_element_by_css_selector(
                                'td div a')

                            orderDetailViewTag.click()

                            # get order details information
                            restaurentName = self.driver2.find_element_by_css_selector('.rest-name').text

                            tblList = self.driver2.find_elements_by_css_selector('table')

                            orderDetailsTbTrTags = tblList[1].find_elements_by_css_selector('tbody tr')
                            orderDetailTableTrLength = orderDetailsTbTrTags.__len__()
                            customerInfoTableTrLength = tblList[2].find_elements_by_css_selector('tbody tr').__len__()

                            # get order details information
                            totalOrderPcs = 0
                            for orderitemIndex in range(2, orderDetailTableTrLength - customerInfoTableTrLength - 9):
                                orderDetailRowData = orderDetailsTbTrTags[orderitemIndex].find_elements_by_css_selector(
                                    'td')
                                if orderDetailRowData.__len__() == 5:
                                    orderPcs = orderDetailRowData[0].text.strip()

                                    orderPdtName = orderDetailRowData[1].text
                                    orderPdtDescription = orderDetailRowData[2].text
                                    orderPdtUnitPrice = orderDetailRowData[3].text
                                    orderPdtTotalPrice = orderDetailRowData[4].text

                                    orderPdtName = self.remove_non_ascii_1(orderPdtName)
                                    orderPdtDescription = self.remove_non_ascii_1(orderPdtDescription)

                                    if orderPcs != "":
                                        totalOrderPcs = totalOrderPcs + int(orderPcs)

                                    print (
                                        "Pcs: " + orderPcs + " Name: " + orderPdtName + " Description: " + orderPdtDescription + " UnitPirce: " + orderPdtUnitPrice + " Total: " + orderPdtTotalPrice)

                            commentInfoText = orderDetailsTbTrTags[
                                orderDetailTableTrLength - customerInfoTableTrLength - 4].find_element_by_css_selector(
                                'td').text
                            tmpCommStrLen = len('Comments:')
                            commentInfoText = commentInfoText[tmpCommStrLen:]
                            commentInfoText = self.remove_non_ascii_1(commentInfoText)
                            print ("comments inforamtion is " + commentInfoText)

                            # get customer information
                            customerDetailTble = tblList[2]
                            customerInfoTrTags = customerDetailTble.find_elements_by_css_selector('tbody tr')
                            customerAddress1 = customerInfoTrTags[1].find_elements_by_css_selector('td')[1].text
                            customerAddress2 = customerInfoTrTags[2].find_elements_by_css_selector('td')[1].text

                            customerName = customerInfoTrTags[0].find_elements_by_css_selector('td')[1].text
                            customerAddress = customerAddress1 + customerAddress2

                            print ("current customer name is " + repr(customerName))
                            print ("current customerAddress1 is " + repr(customerAddress1))
                            print ("current customerAddress2 is " + repr(customerAddress2))
                            print ("current customerAddress is " + repr(customerAddress))

                            orderTimeValue = orderTimeValue + ":00"
                            orderStatusType = "Paid"

                            commentInfoText = self.remove_non_ascii_1(commentInfoText)
                            customerName = self.remove_non_ascii_1(customerName)
                            customerAddress = self.remove_non_ascii_1(customerAddress)

                            insertOrderToDB(orderIDValue,
                                            self.todayRealDate, ("00-00-00 " + orderTimeValue),
                                            orderPaymentType,
                                            repr(totalOrderPcs), orderTotalValue, "Chicko's Fast Food",
                                            "", commentInfoText, customerName, customerAddress)

                            # return history page
                            time.sleep(2)
                            self.driver2.back()
                            time.sleep(2)

                        orderItemNo = orderItemNo + 1
                        orderList = self.driver2.find_elements_by_css_selector('#OrderHistoryTable tbody tr')
            except NoSuchElementException:
                self.driver2.get(self.siteurl1 + "Orders/History/")
                pass
        else:
            pass
        Timer(self.refreshTimeIntVal, self.execScraping2, ()).start()

    def execScraping3(self):

        shopState = self.calcRealDate()
        if shopState:
            self.searchTodayOrder3()
            time.sleep(2)

            try:

                self.driver3.refresh()

                orderCnt = 0
                orderCntText = self.driver3.find_element_by_css_selector('#PageInfo').text

                orderTotalStrList = orderCntText.split()
                if orderTotalStrList[2] != "":
                    totalOrderCNT = float(orderTotalStrList[2])
                    orderCnt = int(math.ceil(totalOrderCNT))

                orderTotalStrList = orderCntText.split()
                if orderTotalStrList[2] != "":
                    totalOrderCNT = float(orderTotalStrList[2])
                    orderCnt = int(totalOrderCNT)

                print ("page count is " + repr(orderCnt))

                print ("Scraping Just Eat Web site-----------------------------------------------------------------")

                currentOrders = getTodayOrderNumber('Punjab Catering Leeds')

                print (
                    "Scraping Just Eat Web site-----------------------------------------------------------------" + str(
                        currentOrders))

                # calculate pagination index

                print ("Order count in Database is****************************** :" + repr(currentOrders))
                print ("Order current Count  is********************************* :" + repr(orderCnt))

                startPaginationIndex = int(math.ceil(orderCnt / 15))

                # pagination Loop
                for pageIndex in range(startPaginationIndex + 1):
                    paginationURL = self.siteurl1 + "Orders/OrdersBetweenDates/" + self.todayDateURL + "/1d?pageIndex=%i" % pageIndex
                    self.driver3.get(paginationURL)

                    orderList = self.driver3.find_elements_by_css_selector('#OrderHistoryTable tbody tr')
                    orderHiddenList = self.driver3.find_elements_by_css_selector('.orderDetailLink')

                    length1 = orderList.__len__()

                    orderItemNo = 0
                    # search page
                    for index in range(length1 / 2):

                        orderItem = orderList[index * 2]
                        print ("order item number:*****************" + repr(orderItemNo))

                        orderItemClass = orderItem.get_attribute('className')

                        if orderItemClass.find('orderDetailsRow') == -1:

                            # get order simple information
                            orderInfoTag = orderItem.find_elements_by_css_selector('td')
                            orderDateValue = orderInfoTag[0].text
                            orderTimeValue = orderInfoTag[1].text
                            orderIDValue = orderInfoTag[2].text
                            orderTotalValue = orderInfoTag[3].text

                            orderTotalValue = float(orderTotalValue[1:])

                            orderCollectionValue = 1

                            orderPaymentType = ""

                            orderCollectionValueHtml = urllib2.unquote(orderInfoTag[5].text)
                            orderCardValueHtml = urllib2.unquote(orderInfoTag[6].get_attribute('innerHTML'))
                            orderCashValueHtml = urllib2.unquote(orderInfoTag[7].get_attribute('innerHTML'))

                            orderCashValueHtml = self.remove_all_spaces(orderCashValueHtml)
                            orderCardValueHtml = self.remove_all_spaces(orderCardValueHtml)

                            if orderCollectionValueHtml.strip() == "":
                                orderCollectionValue = 0

                            if orderCardValueHtml.strip() == "":
                                orderPaymentType = "Cash"

                            if orderCashValueHtml.strip() == "":
                                orderPaymentType = "Paid"

                            # cash and card payment detection
                            print (
                                'This is card HTML : ' + repr(
                                    orderCardValueHtml) + "********************************************")
                            print (
                                'This is cash HTML : ' + repr(
                                    orderCashValueHtml) + "*******************************************")
                            # cash and card payment detection
                            time.sleep(2)
                            # get order details information
                            orderInfoTag[2].click()
                            time.sleep(3)
                            orderDetailViewTag = orderList[index * 2 + 1].find_element_by_css_selector(
                                'td div a')

                            orderDetailViewTag.click()

                            # get order details information
                            restaurentName = self.driver3.find_element_by_css_selector('.rest-name').text

                            tblList = self.driver3.find_elements_by_css_selector('table')

                            orderDetailsTbTrTags = tblList[1].find_elements_by_css_selector('tbody tr')
                            orderDetailTableTrLength = orderDetailsTbTrTags.__len__()
                            customerInfoTableTrLength = tblList[2].find_elements_by_css_selector('tbody tr').__len__()

                            # get order details information
                            totalOrderPcs = 0
                            for orderitemIndex in range(2, orderDetailTableTrLength - customerInfoTableTrLength - 9):
                                orderDetailRowData = orderDetailsTbTrTags[orderitemIndex].find_elements_by_css_selector(
                                    'td')
                                if orderDetailRowData.__len__() == 5:
                                    orderPcs = orderDetailRowData[0].text.strip()

                                    orderPdtName = orderDetailRowData[1].text
                                    orderPdtDescription = orderDetailRowData[2].text
                                    orderPdtUnitPrice = orderDetailRowData[3].text
                                    orderPdtTotalPrice = orderDetailRowData[4].text

                                    orderPdtName = self.remove_non_ascii_1(orderPdtName)
                                    orderPdtDescription = self.remove_non_ascii_1(orderPdtDescription)

                                    if orderPcs != "":
                                        totalOrderPcs = totalOrderPcs + int(orderPcs)

                                    print (
                                        "Pcs: " + orderPcs + " Name: " + orderPdtName + " Description: " + orderPdtDescription + " UnitPirce: " + orderPdtUnitPrice + " Total: " + orderPdtTotalPrice)

                            commentInfoText = orderDetailsTbTrTags[
                                orderDetailTableTrLength - customerInfoTableTrLength - 4].find_element_by_css_selector(
                                'td').text
                            tmpCommStrLen = len('Comments:')
                            commentInfoText = commentInfoText[tmpCommStrLen:]
                            commentInfoText = self.remove_non_ascii_1(commentInfoText)
                            print ("comments inforamtion is " + commentInfoText)

                            # get customer information
                            customerDetailTble = tblList[2]
                            customerInfoTrTags = customerDetailTble.find_elements_by_css_selector('tbody tr')
                            customerAddress1 = customerInfoTrTags[1].find_elements_by_css_selector('td')[1].text
                            customerAddress2 = customerInfoTrTags[2].find_elements_by_css_selector('td')[1].text

                            customerName = customerInfoTrTags[0].find_elements_by_css_selector('td')[1].text
                            customerAddress = customerAddress1 + customerAddress2

                            print ("current customer name is " + repr(customerName))
                            print ("current customerAddress1 is " + repr(customerAddress1))
                            print ("current customerAddress2 is " + repr(customerAddress2))
                            print ("current customerAddress is " + repr(customerAddress))

                            orderTimeValue = orderTimeValue + ":00"
                            orderStatusType = "Paid"

                            commentInfoText = self.remove_non_ascii_1(commentInfoText)
                            customerName = self.remove_non_ascii_1(customerName)
                            customerAddress = self.remove_non_ascii_1(customerAddress)

                            insertOrderToDB(orderIDValue,
                                            self.todayRealDate, ("00-00-00 " + orderTimeValue),
                                            orderPaymentType,
                                            repr(totalOrderPcs), orderTotalValue, "Chicko's Fast Food",
                                            "", commentInfoText, customerName, customerAddress)

                            # return history page
                            time.sleep(2)
                            self.driver3.back()
                            time.sleep(2)

                        orderItemNo = orderItemNo + 1
                        orderList = self.driver3.find_elements_by_css_selector('#OrderHistoryTable tbody tr')
            except NoSuchElementException:
                self.driver3.get(self.siteurl1 + "Orders/History/")
                pass
        else:
            pass
        Timer(self.refreshTimeIntVal, self.execScraping3, ()).start()

    def execScraping4(self):
        shopXPATHList = [
            '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[3]',  # CHICKOS shop
            '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[4]',  # SPECIAL ONE shop
            '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[5]',  # NOM NOM KITCHEN shop
            '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[6]',  # PUNJAB CATERING shop
        ]
        shopNameList = [
            "Chicko's",  # CHICKOS shop
            "Special One",  # SPECIAL ONE shop
            "Nom Nom Kitchen",  # NOM NOM KITCHEN shop
            "Punjab Catering",  # PUNJAB CATERING shop
        ]

        # check current url when session expired
        time.sleep(6)
        if self.driver4.current_url == self.siteurl2:  # This mean session expired

            self.login4(self.username4, self.userpass4)
            self.driver4.get(self.siteurl2 + "select")

        for shopIndex in range(4):

            time.sleep(3)
            print ("*******************************" + "Searching " + shopNameList[shopIndex] + "*********************")

            currentOrders = getTodayOrderNumber(shopNameList[shopIndex])

            print ("Current Shop Orders in DataBase" + str(currentOrders))

            try:
                shopNameTag = self.driver4.find_element_by_xpath(shopXPATHList[shopIndex])
                shopNameTag.click()
            except NoSuchElementException:
                self.driver4.get(self.siteurl2 + "select")
                self.execScraping4()
                return

            time.sleep(4)

            # hide alert box
            try:
                self.driver4.find_element_by_xpath(
                    '/html/body/div[2]/div/div[1]/div/div/div[2]/button[1]').click()  # Recent Order Page
            except NoSuchElementException:
                print ("Alert Dialog Hidden")

            try:
                # open full order page

                print ("Open Current Order Details Page")

                time.sleep(4)
                self.driver4.find_element_by_xpath(
                    '//*[@id="app"]/div/main/div/div[1]/div[3]/div[3]/div[1]/div[2]/button').click()
                # Loop order summary items
                # orderList = driver4.find_element_by_css_selector('.page').find_elements_by_css_selector('.main div div div')
                time.sleep(4)
                orderList = self.driver4.find_elements_by_xpath('//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div')
                orderSize = orderList.__len__()

                # *****************************Get Order Detail Information****************************************************#
                # get order number
                for orderIndex in range(currentOrders, orderSize):

                    time.sleep(2)
                    # order Time
                    orderTimeTags = orderList[orderIndex].find_element_by_css_selector('span span')
                    orderTime = orderTimeTags.text
                    print ("This order info :" + repr(orderTime))
                    # order ID and order Total Price
                    spanTags = orderList[orderIndex].find_elements_by_css_selector('p span')
                    spanTagSize = spanTags.__len__()
                    orderTotalPriceT = 0
                    orderID = ""
                    if spanTagSize > 1:
                        orderTotalPriceStr = spanTags[0].text
                        orderTotalPriceT = float(orderTotalPriceStr[1:])
                        orderID = spanTags[1].text

                    time.sleep(1)
                    orderList[orderIndex].click()

                    # get order information (total order, comments, customer name,restaurant name)

                    # payment status
                    time.sleep(2)
                    orderStatusStr = self.driver4.find_element_by_css_selector('div.main h1').text
                    orderStatusType = 'Cash'
                    if orderStatusStr == "Order Confirmed":
                        orderStatusType = 'Paid'

                    # order payment type
                    time.sleep(1)

                    orderPaymentWrapTag = self.driver4.find_element_by_xpath(
                        '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[2]/div/section[2]/dl[2]/dd')
                    orderPaymentStr = orderPaymentWrapTag.text

                    orderPaymentType = "Cash"
                    if orderPaymentStr == "Prepaid online":
                        orderPaymentType = "Paid"
                    print ("Payment String is: " + orderPaymentType)

                    # get customer address and comments
                    orderDeliveryWrapTag = self.driver4.find_element_by_xpath(
                        '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[2]/div/section[2]/dl[3]')
                    deliveryStrLen = len("Delivery to:")
                    orderCustomerAddress = orderDeliveryWrapTag.text
                    orderCustomerAddress = orderCustomerAddress[deliveryStrLen:]
                    orderCustomerAddress = orderCustomerAddress.strip()
                    orderComments = ""

                    try:
                        commentsElem = orderDeliveryWrapTag.find_element_by_tag_name("span")
                        orderComments = commentsElem.text

                        cstAddrLen = len(orderCustomerAddress)
                        comLen = len(orderComments)
                        orderCustomerAddress = orderCustomerAddress[:(cstAddrLen - comLen)]
                        orderCustomerAddress = orderCustomerAddress.strip()

                    except NoSuchElementException:
                        pass

                    # get all order details
                    orderPdtsTblWrapper = self.driver4.find_element_by_xpath(
                        '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[2]/div/section[3]/ul')

                    orderPdtList = self.driver4.find_elements_by_xpath(
                        '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[2]/div/section[3]/ul/li')

                    totalPdts = 0
                    orderTotalPrice = 0
                    if orderPdtList.__len__() > 1:
                        for pdtIndex in range(1, orderPdtList.__len__()):
                            pdtSpanTags = orderPdtList[pdtIndex].find_elements_by_css_selector('span')

                            pdtSpanTagsLen = pdtSpanTags.__len__()

                            pdtCnt = pdtSpanTags[0].text.strip()  # product counts
                            pdtCnt = pdtCnt[:len(pdtCnt) - 1]
                            totalPdts = totalPdts + int(pdtCnt)

                            pdtDescription = ""
                            for desIndex in range(1, (pdtSpanTagsLen - 1)):
                                pdtDescription = pdtDescription + pdtSpanTags[desIndex].text

                            pdtPrice = pdtSpanTags[pdtSpanTagsLen - 1].text

                            orderTotalPrice = orderTotalPrice + float(pdtPrice[1:])
                            print ("Qty:" + repr(pdtCnt) + ",pdtDescription : " + pdtDescription + ", Price:" + str(
                                orderTotalPrice))

                    # get order total Price
                    # **********************************************insert order data to databse*********************************************
                    tempDateSrt = dt.datetime.strptime(orderTime, '%I:%M %p')
                    orderTime = tempDateSrt.strftime("%H:%M:%S")

                    orderID = orderID[1:]

                    orderComments = self.remove_non_ascii_1(orderComments)
                    orderCustomerAddress = self.remove_non_ascii_1(orderCustomerAddress)

                    print ("Order Customer Address " + orderCustomerAddress)
                    print ("Order Comments**************************" + orderComments)

                    insertOrderToDB(orderID, self.todayRealDate, ("00-00-00 " + orderTime),
                                    orderPaymentType,
                                    repr(totalPdts), orderTotalPriceT, shopNameList[shopIndex],
                                    "", orderComments, "", orderCustomerAddress)

                    time.sleep(1)
                    self.driver4.back()

                    orderList = self.driver4.find_elements_by_xpath(
                        '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div')

                print ("order size is :" + repr(orderSize))
            except NoSuchElementException:
                pass

            self.driver4.get(self.siteurl2 + "select")

        Timer(self.refreshTimeIntVal, self.execScraping4, ()).start()

        print ("OPEN https://partner.hungryhouse.co.uk")

    def execFullScraping(self, threadName, delay):

        self.initScrapParams()

        self.openSite(self.siteurl1, self.siteurl2)

        self.login1(self.username1, self.userpass1)
        self.login2(self.username2, self.userpass2)
        # self.login3(self.username3, self.userpass3)
        self.login4(self.username4, self.userpass4)

        self.openOrderPage1()
        self.openOrderPage2()
        # self.openOrderPage3()

        self.execScraping4()

        self.execScraping1()
        self.execScraping2()

        # self.execScraping3()

    def stopFullScraping(self):

        self.driver1.close()
        self.driver2.close()
        self.driver3.close()
        self.driver4.close()

        pass


# ********************************************Web scraping codes**************************************************#
#
# window building codes
#
window = Tkinter.Tk()
window.wm_title("Data Mining")


class GetOrderWidget(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack()
        self.winfo_toplevel().minsize(1000, 400)

        self.startbtn = Button(self, text='Start Scraping', command=self.start_scraping)
        self.startbtn.grid(row=1, column=0, padx=15, pady=10)

        # self.stopbtn = Button(self, text='Stop Scraping', command=self.stop_scraping)
        # self.stopbtn.grid(row=1, column=2, padx=15)

        self.todaybtn = Button(self, text='Today Orders', command=self.today_orders)
        self.todaybtn.grid(row=1, column=2, padx=15)

        self.totalbtn = Button(self, text='Total Orders', command=self.total_orders)
        self.totalbtn.grid(row=1, column=4, padx=15)

        self.paidbtn = Button(self, text='Paid Orders', command=self.paid_orders)
        self.paidbtn.grid(row=1, column=6, padx=15)

        self.cashbtn = Button(self, text='Cash Orders', command=self.cash_orders)
        self.cashbtn.grid(row=1, column=7, padx=15)

        self.cashbtn = Button(self, text='Clear System', command=self.clear_orders)
        self.cashbtn.grid(row=1, column=8, padx=15)

        self.delbtn = Button(self, text='Delete Order', command=self.delete_order)
        self.delbtn.grid(row=1, column=9, padx=15)

        self.stopbtn = Button(self, text='Save Order', command=self.save_orders)
        self.stopbtn.grid(row=1, column=10, padx=15)

        self.tframe = Frame(self)
        self.tframe.pack()
        self.tframe.grid(row=2, column=0, columnspan=12, rowspan=8)

        self.colLabels = ["OrderNo", "Restaurant Name", "OrderTime", "OrderDate",
                          "TotalPrice", "Pcs", "Paid Status", "Comments", "CustomerName", "CustomerAddress"]

        self.order_model = TableModel()
        # order table column configuration
        self.table = TableCanvas(self.tframe, width=1000, height=350, columnwidh=100, cols=10)

        self.table.model.columnlabels['1'] = "OrderNo"
        self.table.model.columnlabels['2'] = "Restaurant Name"
        self.table.model.columnlabels['3'] = "OrderTime"
        self.table.model.columnlabels['4'] = "OrderDate"
        self.table.model.columnlabels['5'] = "TotalPrice"
        self.table.model.columnlabels['6'] = "Pcs"
        self.table.model.columnlabels['7'] = "Paid Status"
        self.table.model.columnlabels['8'] = "Comments"
        self.table.model.columnlabels['9'] = "CustomerName"
        self.table.model.columnlabels['10'] = "CustomerAddress"

        Label(self, text="Total Amount of Order").grid(row=15, column=1)
        self.totalOrdersBox = Entry(self)
        self.totalOrdersBox.grid(row=15, column=2, pady=100)

        Label(self, text="Paid Amount of Order").grid(row=15, column=4)
        self.totalPaids = Entry(self)
        self.totalPaids.grid(row=15, column=6)

        Label(self, text="Cash Amount of Orders").grid(row=15, column=7)
        self.totalCashs = Entry(self)
        self.totalCashs.grid(row=15, column=8)

        self.table.createTableFrame()

        self.scrapingThread = EatOrderScraping()

        self.todayRealDate = dt.datetime.today().strftime("%Y-%m-%d")

    def start_scraping(self):
        thread.start_new_thread(self.scrapingThread.execFullScraping, ("Scraping_Thread", 2,))

    def stop_scraping(self):
        self.scrapingThread.stopFullScraping()

        thread.exit()

        self.quit()

    def createRandomStrings(self, l, n):
        """create list of l random strings, each of length n"""
        names = []
        for i in range(l):
            val = ''.join(random.choice(string.ascii_lowercase) for x in range(n))
            names.append(val)
        return names

    def createData(self, orderData):
        """Creare random dict for test data"""

        data = {}
        rowCnt = 0
        tmpdata = {}
        for tempRow in orderData:
            data[rowCnt] = {}
            rowCnt = rowCnt + 1
        for rowIndex in range(rowCnt):
            data[rowIndex][0] = orderData[rowIndex][1]
            data[rowIndex][1] = orderData[rowIndex][2]

            tmpVar = orderData[rowIndex][3]

            data[rowIndex][2] = tmpVar[11:]
            data[rowIndex][3] = orderData[rowIndex][4].strftime("%Y-%m-%d")
            data[rowIndex][4] = orderData[rowIndex][5]
            data[rowIndex][5] = orderData[rowIndex][6]
            data[rowIndex][6] = orderData[rowIndex][7]
            data[rowIndex][7] = orderData[rowIndex][9]
            data[rowIndex][8] = orderData[rowIndex][10]
            data[rowIndex][9] = orderData[rowIndex][11]
        return data

    def today_orders(self):

        todayRealDateT = dt.datetime.today().strftime("%Y-%m-%d")
        condDateStr = todayRealDateT + " 00:00:00"

        getOrderSQL = 'SELECT * FROM orders WHERE order_date = "' + condDateStr + '" ORDER BY order_time'
        print ("today order query"+repr(getOrderSQL))
        orderData = getOrdersFromDB(getOrderSQL)
        data = self.createData(orderData)
        self.order_model.importDict(data)
        self.table.setModel(self.order_model)
        self.table.redrawTable()

    def total_orders(self):

        recCntPrev = self.table.model.getRowCount()
        self.table.model.deleteRows(range(recCntPrev))
        self.table.redrawTable()

        getOrderSQL = 'SELECT * FROM orders ORDER BY order_date'
        orderData = getOrdersFromDB(getOrderSQL)
        data = self.createData(orderData)

        self.order_model = TableModel()

        self.order_model.importDict(data)
        self.table.setModel(self.order_model)
        self.table.redrawTable()

        #recCnt = self.order_model.getRowCount()

        recCnt = getOrderPrices('Total')

        self.totalOrdersBox.delete(0, 'end')
        self.totalOrdersBox.insert(0, str(recCnt))

    def paid_orders(self):

        recCntPrev = self.table.model.getRowCount()
        self.table.model.deleteRows(range(recCntPrev))
        self.table.redrawTable()

        getOrderSQL = 'SELECT * FROM orders WHERE paid_status = "Paid" ORDER BY order_date'
        orderData = getOrdersFromDB(getOrderSQL)

        self.order_model = TableModel()

        data = self.createData(orderData)
        self.order_model.importDict(data)
        self.table.setModel(self.order_model)
        self.table.redrawTable()

        #recCnt = self.order_model.getRowCount()

        recCnt = getOrderPrices('Paid')

        self.totalPaids.delete(0, 'end')
        self.totalPaids.insert(0, str(recCnt))

    def cash_orders(self):

        recCntPrev = self.table.model.getRowCount()
        self.table.model.deleteRows(range(recCntPrev))
        self.table.redrawTable()

        getOrderSQL = 'SELECT * FROM orders WHERE paid_status = "Cash" ORDER BY order_time'
        orderData = getOrdersFromDB(getOrderSQL)
        data = self.createData(orderData)

        self.order_model = TableModel()

        self.order_model.importDict(data)
        self.table.setModel(self.order_model)
        self.table.redrawTable()

        recCnt = getOrderPrices('Cash')

        self.totalCashs.delete(0, 'end')
        self.totalCashs.insert(0, str(recCnt))

    def clear_orders(self):

        deleteOrderSQL = 'DELETE FROM orders'
        deleteOrderFromDB(deleteOrderSQL)
        self.order_model = TableModel()
        recCnt = self.table.model.getRowCount()
        self.table.model.deleteRows(range(recCnt))
        self.table.redrawTable()

    def delete_order(self):

        selectedRow = self.table.getSelectedRow()
        if selectedRow > -1:
            selOrderID = self.table.model.getValueAt(selectedRow, 0)
            deleteOrderSQL = 'DELETE FROM orders WHERE order_no = "' + selOrderID + '"'
            deleteOrderFromDB(deleteOrderSQL)
            self.order_model.deleteRow(selectedRow)
            self.table.redrawTable()

    def save_orders(self):

        selectedRow = self.table.getSelectedRow()
        if selectedRow > -1:
            order_no = self.table.model.getValueAt(selectedRow, 0)
            restaurant_name = self.table.model.getValueAt(selectedRow, 1)
            order_time = self.table.model.getValueAt(selectedRow, 2)
            order_date = self.table.model.getValueAt(selectedRow, 3)
            total_price = self.table.model.getValueAt(selectedRow, 4)
            total_pdt = self.table.model.getValueAt(selectedRow, 5)
            paid_status = self.table.model.getValueAt(selectedRow, 6)
            comments = self.table.model.getValueAt(selectedRow, 7)
            customername = self.table.model.getValueAt(selectedRow, 8)
            customeraddress = self.table.model.getValueAt(selectedRow, 9)
            order_time = "00-00-00 " + order_time
            order_date = order_date + " 00:00:00"
            saveOrderToDB(order_no,
                          order_date, order_time, paid_status,
                          total_pdt, total_price,
                          restaurant_name, "",
                          comments, customername, customeraddress)


GetOrderWidget().mainloop()
