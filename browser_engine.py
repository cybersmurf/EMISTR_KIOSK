import sys
import os
import json
import queue
import threading
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMenu
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings

try:
    import serial
except ImportError:
    serial = None


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


class Rs232Reader:
    """Čte RS232 port v background threadu a vkládá záznamy do fronty."""

    def __init__(self, port, baud_rate, data_queue, source):
        self.port = port
        self.baud_rate = baud_rate
        self.data_queue = data_queue
        self.source = source
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._running = False
        self._buffer = ""

    def start(self):
        self._running = True
        self._thread.start()

    def stop(self):
        self._running = False

    def _run(self):
        try:
            with serial.Serial(self.port, self.baud_rate, timeout=0.1) as ser:
                while self._running:
                    if ser.in_waiting > 0:
                        chunk = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
                        for ch in chunk:
                            if ch in ('\r', '\n'):
                                data = self._buffer.strip()
                                if data:
                                    self.data_queue.put((data, self.source))
                                self._buffer = ""
                            else:
                                self._buffer += ch
        except Exception as e:
            print(f"RS232 chyba na {self.port}: {e}", flush=True)

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

        # RS232 čtečky — inicializace
        self._scan_queue: queue.Queue = queue.Queue()
        self._readers: list = []
        self._setup_rs232(config)
        self._scan_timer = QTimer()
        self._scan_timer.setInterval(50)
        self._scan_timer.timeout.connect(self._process_scan_queue)
        self._scan_timer.start()

    def _setup_rs232(self, config):
        """Inicializuje RS232 čtečky podle konfigurace."""
        if serial is None:
            return
        for key, source in [("barcode_scanner", "barcode"), ("rfid_reader", "rfid")]:
            cfg = config.get(key, {})
            if not cfg:
                continue
            port = cfg.get("port", "").strip()
            baud = cfg.get("baud_rate", 9600)
            if port:
                reader = Rs232Reader(port, baud, self._scan_queue, source)
                reader.start()
                self._readers.append(reader)

    def _process_scan_queue(self):
        """Zavolá se každých 50 ms z hlavního vlákna — zpracuje frontu dat."""
        while not self._scan_queue.empty():
            data, source = self._scan_queue.get_nowait()
            self.inject_scan_data(data, source)

    def inject_scan_data(self, data, source):
        """Odešle přečtenou hodnotu do aktuálního WebView přes CustomEvent."""
        current_index = self.tabs.currentIndex()
        view = self.tabs.widget(current_index)
        if view and isinstance(view, WebEngineView):
            escaped = json.dumps(data)
            js = (
                f"window.dispatchEvent(new CustomEvent('kioskInput',"
                f"{{detail:{{value:{escaped},source:'{source}'}}}}))"
            )
            view.page().runJavaScript(js)

    def closeEvent(self, event):
        for reader in self._readers:
            reader.stop()
        self._scan_timer.stop()
        super().closeEvent(event)

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
