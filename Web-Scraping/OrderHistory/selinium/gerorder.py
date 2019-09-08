from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import os, fnmatch, sys, time, csv
from configparser import SafeConfigParser
import datetime as dt
import urllib2
import math
from threading import Timer

from random import randint

# Read config.ini
refreshTimeIntVal = 5

config = SafeConfigParser()
config.read('config.ini')

username1 = config.get('main', 'username1')
userpass1 = config.get('main', 'password1')

username2 = config.get('main', 'username2')
userpass2 = config.get('main', 'password2')

username3 = config.get('main', 'username3')
userpass3 = config.get('main', 'password3')

username4 = config.get('main', 'username4')
userpass4 = config.get('main', 'password4')

siteurl1 = config.get('main', 'firstSite')
siteurl2 = config.get('main', 'secondSite')

chrome_path = os.path.join(os.path.dirname(__file__), 'driver', 'chromedriver')
chrome_options = Options()
chrome_options.add_argument("--enable-save-password-bubble=false")

driver1 = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
driver2 = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
driver3 = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
driver4 = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)

todayDateURL = dt.datetime.today().strftime("%d-%m-%Y")
todayDate = dt.datetime.today().strftime("%d/%m/%Y")


# todayDateURL = "02-01-2018"
# todayDate = "02/01/2018"

def calcRealDate():
    nowTime = dt.datetime.now()

    today12AM = nowTime.replace(hour=12, minute=0, second=0, microsecond=0)
    today7AM = nowTime.replace(hour=7, minute=0, second=0, microsecond=0)

    global todayDate, todayDateURL
    if nowTime < today12AM and nowTime > today7AM:
        changedDate = dt.date.today() + dt.timedelta(days=1)
        todayDate = changedDate.strftime("%d/%m/%Y")
        todayDateURL = changedDate.strftime("%d-%m-%Y")

        return False

    print ("today date url is " + todayDateURL)
    print ("today date  is " + todayDate)

    return True


def openSite(siteurl1, siteurl2):
    driver1.get(siteurl1)
    driver2.get(siteurl1)
    driver3.get(siteurl1)
    driver4.get(siteurl2)


def login1(useremail, userpass):
    inputemail = driver1.find_element_by_id('username')
    inputemail.click()
    inputemail.send_keys(useremail)

    inputpass = driver1.find_element_by_id('password')
    time.sleep(3)
    inputpass.click()

    inputpass.send_keys(userpass)
    time.sleep(3)
    btnlogin = driver1.find_element_by_id("continue")
    btnlogin.click()


def login2(useremail, userpass):
    inputemail = driver2.find_element_by_id('username')
    inputemail.click()

    inputemail.send_keys(useremail)
    inputpass = driver2.find_element_by_id('password')
    time.sleep(3)
    inputpass.click()

    inputpass.send_keys(userpass)
    time.sleep(3)
    btnlogin = driver2.find_element_by_id("continue")
    btnlogin.click()


def login3(useremail, userpass):
    inputemail = driver3.find_element_by_id('username')
    inputemail.click()

    inputemail.send_keys(useremail)
    inputpass = driver3.find_element_by_id('password')
    time.sleep(3)
    inputpass.click()

    inputpass.send_keys(userpass)
    time.sleep(3)
    btnlogin = driver3.find_element_by_id("continue")
    btnlogin.click()


def login4(useremail, userpass):
    inputemail = driver4.find_element_by_name('username')
    inputemail.click()

    inputemail.send_keys(useremail)
    inputpass = driver4.find_element_by_name('password')
    time.sleep(3)
    inputpass.click()

    inputpass.send_keys(userpass)
    time.sleep(3)
    btnlogin = driver4.find_element_by_css_selector("button")
    btnlogin.click()


def openOrderPage1():
    time.sleep(3)
    orderMenu1 = driver1.find_element_by_class_name('orders')
    orderMenu1.click()

    time.sleep(1)
    orderHistory1 = driver1.find_element_by_id('OrdersHistoryLink')
    orderHistory1.click()


def openOrderPage2():
    time.sleep(3)
    orderMenu2 = driver2.find_element_by_class_name('orders')
    orderMenu2.click()

    time.sleep(1)
    orderHistory2 = driver2.find_element_by_id('OrdersHistoryLink')
    orderHistory2.click()


def openOrderPage3():
    time.sleep(3)
    orderMenu2 = driver3.find_element_by_class_name('orders')
    orderMenu2.click()

    time.sleep(1)
    orderHistory2 = driver3.find_element_by_id('OrdersHistoryLink')
    orderHistory2.click()


def searchTodayOrder1():
    time.sleep(2)
    todayTimeTag1 = driver1.find_element_by_id('OrderFromTextBox')

    todayTimeTag1.clear()
    time.sleep(1)

    todayTimeTag1.send_keys(todayDate)
    time.sleep(1)

    listOrdersBtn1 = driver1.find_element_by_id("ListOrdersButton")
    listOrdersBtn1.click()


def searchTodayOrder2():
    time.sleep(2)
    todayTimeTag2 = driver2.find_element_by_id('OrderFromTextBox')

    todayTimeTag2.clear()
    time.sleep(1)

    todayTimeTag2.send_keys(todayDate)
    time.sleep(1)

    listOrdersBtn2 = driver2.find_element_by_id("ListOrdersButton")
    listOrdersBtn2.click()


def searchTodayOrder3():
    time.sleep(2)
    todayTimeTag2 = driver3.find_element_by_id('OrderFromTextBox')

    todayTimeTag2.clear()
    time.sleep(1)

    todayTimeTag2.send_keys(todayDate)
    time.sleep(1)

    listOrdersBtn2 = driver3.find_element_by_id("ListOrdersButton")
    listOrdersBtn2.click()


def execScraping1():
    print "START SCRAPING FROM *********************************************************************************"
    shopState = calcRealDate()
    if shopState:
        searchTodayOrder1()
        time.sleep(2)

        try:
            orderCnt = 0
            orderCntText = driver1.find_element_by_css_selector('#PageInfo').text

            orderTotalStrList = orderCntText.split()
            if orderTotalStrList[2] != "":
                totalOrderCNT = float(orderTotalStrList[2])
                orderCnt = int(math.ceil(totalOrderCNT / 15))

            print ("page count is " + repr(orderCnt))
            # pagination Loop
            for pageIndex in range(orderCnt):
                paginationURL = siteurl1 + "Orders/OrdersBetweenDates/" + todayDateURL + "/1d?pageIndex=%i" % pageIndex
                driver1.get(paginationURL)

                orderList = driver1.find_elements_by_css_selector('#OrderHistoryTable tbody tr')
                length1 = orderList.__len__()

                orderItemNo = 0
                # search page
                for index in range(length1):

                    orderItem = orderList[index]
                    print ("order item number" + repr(orderItemNo))

                    orderItemClass = orderItem.get_attribute('className')

                    if orderItemClass.find('orderDetailsRow') == -1:

                        # get order simple information
                        orderInfoTag = orderItem.find_elements_by_css_selector('td')
                        orderDateValue = orderInfoTag[0].get_attribute('innerHTML')
                        orderTimeValue = orderInfoTag[1].get_attribute('innerHTML')
                        orderIDValue = orderInfoTag[2].get_attribute('innerHTML')
                        orderTotalValue = orderInfoTag[3].get_attribute('innerHTML')

                        orderCollectionValue = 1
                        orderCardValue = 1
                        orderCashValue = 1

                        orderCollectionValueHtml = urllib2.unquote(orderInfoTag[5].get_attribute('innerHTML'))
                        orderCardValueHtml = urllib2.unquote(orderInfoTag[6].get_attribute('innerHTML'))
                        orderCashValueHtml = urllib2.unquote(orderInfoTag[7].get_attribute('innerHTML'))

                        if orderCollectionValueHtml.strip() == "":
                            orderCollectionValue = 0

                        if orderCardValueHtml.strip() == "":
                            orderCardValue = 0

                        if orderCashValueHtml.strip() == "":
                            orderCashValue = 0

                        time.sleep(2)
                        # get order details information
                        orderInfoTag[2].click()
                        time.sleep(2)
                        orderDetailViewTag = orderList[orderItemNo + 1].find_element_by_css_selector('td div a')
                        orderDetailViewTag.click()

                        # get order details information
                        restaurentName = driver1.find_element_by_css_selector('.rest-name').get_attribute('innerHTML')

                        tblList = driver1.find_elements_by_css_selector('table')

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

                                if orderPcs != "":
                                    totalOrderPcs = totalOrderPcs + int(orderPcs)

                                print (
                                    "Pcs: " + orderPcs + " Name: " + orderPdtName + " Description: " + orderPdtDescription + " UnitPirce: " + orderPdtUnitPrice + " Total: " + orderPdtTotalPrice)

                        commentInfoText = orderDetailsTbTrTags[
                            orderDetailTableTrLength - customerInfoTableTrLength - 4].find_element_by_css_selector(
                            'td').text

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

                        # return history page
                        time.sleep(2)
                        driver1.back()
                        time.sleep(2)

                    orderItemNo = orderItemNo + 1
                    orderList = driver1.find_elements_by_css_selector('#OrderHistoryTable tbody tr')
        except NoSuchElementException:
            driver1.get(siteurl1 + "Orders/History/")
            pass
    else:
        pass
    Timer(refreshTimeIntVal, execScraping1, ()).start()


def execScraping2():
    shopState = calcRealDate()
    if shopState:
        searchTodayOrder2()
        time.sleep(1)
        print "START SCRAPING FROM *********************************************************************************"
        try:
            orderCnt = 0
            orderCntText = driver2.find_element_by_css_selector('#PageInfo').text

            orderTotalStrList = orderCntText.split()
            if orderTotalStrList[2] != "":
                totalOrderCNT = float(orderTotalStrList[2])
                orderCnt = int(math.ceil(totalOrderCNT / 15))

            print ("page count is " + repr(orderCnt))
            # pagination Loop
            for pageIndex in range(orderCnt):
                paginationURL = siteurl1 + "Orders/OrdersBetweenDates/" + todayDateURL + "/1d?pageIndex=%i" % pageIndex
                driver2.get(paginationURL)

                orderList = driver2.find_elements_by_css_selector('#OrderHistoryTable tbody tr')
                length1 = orderList.__len__()

                orderItemNo = 0
                # search page
                for index in range(length1):

                    orderItem = orderList[index]
                    print ("order item number" + repr(orderItemNo))

                    orderItemClass = orderItem.get_attribute('className')

                    if orderItemClass.find('orderDetailsRow') == -1:

                        # get order simple information
                        orderInfoTag = orderItem.find_elements_by_css_selector('td')
                        orderDateValue = orderInfoTag[0].get_attribute('innerHTML')
                        orderTimeValue = orderInfoTag[1].get_attribute('innerHTML')
                        orderIDValue = orderInfoTag[2].get_attribute('innerHTML')
                        orderTotalValue = orderInfoTag[3].get_attribute('innerHTML')

                        orderCollectionValue = 1
                        orderCardValue = 1
                        orderCashValue = 1

                        orderCollectionValueHtml = urllib2.unquote(orderInfoTag[5].get_attribute('innerHTML'))
                        orderCardValueHtml = urllib2.unquote(orderInfoTag[6].get_attribute('innerHTML'))
                        orderCashValueHtml = urllib2.unquote(orderInfoTag[7].get_attribute('innerHTML'))

                        if orderCollectionValueHtml.strip() == "":
                            orderCollectionValue = 0

                        if orderCardValueHtml.strip() == "":
                            orderCardValue = 0

                        if orderCashValueHtml.strip() == "":
                            orderCashValue = 0

                        time.sleep(2)
                        # get order details information
                        orderInfoTag[2].click()
                        time.sleep(2)
                        orderDetailViewTag = orderList[orderItemNo + 1].find_element_by_css_selector('td div a')
                        orderDetailViewTag.click()

                        # get order details information
                        restaurentName = driver2.find_element_by_css_selector('.rest-name').get_attribute('innerHTML')

                        tblList = driver2.find_elements_by_css_selector('table')

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

                                if orderPcs != "":
                                    totalOrderPcs = totalOrderPcs + int(orderPcs)

                                print (
                                    "Pcs: " + orderPcs + " Name: " + orderPdtName + " Description: " + orderPdtDescription + " UnitPirce: " + orderPdtUnitPrice + " Total: " + orderPdtTotalPrice)

                        commentInfoText = orderDetailsTbTrTags[
                            orderDetailTableTrLength - customerInfoTableTrLength - 4].find_element_by_css_selector(
                            'td').text

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

                        # return history page
                        time.sleep(2)
                        driver2.back()
                        time.sleep(2)

                    orderItemNo = orderItemNo + 1
                    orderList = driver2.find_elements_by_css_selector('#OrderHistoryTable tbody tr')
        except NoSuchElementException:
            driver2.get(siteurl1 + "Orders/History/")
            pass
    else:
        pass

    Timer(refreshTimeIntVal, execScraping2, ()).start()


def execScraping3():
    shopState = calcRealDate()
    if shopState:
        searchTodayOrder3()
        print "START SCRAPING FROM *********************************************************************************"
        orderCnt = 0
        try:
            orderCntText = driver3.find_element_by_css_selector('#PageInfo').text
            orderTotalStrList = orderCntText.split()
            if orderTotalStrList[2] != "":
                totalOrderCNT = float(orderTotalStrList[2])
                orderCnt = int(math.ceil(totalOrderCNT / 15))

            print ("page count is " + repr(orderCnt))
            # pagination Loop
            for pageIndex in range(orderCnt):
                paginationURL = siteurl1 + "Orders/OrdersBetweenDates/" + todayDateURL + "/1d?pageIndex=%i" % pageIndex
                driver3.get(paginationURL)

                orderList = driver3.find_elements_by_css_selector('#OrderHistoryTable tbody tr')
                length1 = orderList.__len__()

                orderItemNo = 0
                # search page
                for index in range(length1):

                    orderItem = orderList[index]
                    print ("order item number" + repr(orderItemNo))

                    orderItemClass = orderItem.get_attribute('className')

                    if orderItemClass.find('orderDetailsRow') == -1:

                        # get order simple information
                        orderInfoTag = orderItem.find_elements_by_css_selector('td')
                        orderDateValue = orderInfoTag[0].get_attribute('innerHTML')
                        orderTimeValue = orderInfoTag[1].get_attribute('innerHTML')
                        orderIDValue = orderInfoTag[2].get_attribute('innerHTML')
                        orderTotalValue = orderInfoTag[3].get_attribute('innerHTML')

                        orderCollectionValue = 1
                        orderCardValue = 1
                        orderCashValue = 1

                        orderCollectionValueHtml = urllib2.unquote(orderInfoTag[5].get_attribute('innerHTML'))
                        orderCardValueHtml = urllib2.unquote(orderInfoTag[6].get_attribute('innerHTML'))
                        orderCashValueHtml = urllib2.unquote(orderInfoTag[7].get_attribute('innerHTML'))

                        if orderCollectionValueHtml.strip() == "":
                            orderCollectionValue = 0

                        if orderCardValueHtml.strip() == "":
                            orderCardValue = 0

                        if orderCashValueHtml.strip() == "":
                            orderCashValue = 0

                        time.sleep(2)
                        # get order details information
                        orderInfoTag[2].click()
                        time.sleep(2)
                        orderDetailViewTag = orderList[orderItemNo + 1].find_element_by_css_selector('td div a')
                        orderDetailViewTag.click()

                        # get order details information
                        restaurentName = driver3.find_element_by_css_selector('.rest-name').get_attribute('innerHTML')

                        tblList = driver3.find_elements_by_css_selector('table')

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

                                if orderPcs != "":
                                    totalOrderPcs = totalOrderPcs + int(orderPcs)

                                print (
                                    "Pcs: " + orderPcs + " Name: " + orderPdtName + " Description: " + orderPdtDescription + " UnitPirce: " + orderPdtUnitPrice + " Total: " + orderPdtTotalPrice)

                        commentInfoText = orderDetailsTbTrTags[
                            orderDetailTableTrLength - customerInfoTableTrLength - 4].find_element_by_css_selector(
                            'td').text

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

                        # return history page
                        time.sleep(2)
                        driver3.back()
                        time.sleep(2)

                    orderItemNo = orderItemNo + 1
                    orderList = driver3.find_elements_by_css_selector('#OrderHistoryTable tbody tr')
        except NoSuchElementException:
            driver3.get(siteurl1 + "Orders/History")
            pass
    else:
        pass

    Timer(refreshTimeIntVal, execScraping2, ()).start()


def execScraping4():
    shopXPATHList = [
        '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[3]',  # CHICKOS shop
        '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[4]',  # SPECIAL ONE shop
        '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[5]',  # NOM NOM KITCHEN shop
        '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[6]',  # PUNJAB CATERING shop
    ]
    shopNameList = [
        'CHICKOS shop',  # CHICKOS shop
        'SPECIAL ONE shop',  # SPECIAL ONE shop
        'NOM NOM KITCHEN shop',  #
        'PUNJAB CATERING shop',  #
    ]
    for shopIndex in range(4):

        print (
        "*******************************" + "Searching " + shopNameList[shopIndex] + "*******************************")

        time.sleep(5)
        shopNameTag = driver4.find_element_by_xpath(shopXPATHList[shopIndex])
        shopNameTag.click()
        # hide alert box
        time.sleep(4)

        try:
            driver4.find_element_by_xpath(
                '/html/body/div[2]/div/div[1]/div/div/div[2]/button[1]').click()  # Recent Order Page
        except NoSuchElementException:
            pass

        # open full order page
        time.sleep(6)
        driver4.find_element_by_xpath('//*[@id="app"]/div/main/div/div[1]/div[3]/div[3]/div[1]/div[2]/button').click()

        # Loop order summary items
        # orderList = driver4.find_element_by_css_selector('.page').find_elements_by_css_selector('.main div div div')
        time.sleep(4)
        orderList = driver4.find_elements_by_xpath('//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div')
        orderSize = orderList.__len__()

        # *****************************Get Order Detail Information****************************************************#
        # get order number
        for orderIndex in range(orderSize):

            time.sleep(2)
            # order Time
            orderTimeTags = orderList[orderIndex].find_element_by_css_selector('span span')
            orderTime = orderTimeTags.text
            print ("This order info :" + repr(orderTime))
            # order ID and order Total Price
            spanTags = orderList[orderIndex].find_elements_by_css_selector('p span')
            spanTagSize = spanTags.__len__()
            orderTotalPrice = ""
            orderID = ""
            if spanTagSize > 1:
                orderTotalPrice = spanTags[0].text
                orderID = spanTags[1].text

            time.sleep(1)
            orderList[orderIndex].click()

            # get order information (total order, comments, customer name,restaurant name)

            # payment status
            time.sleep(2)
            orderStatusStr = driver4.find_element_by_css_selector('div.main h1').text
            orderStatusType = 0
            if orderStatusStr == "Order Confirmed":
                orderStatusType = 1

            # order payment type
            time.sleep(1)

            orderPaymentWrapTag = driver4.find_element_by_xpath(
                '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[2]/div/section[2]/dl[2]/dd')
            orderPaymentStr = orderPaymentWrapTag.text

            orderPaymentType = "Cash"
            if orderPaymentStr == "Prepaid online":
                orderPaymentType = "Card"
            print ("Payment String is: " + orderPaymentType)

            # get customer address and comments
            orderDeliveryWrapTag = driver4.find_element_by_xpath(
                '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[2]/div/section[2]/dl[3]')
            deliveryStrLen = len("Delivery to:")
            orderCustomerAddress = orderDeliveryWrapTag.text
            orderCustomerAddress = orderCustomerAddress[deliveryStrLen:]
            orderComments = ""

            try:
                commentsElem = orderDeliveryWrapTag.find_element_by_tag_name("span")
                orderComments = commentsElem.text
                orderCustomerAddress = orderCustomerAddress.strip()
                cstAddrLen = len(orderCustomerAddress)
                comLen = len(orderComments)
                orderCustomerAddress = orderCustomerAddress[:(cstAddrLen - comLen)]
                orderCustomerAddress = orderCustomerAddress.strip()
                print ("Order Customer Address " + orderCustomerAddress)
                print ("Order Comments**************************" + orderComments)
            except NoSuchElementException:
                pass

            # get all order details
            orderPdtsTblWrapper = driver4.find_element_by_xpath(
                '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[2]/div/section[3]/ul')

            orderPdtList = driver4.find_elements_by_xpath(
                '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[2]/div/section[3]/ul/li')

            totalPdts = 0
            if orderPdtList.__len__() > 1:
                for pdtIndex in range(1, orderPdtList.__len__()):
                    pdtSpanTags = orderPdtList[pdtIndex].find_elements_by_css_selector('span')
                    pdtCnt = pdtSpanTags[0].text.strip()  # product counts
                    pdtCnt = pdtCnt[:len(pdtCnt) - 1]
                    totalPdts = int(pdtCnt)

                    pdtNameInfoWrapper = pdtSpanTags[1].text

                    # *******We can update this part*************#
                    pdtName = pdtNameInfoWrapper
                    pdtDescription = ""
                    pdtPrice = pdtSpanTags[2].text

                    print ("Qty:" + repr(pdtCnt) + ",Item : " + pdtName + ", Price:" + pdtPrice)

            # get order total Price
            orderTotalPriceTag = driver4.find_element_by_xpath(
                '//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div[2]/div/section[3]/div/ul/li[3]/span[2]')
            orderTotalPrice = orderTotalPriceTag.text

            time.sleep(1)
            driver4.back()

            orderList = driver4.find_elements_by_xpath('//*[@id="app"]/div/main/div/div[1]/div[3]/div/div/div')

        print ("order size is :" + repr(orderSize))

        driver4.get(siteurl2 + "select")

    Timer(refreshTimeIntVal, execScraping4, ()).start()

    print ("OPEN https://partner.hungryhouse.co.uk")


def execFullScraping():

    openSite(siteurl1, siteurl2)

    login1(username1, userpass1)
    login2(username2, userpass2)
    login3(username3, userpass3)
    login4(username4, userpass4)

    openOrderPage1()
    openOrderPage2()
    openOrderPage3()

    execScraping4()

    execScraping1()
    execScraping2()
    execScraping3()


def main():

    pass


if __name__ == "__main__":

    main()
