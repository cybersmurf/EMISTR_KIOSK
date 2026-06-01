using System.Windows;
using KioskEmistr.Wpf.Models;

namespace KioskEmistr.Wpf.Services;

public sealed class KioskWindowService
{
    private readonly BrowserConfig _config;

    public KioskWindowService(BrowserConfig config)
    {
        _config = config;
    }

    public void Apply(Window window)
    {
        if (!_config.KioskMode)
        {
            return;
        }

        window.WindowStyle = WindowStyle.None;
        window.ResizeMode = ResizeMode.NoResize;
        window.WindowState = WindowState.Maximized;
        window.Topmost = true;
        window.ShowInTaskbar = false;
        window.Cursor = System.Windows.Input.Cursors.None;
    }
}
