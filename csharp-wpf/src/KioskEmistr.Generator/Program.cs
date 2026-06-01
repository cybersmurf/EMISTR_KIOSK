using KioskEmistr.Core;

var parsed = ParseArgs(args);
if (parsed is null)
{
    PrintUsage();
    return 1;
}

try
{
    var service = new GeneratorService();
    var outputPath = service.Generate(parsed);
    Console.WriteLine($"Kiosk package generated at: {outputPath}");
    return 0;
}
catch (Exception ex)
{
    Console.Error.WriteLine($"Generator failed: {ex.Message}");
    return 2;
}

static GeneratorOptions? ParseArgs(string[] args)
{
    var map = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

    for (var i = 0; i < args.Length; i++)
    {
        var key = args[i];
        if (!key.StartsWith("--", StringComparison.Ordinal) || i + 1 >= args.Length)
        {
            continue;
        }

        map[key] = args[++i];
    }

    if (!map.TryGetValue("--app-name", out var appName)
        || !map.TryGetValue("--url", out var url)
        || !map.TryGetValue("--runtime-dir", out var runtimeDir)
        || !map.TryGetValue("--output-dir", out var outputDir))
    {
        return null;
    }

    return new GeneratorOptions
    {
        AppName = appName,
        TargetUrl = url,
        RuntimeSourceDir = runtimeDir,
        OutputDir = outputDir,
        TitleOverride = map.GetValueOrDefault("--title"),
        KioskMode = ParseBool(map, "--kiosk-mode", true),
        AllowNewTabs = ParseBool(map, "--allow-new-tabs", false),
        EnableDevTools = ParseBool(map, "--enable-devtools", false)
    };
}

static bool ParseBool(Dictionary<string, string> map, string key, bool defaultValue)
{
    if (!map.TryGetValue(key, out var value))
    {
        return defaultValue;
    }

    return value.Equals("1", StringComparison.OrdinalIgnoreCase)
        || value.Equals("true", StringComparison.OrdinalIgnoreCase)
        || value.Equals("yes", StringComparison.OrdinalIgnoreCase);
}

static void PrintUsage()
{
    Console.WriteLine("Usage:");
    Console.WriteLine("  KioskEmistr.Generator --app-name <name> --url <targetUrl> --runtime-dir <path> --output-dir <path> [--title <title>] [--kiosk-mode true|false] [--allow-new-tabs true|false] [--enable-devtools true|false]");
}