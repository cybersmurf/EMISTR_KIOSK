using System;
using System.Text.Json;
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
    private Rs232Service? _rs232Service;
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
        Closing += (_, e) =>
        {
            e.Cancel = _config.KioskMode && !_allowShutdown;
            if (!e.Cancel) _rs232Service?.Dispose();
        };
        Loaded += OnLoaded;
        _rs232Service = new Rs232Service(_config, _diagnostics, OnScanData);
    }

    private async void OnLoaded(object sender, RoutedEventArgs e)
    {
        try
        {
            var tab = _tabHost.OpenInitialTab();
            Tabs.SelectedItem = tab;
            var env = await BrowserTabHost.EnvironmentTask;
            await tab.WebView.EnsureCoreWebView2Async(env);

            if (!_config.AllowNewTabs)
            {
                Tabs.ApplyTemplate();
                if (Tabs.Template?.FindName("HeaderPanel", Tabs) is UIElement panel)
                {
                    panel.Visibility = Visibility.Collapsed;
                }
            }
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

    private void OnScanData(string data, string source)
    {
        Dispatcher.InvokeAsync(async () =>
        {
            if (Tabs.SelectedItem is not BrowserTab tab) return;
            if (tab.WebView.CoreWebView2 is null) return;
            var escaped = JsonSerializer.Serialize(data);
            await tab.WebView.CoreWebView2.ExecuteScriptAsync(
                $"window.dispatchEvent(new CustomEvent('kioskInput',{{detail:{{value:{escaped},source:'{source}'}}}}))"
            );
        });
    }
}
