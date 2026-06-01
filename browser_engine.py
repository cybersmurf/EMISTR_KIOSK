import sys
import os
import json
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMenu
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings


SEPARATOR = b"<<<KIOSK_CONFIG>>>"

def load_config():
    default_config = {
        "title": "Kiosk Browser Template",
        "url": "https://www.google.com",
        "zoom": 1.0
    }
    try:
        exe_path = sys.executable
        with open(exe_path, "rb") as f:
            content = f.read()
        if SEPARATOR in content:
            parts = content.split(SEPARATOR)
            json_bytes = parts[-1]
            try:
                config = json.loads(json_bytes.decode("utf-8"))
                return config
            except Exception as e:
                print(f"Failed to parse config: {e}")
                return default_config
        else:
            return default_config
    except Exception as e:
        print(f"Error reading config: {e}")
        return default_config

class WebEnginePage(QWebEnginePage):
    def __init__(self, parent_browser, profile, parent=None):
        super().__init__(profile, parent)
        self.parent_browser = parent_browser

    def createWindow(self, _type):
        # Called when a script wants to create a new window (e.g. target="_blank")
        return self.parent_browser.create_new_tab()

class WebEngineView(QWebEngineView):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        # Use a custom page to intercept new window creation
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
        # Custom context menu overrides the default one
        menu = QMenu(self)
        reload_action = menu.addAction("↻ Aktualizovat")
        
        # We can add "Zpět" and "Vpřed" if we want, but let's keep it minimal
        # back_action = menu.addAction("Zpět")
        # forward_action = menu.addAction("Vpřed")
        
        action = menu.exec(event.globalPos())
        if action == reload_action:
            self.reload()

class CustomBrowser(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        self.setWindowTitle(self.config.get("title", "Kiosk Browser"))
        self.resize(1200, 800)
        
        self.zoom = self.config.get("zoom", 1.0)
        
        icon_path = None
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "favicon.ico")
        elif os.path.exists("favicon.ico"):
            icon_path = os.path.abspath("favicon.ico")
            
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
            
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        
        # Hide tab bar if only 1 tab
        self.tabs.tabBar().setVisible(False)
        self.tabs.currentChanged.connect(self.update_tab_bar_visibility)
        
        # Whenever a tab is added or removed, update visibility
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        
        self.setCentralWidget(self.tabs)
        
        # Create initial tab
        initial_url = self.config.get("url", "https://example.com")
        self.add_new_tab(QUrl(initial_url), "Hlavní stránka")

    def create_new_tab(self):
        # Called by WebEnginePage when a new window is requested
        view = WebEngineView(self)
        view.setZoomFactor(self.zoom)
        
        i = self.tabs.addTab(view, "Načítání...")
        self.tabs.setCurrentIndex(i)
        
        view.titleChanged.connect(lambda title, view=view: self.update_tab_title(view, title))
        view.iconChanged.connect(lambda icon, view=view: self.update_tab_icon(view, icon))
        view.loadFinished.connect(lambda _, view=view: self.update_tab_title(view, view.title()))
        
        # Handle window.close() from JS
        view.page().windowCloseRequested.connect(lambda: self.close_specific_tab(view))
        
        self.update_tab_bar_visibility()
        return view.page()

    def add_new_tab(self, qurl, label="Nový panel"):
        view = WebEngineView(self)
        view.setUrl(qurl)
        view.setZoomFactor(self.zoom)
        
        i = self.tabs.addTab(view, label)
        self.tabs.setCurrentIndex(i)
        
        view.titleChanged.connect(lambda title, view=view: self.update_tab_title(view, title))
        view.iconChanged.connect(lambda icon, view=view: self.update_tab_icon(view, icon))
        
        # Handle window.close() from JS
        view.page().windowCloseRequested.connect(lambda: self.close_specific_tab(view))
        
        self.update_tab_bar_visibility()

    def update_tab_title(self, view, title):
        i = self.tabs.indexOf(view)
        if i != -1:
            self.tabs.setTabText(i, title[:30] + ("..." if len(title) > 30 else ""))

    def update_tab_icon(self, view, icon):
        i = self.tabs.indexOf(view)
        if i != -1 and not icon.isNull():
            self.tabs.setTabIcon(i, icon)

    def close_specific_tab(self, view):
        i = self.tabs.indexOf(view)
        if i != -1:
            self.close_current_tab(i)

    def close_current_tab(self, i):
        # Don't close the last tab
        if self.tabs.count() > 1:
            view = self.tabs.widget(i)
            self.tabs.removeTab(i)
            view.deleteLater()
            self.update_tab_bar_visibility()
        else:
            # If it's the last tab and JS wants to close it, maybe we just go back to start?
            # Or if it's the main window, we could close the app. 
            # But usually in Kiosk, we stay alive.
            pass
            
    def update_tab_bar_visibility(self):
        if self.tabs.count() > 1:
            self.tabs.tabBar().setVisible(True)
        else:
            self.tabs.tabBar().setVisible(False)
            
    def tab_open_doubleclick(self, i):
        if i == -1:
            # Double clicking on empty tab bar space could open a new tab, but maybe unnecessary here.
            pass

def main():
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
    
    config = load_config()
    browser = CustomBrowser(config)
    browser.showMaximized()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
