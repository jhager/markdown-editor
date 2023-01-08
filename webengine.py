from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import (
    QWebEnginePage,
    QWebEngineView,
)
from PyQt5.QtGui import QDesktopServices

class MyWebEngineView(QWebEngineView):
    def acceptNavigationRequest(self, url, type, isMainFrame):
        print ("acceptNavigationRequest " + url)
        if type == QWebEnginePage.NavigationTypeLinkClicked:
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(url, type, isMainFrame)

class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        pass
#        print("loading...")
#        print(info.requestUrl()) 

class MyWebEnginePage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
#        print("acceptNavigationRequest for ...")
#        print(url)
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            QDesktopServices.openUrl(url)
            return False
        return QWebEnginePage.acceptNavigationRequest(self, url, _type, isMainFrame)