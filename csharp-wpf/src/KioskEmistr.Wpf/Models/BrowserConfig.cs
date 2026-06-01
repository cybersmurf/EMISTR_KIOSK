namespace KioskEmistr.Wpf.Models;

public sealed class BrowserConfig
{
    public string Title { get; set; } = "KIOSK_EMISTR";
    public string StartUrl { get; set; } = "https://example.com";
    public double Zoom { get; set; } = 1.0;
    public bool KioskMode { get; set; } = true;
    public string[] AllowedOrigins { get; set; } = ["https://example.com"];
    public bool AllowNewTabs { get; set; } = false;
    public bool EnableDevTools { get; set; } = false;
}
