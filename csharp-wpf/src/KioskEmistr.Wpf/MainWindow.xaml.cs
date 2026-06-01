using System;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows;
using KioskEmistr.Wpf.Models;
using KioskEmistr.Wpf.Services;
using Microsoft.Web.WebView2.Core;

namespace KioskEmistr.Wpf;

public partial class MainWindow : Window
{
    private readonly BrowserConfig _config;
    private readonly BrowserService _browserService = new();
    private readonly DiagnosticsService _diagnostics = new();
    private readonly KioskPolicy _policy;
    private readonly BrowserTabHost _tabHost;
    private readonly KioskWindowService _windowService;
    private readonly KioskShutdownService _shutdownService = new();
    private bool _allowShutdown;

    public MainWindow()
    {
        InitializeComponent();
        _config = ConfigStore.Load();
        _policy = new KioskPolicy(_config);
        _tabHost = new BrowserTabHost(_config, _policy, _browserService, _diagnostics);
        _windowService = new KioskWindowService(_config);
        Title = _config.Title;
        Tabs.ItemsSource = _tabHost.Tabs;
        Loaded += (_, __) => _windowService.Apply(this);
        Closing += (_, e) => e.Cancel = _config.KioskMode && !_allowShutdown;
        Loaded += OnLoaded;
    }

    private async void OnLoaded(object sender, RoutedEventArgs e)
    {
        try
        {
            var tab = _tabHost.OpenInitialTab();
            Tabs.SelectedItem = tab;
            await tab.WebView.EnsureCoreWebView2Async();
        }
        catch (Exception ex)
        {
            _diagnostics.LogException("MainWindow.OnLoaded", ex);
            Title = $"KIOSK_EMISTR - {ex.Message}";
        }
    }

    private void CloseCurrentTab()
    {
        if (Tabs.SelectedItem is not BrowserTab tab)
        {
            return;
        }

        _tabHost.CloseTab(tab);
    }

    private void Window_KeyDown(object sender, KeyEventArgs e)
    {
        if (_policy.IsAdminExitShortcut(e))
        {
            _allowShutdown = true;
            _shutdownService.RequestExit(this);
            return;
        }

        if (_policy.IsCloseTabShortcut(e))
        {
            CloseCurrentTab();
            e.Handled = true;
        }
    }
}
