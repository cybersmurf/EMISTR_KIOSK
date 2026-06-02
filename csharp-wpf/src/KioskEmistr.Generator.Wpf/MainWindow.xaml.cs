using System.IO;
using System.Windows;
using System.Windows.Media;
using KioskEmistr.Core;

namespace KioskEmistr.Generator.Wpf;

public partial class MainWindow : Window
{
    private readonly GeneratorService _generator = new();

    public MainWindow()
    {
        InitializeComponent();
    }

    private async void Generate_Click(object sender, RoutedEventArgs e)
    {
        var appName = TxtAppName.Text.Trim();
        var url     = TxtUrl.Text.Trim();

        if (string.IsNullOrEmpty(appName))
        {
            SetStatus("Zadejte n\u00e1zev aplikace.", error: true);
            TxtAppName.Focus();
            return;
        }

        if (string.IsNullOrEmpty(url))
        {
            SetStatus("Zadejte c\u00edlovou URL.", error: true);
            TxtUrl.Focus();
            return;
        }

        // Runtime je ve vedlejsi slozce 'runtime' vedle generatoru
        var runtimeDir = Path.Combine(
            AppContext.BaseDirectory, "runtime");

        if (!Directory.Exists(runtimeDir))
        {
            SetStatus($"Runtime slo\u017eka nenalezena: {runtimeDir}", error: true);
            return;
        }

        var outputDir = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "kiosk-output");

        BtnGenerate.IsEnabled = false;
        SetStatus("Generuji\u2026", error: false);

        var options = new GeneratorOptions
        {
            AppName          = appName,
            TargetUrl        = url,
            RuntimeSourceDir = runtimeDir,
            OutputDir        = outputDir,
            KioskMode        = true,
            BarcodeScanner   = ParseRs232(TxtBarcodePort.Text, TxtBarcodeBaud.Text),
            RfidReader       = ParseRs232(TxtRfidPort.Text, TxtRfidBaud.Text)
        };

        try
        {
            var outPath = await Task.Run(() => _generator.Generate(options));
            SetStatus($"\u2713  Hotovo: {outPath}", error: false, success: true);
        }
        catch (Exception ex)
        {
            SetStatus($"Chyba: {ex.Message}", error: true);
        }
        finally
        {
            BtnGenerate.IsEnabled = true;
        }
    }

    private void SetStatus(string msg, bool error, bool success = false)
    {
        TxtStatus.Text = msg;
        TxtStatus.Foreground = error   ? Brushes.Crimson
                             : success ? Brushes.Green
                                       : Brushes.Gray;
    }

    private static Rs232DeviceConfig? ParseRs232(string port, string baud)
    {
        var p = port.Trim();
        if (string.IsNullOrEmpty(p)) return null;
        _ = int.TryParse(baud.Trim(), out var b);
        return new Rs232DeviceConfig { Port = p, BaudRate = b > 0 ? b : 9600 };
    }
}
