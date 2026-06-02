namespace KioskEmistr.Core;

public sealed class GeneratorOptions
{
    public required string AppName { get; init; }
    public required string TargetUrl { get; init; }
    public required string RuntimeSourceDir { get; init; }
    public required string OutputDir { get; init; }
    public string? TitleOverride { get; init; }
    public bool KioskMode { get; init; } = true;
    public bool AllowNewTabs { get; init; }
    public bool EnableDevTools { get; init; }
    public Rs232DeviceConfig? BarcodeScanner { get; init; }
    public Rs232DeviceConfig? RfidReader { get; init; }
}
