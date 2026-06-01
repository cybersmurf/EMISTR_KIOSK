using System;
using System.Collections.ObjectModel;
using System.Windows;
using KioskEmistr.Wpf.Models;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.Wpf;

namespace KioskEmistr.Wpf.Services;

public sealed class BrowserTabHost
{
    private readonly BrowserConfig _config;
    private readonly KioskPolicy _policy;
    private readonly BrowserService _browserService;
    private readonly DiagnosticsService _diagnostics;
    private readonly ObservableCollection<BrowserTab> _tabs = new();

    public BrowserTabHost(BrowserConfig config, KioskPolicy policy, BrowserService browserService, DiagnosticsService diagnostics)
    {
        _config = config;
        _policy = policy;
        _browserService = browserService;
        _diagnostics = diagnostics;
    }

    public ObservableCollection<BrowserTab> Tabs => _tabs;

    public BrowserTab OpenInitialTab()
    {
        return OpenTab(_browserService.NormalizeUrl(_config.StartUrl), canClose: false);
    }

    public BrowserTab OpenTab(string url, bool canClose = true)
    {
        var normalizedUrl = _browserService.NormalizeUrl(url);
        var webView = new WebView2();
        var tab = new BrowserTab
        {
            Title = _config.Title,
            WebView = webView,
            CanClose = canClose
        };

        webView.CoreWebView2InitializationCompleted += (_, args) =>
        {
            if (!args.IsSuccess || webView.CoreWebView2 is null)
            {
                _diagnostics.Log("WebView initialization failed for tab.");
                return;
            }

            ConfigureWebView(tab);
            webView.ZoomFactor = _config.Zoom;
            webView.CoreWebView2.Settings.AreDefaultContextMenusEnabled = false;
            webView.CoreWebView2.Settings.AreDevToolsEnabled = _config.EnableDevTools;
            webView.CoreWebView2.Settings.AreBrowserAcceleratorKeysEnabled = false;
            webView.CoreWebView2.Settings.AreHostObjectsAllowed = false;
            webView.CoreWebView2.NewWindowRequested += (_, requestArgs) =>
            {
                if (_config.KioskMode && !_policy.AllowNewWindow(requestArgs.Uri))
                {
                    _diagnostics.Log($"Blocked popup or new window: {requestArgs.Uri}");
                    requestArgs.Handled = true;
                    return;
                }

                requestArgs.Handled = true;
                if (_config.AllowNewTabs)
                {
                    Application.Current.Dispatcher.Invoke(() => OpenTab(requestArgs.Uri ?? normalizedUrl));
                }
                else
                {
                    Application.Current.Dispatcher.Invoke(() => webView.CoreWebView2.Navigate(requestArgs.Uri ?? normalizedUrl));
                }
            };

            webView.CoreWebView2.ProcessFailed += (_, processArgs) =>
            {
                _diagnostics.Log($"WebView process failed: {processArgs.ProcessFailedKind}");
                if (webView.CoreWebView2 is not null)
                {
                    webView.CoreWebView2.Navigate(_browserService.NormalizeUrl(_config.StartUrl));
                }
            };
        };

        webView.Loaded += async (_, __) =>
        {
            await webView.EnsureCoreWebView2Async();
            if (webView.CoreWebView2 is not null)
            {
                webView.Source = new Uri(normalizedUrl);
            }
        };

        _tabs.Add(tab);
        return tab;
    }

    public bool CloseTab(BrowserTab tab)
    {
        if (!tab.CanClose || _tabs.Count <= 1)
        {
            return false;
        }

        return _tabs.Remove(tab);
    }

    public BrowserTab? CurrentTab => Application.Current?.MainWindow is null
        ? null
        : _tabs.Count == 0
            ? null
            : _tabs[^1];

    public BrowserTab? TabFor(WebView2 webView)
    {
        foreach (var tab in _tabs)
        {
            if (ReferenceEquals(tab.WebView, webView))
            {
                return tab;
            }
        }

        return null;
    }

    private void ConfigureWebView(BrowserTab tab)
    {
        var webView = tab.WebView;
        if (webView.CoreWebView2 is null)
        {
            return;
        }

        webView.CoreWebView2.NavigationStarting += (_, args) =>
        {
            if (_config.KioskMode && !_policy.AllowNavigation(args.Uri))
            {
                _diagnostics.Log($"Blocked navigation by policy: {args.Uri}");
                args.Cancel = true;
            }
        };

        webView.CoreWebView2.DocumentTitleChanged += (_, __) =>
        {
            if (webView.CoreWebView2 is null)
            {
                return;
            }

            tab.Title = string.IsNullOrWhiteSpace(webView.CoreWebView2.DocumentTitle)
                ? _config.Title
                : webView.CoreWebView2.DocumentTitle;
        };
    }
}
