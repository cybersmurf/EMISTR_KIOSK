using System.Windows;

namespace KioskEmistr.Wpf.Services;

public sealed class KioskShutdownService
{
    public void RequestExit(Window window)
    {
        window.Close();
    }
}