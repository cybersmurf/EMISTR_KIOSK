using System;
using System.IO;
using System.Text.Json;
using KioskEmistr.Wpf.Models;

namespace KioskEmistr.Wpf.Services;

public static class ConfigStore
{
    private static readonly JsonSerializerOptions Options = new()
    {
        WriteIndented = true,
        PropertyNameCaseInsensitive = true
    };

    public static BrowserConfig Load()
    {
        foreach (var path in GetCandidatePaths())
        {
            if (!File.Exists(path))
            {
                continue;
            }

            var json = File.ReadAllText(path);
            return JsonSerializer.Deserialize<BrowserConfig>(json, Options) ?? new BrowserConfig();
        }

        return new BrowserConfig();
    }

    public static void Save(BrowserConfig config)
    {
        var path = GetConfigPath();
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        File.WriteAllText(path, JsonSerializer.Serialize(config, Options));
    }

    private static string GetConfigPath()
    {
        var baseFolder = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "KIOSK_EMISTR");
        return Path.Combine(baseFolder, "config.json");
    }

    private static string GetAppSettingsPath()
    {
        return Path.Combine(AppContext.BaseDirectory, "appsettings.json");
    }

    private static IEnumerable<string> GetCandidatePaths()
    {
        yield return GetConfigPath();
        yield return GetAppSettingsPath();
    }
}
