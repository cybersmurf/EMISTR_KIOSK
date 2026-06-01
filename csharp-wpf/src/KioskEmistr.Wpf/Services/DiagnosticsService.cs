using System;
using System.IO;

namespace KioskEmistr.Wpf.Services;

public sealed class DiagnosticsService
{
    private readonly string _logFilePath;

    public DiagnosticsService()
    {
        var folder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "KIOSK_EMISTR", "logs");
        Directory.CreateDirectory(folder);
        _logFilePath = Path.Combine(folder, "kiosk.log");
    }

    public void Log(string message)
    {
        var line = $"[{DateTime.UtcNow:O}] {message}{Environment.NewLine}";
        File.AppendAllText(_logFilePath, line);
    }

    public void LogException(string context, Exception ex)
    {
        Log($"{context}: {ex}");
    }
}