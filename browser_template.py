import sys
import os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMenu
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings


# Placeholder URL - this will be replaced by the creator script
TARGET_URL = "%URL%"

class WebEnginePage(QWebEnginePage):
    def __init__(self, parent_browser, profile, parent=None):
        super().__init__(profile, parent)
        self.parent_browser = parent_browser

    def createWindow(self, _type):
        return self.parent_browser.create_new_tab()


class WebEngineView(QWebEngineView):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setPage(WebEnginePage(self.main_window, self.page().profile(), self))
        
        # Optimize page performance settings
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ErrorPageEnabled, True)

        
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        reload_action = menu.addAction("↻ Aktualizovat")
        action = menu.exec(event.globalPos())
        if action == reload_action:
            self.reload()

class CustomBrowser(QMainWindow):
    def __init__(self, url):
        super().__init__()
        
        # `title` is replaced by creator.py, if we want it to. Currently template does title='Kiosk Browser'.
        # creator.py does: new_content = new_content.replace("title='Kiosk Browser'", f"title='{app_name}'")
        # So I will use the same string so creator.py can replace it.
        self.setWindowTitle('Kiosk Browser')
        self.resize(1200, 800)
        
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        
        self.tabs.tabBar().setVisible(False)
        self.tabs.currentChanged.connect(self.update_tab_bar_visibility)
        
        self.setCentralWidget(self.tabs)
        
        self.add_new_tab(QUrl(url), "Hlavní stránka")

    def create_new_tab(self):
        view = WebEngineView(self)
        i = self.tabs.addTab(view, "Načítání...")
        self.tabs.setCurrentIndex(i)
        
        view.titleChanged.connect(lambda title, view=view: self.update_tab_title(view, title))
        view.iconChanged.connect(lambda icon, view=view: self.update_tab_icon(view, icon))
        view.loadFinished.connect(lambda _, view=view: self.update_tab_title(view, view.title()))
        
        self.update_tab_bar_visibility()
        return view.page()

    def add_new_tab(self, qurl, label="Nový panel"):
        view = WebEngineView(self)
        view.setUrl(qurl)
        i = self.tabs.addTab(view, label)
        self.tabs.setCurrentIndex(i)
        
        view.titleChanged.connect(lambda title, view=view: self.update_tab_title(view, title))
        view.iconChanged.connect(lambda icon, view=view: self.update_tab_icon(view, icon))
        
        self.update_tab_bar_visibility()

    def update_tab_title(self, view, title):
        i = self.tabs.indexOf(view)
        if i != -1:
            self.tabs.setTabText(i, title[:30] + ("..." if len(title) > 30 else ""))

    def update_tab_icon(self, view, icon):
        i = self.tabs.indexOf(view)
        if i != -1 and not icon.isNull():
            self.tabs.setTabIcon(i, icon)

    def close_current_tab(self, i):
        if self.tabs.count() > 1:
            view = self.tabs.widget(i)
            self.tabs.removeTab(i)
            view.deleteLater()
            self.update_tab_bar_visibility()
            
    def update_tab_bar_visibility(self):
        if self.tabs.count() > 1:
            self.tabs.tabBar().setVisible(True)
        else:
            self.tabs.tabBar().setVisible(False)

def main():
    if TARGET_URL == "%URL%":
        print("Error: This is a template. Please generate the application using the creator tool.")
        sys.exit(1)

    # Set Chromium command-line optimization flags before QApplication is initialized
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
        "--enable-gpu-rasterization "
        "--enable-oop-rasterization "
        "--enable-zero-copy "
        "--ignore-gpu-blocklist "
        "--enable-webgl "
        "--enable-accelerated-2d-canvas "
        "--num-raster-threads=4 "
        "--enable-fast-unload "
        "--enable-tcp-fastopen "
        "--disable-logging "
        "--log-level=3"
    )

    # Enable hardware acceleration sharing/desktop settings
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL)

    app = QApplication(sys.argv)
    browser = CustomBrowser(TARGET_URL)
    browser.showMaximized()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
