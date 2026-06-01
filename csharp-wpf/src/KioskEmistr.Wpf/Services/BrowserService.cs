using System;

namespace KioskEmistr.Wpf.Services;

public sealed class BrowserService
{
    public string NormalizeUrl(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
        {
            return "https://example.com";
        }

        if (!input.Contains("://", StringComparison.Ordinal))
        {
            return $"https://{input}";
        }

        return input;
    }

    public string[] BuildAllowedOrigins(string startUrl, IEnumerable<string>? configuredOrigins)
    {
        var origins = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        if (Uri.TryCreate(startUrl, UriKind.Absolute, out var startUri))
        {
            origins.Add(startUri.GetLeftPart(UriPartial.Authority));
        }

        foreach (var origin in configuredOrigins ?? [])
        {
            if (!Uri.TryCreate(origin, UriKind.Absolute, out var parsedOrigin))
            {
                continue;
            }

            origins.Add(parsedOrigin.GetLeftPart(UriPartial.Authority));
        }

        return origins.ToArray();
    }
}
