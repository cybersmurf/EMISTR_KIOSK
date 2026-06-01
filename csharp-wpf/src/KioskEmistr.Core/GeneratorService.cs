using System.Text.Json;


namespace KioskEmistr.Core;

public sealed class GeneratorService
{
    private static readonly JsonSerializerOptions JsonOptions = new() { WriteIndented = true };

    public string Generate(GeneratorOptions options)
    {
        if (!Directory.Exists(options.RuntimeSourceDir))
        {
            throw new DirectoryNotFoundException($"Runtime source directory not found: {options.RuntimeSourceDir}");
        }

        var appFolder = Path.Combine(options.OutputDir, options.AppName);
        if (Directory.Exists(appFolder))
        {
            Directory.Delete(appFolder, recursive: true);
        }

        Directory.CreateDirectory(appFolder);
        CopyDirectory(options.RuntimeSourceDir, appFolder);

        var normalizedUrl = NormalizeUrl(options.TargetUrl);
        var config = new
        {
            Title = string.IsNullOrWhiteSpace(options.TitleOverride) ? options.AppName : options.TitleOverride,
            StartUrl = normalizedUrl,
            Zoom = 1.0,
            KioskMode = options.KioskMode,
            AllowedOrigins = new[] { GetOrigin(normalizedUrl) },
            AllowNewTabs = options.AllowNewTabs,
            EnableDevTools = options.EnableDevTools
        };

        var configPath = Path.Combine(appFolder, "appsettings.json");
        File.WriteAllText(configPath, JsonSerializer.Serialize(config, JsonOptions));

        return appFolder;
    }

    public static string NormalizeUrl(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
        {
            throw new ArgumentException("Target URL must not be empty.", nameof(input));
        }

        return input.Contains("://", StringComparison.Ordinal) ? input : $"https://{input}";
    }

    public static string GetOrigin(string url)
    {
        return new Uri(url).GetLeftPart(UriPartial.Authority);
    }

    private static void CopyDirectory(string sourceDir, string destinationDir)
    {
        foreach (var directory in Directory.GetDirectories(sourceDir, "*", SearchOption.AllDirectories))
        {
            var relative = Path.GetRelativePath(sourceDir, directory);
            Directory.CreateDirectory(Path.Combine(destinationDir, relative));
        }

        foreach (var file in Directory.GetFiles(sourceDir, "*", SearchOption.AllDirectories))
        {
            var relative = Path.GetRelativePath(sourceDir, file);
            File.Copy(file, Path.Combine(destinationDir, relative), overwrite: true);
        }
    }
}
