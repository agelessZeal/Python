print "START SCRAPING FROM *********************************************************************************"
shopState = self.calcRealDate()
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
                                    repr(totalOrderPcs), orderTotalValue, "Chicko's Fast Food",
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