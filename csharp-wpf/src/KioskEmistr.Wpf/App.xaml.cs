using System.Windows;
using KioskEmistr.Wpf.Services;

namespace KioskEmistr.Wpf;

public partial class App : Application
{
	private readonly DiagnosticsService _diagnostics = new();

	protected override void OnStartup(StartupEventArgs e)
	{
		base.OnStartup(e);

		DispatcherUnhandledException += (_, args) =>
		{
			_diagnostics.LogException("DispatcherUnhandledException", args.Exception);
			args.Handled = true;
		};

		AppDomain.CurrentDomain.UnhandledException += (_, args) =>
		{
			if (args.ExceptionObject is Exception ex)
			{
				_diagnostics.LogException("AppDomainUnhandledException", ex);
			}
		};

		TaskScheduler.UnobservedTaskException += (_, args) =>
		{
			_diagnostics.LogException("UnobservedTaskException", args.Exception);
			args.SetObserved();
		};
	}
}
