namespace KioskEmistr.Wpf.Models;

/// <summary>
/// Konfigurace RS232 portu pro čtečku čárových kódů nebo RFID čipů.
/// Port prázdný nebo null = zařízení zakázáno.
/// </summary>
public sealed class Rs232DeviceConfig
{
    /// <summary>Název portu, např. "COM3".</summary>
    public string Port { get; set; } = "";

    /// <summary>Přenosová rychlost. Standard pro většinu čteček je 9600.</summary>
    public int BaudRate { get; set; } = 9600;
}
