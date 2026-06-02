using System;
using System.IO.Ports;
using System.Text;
using KioskEmistr.Wpf.Models;

namespace KioskEmistr.Wpf.Services;

/// <summary>
/// Otevře RS232 porty pro čtečku čárových kódů a RFID čteček.
/// Přečtená data (zakončená CR nebo LF) předá callbacku pro injekci do WebView2.
/// Protokol: 8N1, přenosová rychlost z konfigurace.
/// </summary>
public sealed class Rs232Service : IDisposable
{
    private readonly DiagnosticsService _diagnostics;
    private readonly Action<string, string> _onData;
    private SerialPort? _barcodePort;
    private SerialPort? _rfidPort;
    private readonly StringBuilder _barcodeBuffer = new();
    private readonly StringBuilder _rfidBuffer = new();

    public Rs232Service(BrowserConfig config, DiagnosticsService diagnostics, Action<string, string> onData)
    {
        _diagnostics = diagnostics;
        _onData = onData;
        _barcodePort = OpenPort(config.BarcodeScanner, "barcode", _barcodeBuffer);
        _rfidPort    = OpenPort(config.RfidReader,     "rfid",    _rfidBuffer);
    }

    private SerialPort? OpenPort(Rs232DeviceConfig? cfg, string source, StringBuilder buffer)
    {
        if (cfg is null || string.IsNullOrWhiteSpace(cfg.Port)) return null;
        SerialPort? port = null;
        try
        {
            port = new SerialPort(cfg.Port, cfg.BaudRate, Parity.None, 8, StopBits.One);
            port.DataReceived += (_, _) => OnDataReceived(port, source, buffer);
            port.Open();
            _diagnostics.Log($"RS232 {source}: port {cfg.Port} @ {cfg.BaudRate} bps otevren");
        }
        catch (Exception ex)
        {
            _diagnostics.LogException($"RS232 {source}: nepodarilo se otevrit {cfg?.Port}", ex);
            port?.Dispose();
            port = null;
        }
        return port;
    }

    private void OnDataReceived(SerialPort port, string source, StringBuilder buffer)
    {
        try
        {
            var data = port.ReadExisting();
            string? line = null;
            lock (buffer)
            {
                foreach (var ch in data)
                {
                    if (ch is '\r' or '\n')
                    {
                        var s = buffer.ToString().Trim();
                        buffer.Clear();
                        if (s.Length > 0) line = s;
                    }
                    else
                    {
                        buffer.Append(ch);
                    }
                }
            }
            if (line is not null) _onData(line, source);
        }
        catch (Exception ex)
        {
            _diagnostics.LogException($"RS232 cteni ({source})", ex);
        }
    }

    public void Dispose()
    {
        _barcodePort?.Close();
        _barcodePort?.Dispose();
        _rfidPort?.Close();
        _rfidPort?.Dispose();
    }
}
