using System.ComponentModel;
using System.Runtime.CompilerServices;
using Microsoft.Web.WebView2.Wpf;

namespace KioskEmistr.Wpf.Models;

public sealed class BrowserTab : INotifyPropertyChanged
{
    private string _title = string.Empty;

    public required string Title
    {
        get => _title;
        set
        {
            if (_title == value)
            {
                return;
            }

            _title = value;
            OnPropertyChanged();
        }
    }

    public required WebView2 WebView { get; init; }
    public bool CanClose { get; init; } = true;

    public event PropertyChangedEventHandler? PropertyChanged;

    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
