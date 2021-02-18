
import sys
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.uic import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QAxContainer import *
import datetime
import time

class StockItem():
    def __init__(self):
        self.info = dict()

class Form(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("hello.ui")
        self.ui.setWindowTitle("PyQt5 !")
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.item = dict()
        self.gScrNo1 = "0101"
        self.gScrNo2 = "0102"
        self.gScrNo = self.gScrNo1
        
        ret = self.kiwoom.dynamicCall("CommConnect()")
        self.kiwoom.OnEventConnect.connect(self.eventConnect)
        self.kiwoom.OnReceiveTrData.connect(self.rcvTransData)

        self.ui.funcRun.clicked.connect(self.openApiCallWithWidget)
        self.ui.tranBtn.clicked.connect(self.transactionWithWidget)
        self.ui.reqCode.clicked.connect(self.requestCode)
        self.ui.reqInfo.clicked.connect(self.requestInfo)

        sys.stdout = self
        self.ui.show()
    
    def write(self, text):
        tlog = "[{0}] {1}".format(datetime.datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3], text)
        self.ui.logBox.append(tlog.strip())

    def transactionWithWidget(self):
        self.transactionCall("000660", "opt10001", "하이닉스")

## transaction rotine ##
    def transactionCall(self, itemCode, transCode, reqStr, scrNo = None):
        print("transaction")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", itemCode)
        
        if scrNo == None:
            scrNo = self.gScrNo
            if (self.gScrNo == self.gScrNo1) : 
                self.gScrNo = self.gScrNo2 
            else: 
                self.gScrNo = self.gScrNo1

        self.write("CommRqData({0}, {1}, {2}, {3})".format(reqStr, transCode, 0, scrNo))
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", reqStr, transCode, 0, scrNo)

    def rcvTransData(self, sScrNo, sRQName, sTrCode, sRecordName, sPreNext, nDataLength, sErrorCode, sMessage, sSplmMsg):
        print("rcv transaction data")
        print("recv info  : {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}".format
            (sScrNo, sRQName, sTrCode, sRecordName, sPreNext, nDataLength, sErrorCode, sMessage, sSplmMsg))

        def queryBasicInfo(item) : 
            return self.kiwoom.dynamicCall("GetCommData(QString, QString, long, QString)", sTrCode, "주식기본정보", 0, item).strip()
        
        name = queryBasicInfo("종목명")
        volume = queryBasicInfo("거래량")
        updownrate = queryBasicInfo("등락율")
        cur_cost = queryBasicInfo("현재가")

        self.write("name : {0}, vol : {1}, updown : {2}, cur_cost : {3}".format(name, volume, updownrate, cur_cost))
########################

    def openApiCallWithWidget(self):
        
        funcName = self.ui.function_name.text()
        argu1 = self.ui.argu_1.text()
        
        self.write("openApiCall : {0}, {1}".format(funcName, argu1))
        argu1 = argu1.split(":")
        
        ret = self.kiwoom.dynamicCall(funcName, argu1)
        self.write(ret)

        return ret

    def openApiCall(self, funcName, argu, callback):

        ret = self.kiwoom.dynamicCall(funcName, argu)
        if callback != None:
            callback(ret)
        # self.write(ret)
        return ret

    def requestName(self, code):
        return self.openApiCall("GetMasterCodeName(QString)", code, None)

    def requestCode(self):
        start = time.time()
        def makeItemDic(ret):
            codes = ret.split(";")
            for i in codes:
                self.item[i] = StockItem()
                self.item[i].info["code"] = i
                self.item[i].info["name"] = self.requestName(i)
                # self.write("code : {0}, name : {1}".format(self.item[i].info["code"], self.item[i].info["name"]))

        self.openApiCall("GetCodeListByMarket(QString)", "0", makeItemDic)
        self.openApiCall("GetCodeListByMarket(QString)", "10", makeItemDic)
        self.write(self.item)
        self.write(time.time() - start)
        self.write("=====")
        # for k, v in self.item.items():
        #     self.write("k : {0}, v : {1}".format(k, v.info["name"]))
    
    def requestInfo(self):
        self.write("request Info")
        self.write("item size {0}".format(len(self.item)))
        if len(self.item) == 0:
            return
        
        
    def eventConnect(self, err_code):
        self.write("connect : " + str(err_code))

if __name__ == "__main__" : 
    print("hello python entry main")
    app = QApplication(sys.argv)
    
    win = Form()
    
    print(sys.executable)
    app.exec_()