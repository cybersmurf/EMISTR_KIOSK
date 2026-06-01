using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using System.Windows.Input;
using KioskEmistr.Wpf.Models;

namespace KioskEmistr.Wpf.Services;

/// <summary>
/// Vyhodnocuje navigační povolení pro kiosk.
/// Podporuje přesné originy, wildcard subdomény (*.example.com)
/// a URL prefix patterny (https://example.com/app/*).
/// </summary>
public sealed class KioskPolicy
{
    private readonly HashSet<string> _exactOrigins;
    private readonly List<Regex> _compiledPatterns;

    public KioskPolicy(BrowserConfig config)
    {
        _exactOrigins = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        _compiledPatterns = new List<Regex>();

        var entries = (config.AllowedOrigins ?? []).ToList();
        if (!string.IsNullOrWhiteSpace(config.StartUrl))
        {
            entries.Add(config.StartUrl);
        }

        foreach (var entry in entries)
        {
            ParseEntry(entry);
        }
    }

    private void ParseEntry(string entry)
    {
        if (string.IsNullOrWhiteSpace(entry)) return;

        // Wildcard subdoména: *.example.com
        if (entry.StartsWith("*.", StringComparison.Ordinal))
        {
            var baseDomain = Regex.Escape(entry[2..]);
            _compiledPatterns.Add(new Regex(
                $@"^https?://([a-zA-Z0-9\-]+\.)*{baseDomain}$",
                RegexOptions.IgnoreCase | RegexOptions.Compiled,
                TimeSpan.FromMilliseconds(50)));
            return;
        }

        // URL prefix pattern: https://example.com/path/*
        if (entry.EndsWith("*", StringComparison.Ordinal))
        {
            var prefix = Regex.Escape(entry[..^1]);
            _compiledPatterns.Add(new Regex(
                $@"^{prefix}.*$",
                RegexOptions.IgnoreCase | RegexOptions.Compiled,
                TimeSpan.FromMilliseconds(50)));
            return;
        }

        // Přesný origin nebo URL — normalizovat na origin
        if (Uri.TryCreate(entry, UriKind.Absolute, out var parsed))
        {
            _exactOrigins.Add(parsed.GetLeftPart(UriPartial.Authority));
        }
        else if (!entry.Contains("://", StringComparison.Ordinal))
        {
            // Holá doména bez schématu — přidat obě varianty
            if (Uri.TryCreate($"https://{entry}", UriKind.Absolute, out var withHttps))
            {
                _exactOrigins.Add(withHttps.GetLeftPart(UriPartial.Authority));
            }
        }
    }

    public bool AllowNavigation(string? uri)
    {
        if (!TryGetUri(uri, out var parsedUri)) return false;
        if (parsedUri.Scheme is not ("http" or "https")) return false;

        var origin = parsedUri.GetLeftPart(UriPartial.Authority);
        if (_exactOrigins.Contains(origin)) return true;

        var fullUrl = parsedUri.AbsoluteUri;
        foreach (var pattern in _compiledPatterns)
        {
            try
            {
                if (pattern.IsMatch(origin) || pattern.IsMatch(fullUrl)) return true;
            }
            catch (RegexMatchTimeoutException)
            {
                // Timeout — odmítnout (bezpečné selhání)
            }
        }

        return false;
    }

    public bool AllowNewWindow(string? uri) => AllowNavigation(uri);

    public bool IsCloseTabShortcut(KeyEventArgs e)
    {
        return e.Key == Key.W && Keyboard.Modifiers.HasFlag(ModifierKeys.Control);
    }

    public bool IsAdminExitShortcut(KeyEventArgs e)
    {
        return e.Key == Key.Q
            && Keyboard.Modifiers.HasFlag(ModifierKeys.Control)
            && Keyboard.Modifiers.HasFlag(ModifierKeys.Shift);
    }

    public bool IsAllowedScheme(string? uri)
    {
        return TryGetUri(uri, out var parsedUri) && parsedUri.Scheme is "http" or "https";
    }

    private static bool TryGetUri(string? uri, out Uri parsedUri)
    {
        return Uri.TryCreate(uri, UriKind.Absolute, out parsedUri!);
    }
}
