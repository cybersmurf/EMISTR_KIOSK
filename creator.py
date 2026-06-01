import sys
import os
import shutil
import subprocess

def create_kiosk_app(app_name, target_url):
    print(f"Creating Kiosk App: {app_name}")
    print(f"Target URL: {target_url}")

    template_file = "browser_template.py"
    if not os.path.exists(template_file):
        print(f"Error: Template file '{template_file}' not found.")
        return

    # Create a temporary script for this specific app
    temp_script = f"{app_name}_script.py"
    
    with open(template_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace the placeholder URL with the actual target URL
    new_content = content.replace('"%URL%"', f'"{target_url}"')
    
    # Also update the window title to match the app name if desired, 
    # though strictly the template sets it to 'Kiosk Browser'. 
    # Let's make it smarter:
    new_content = new_content.replace("title='Kiosk Browser'", f"title='{app_name}'")

    with open(temp_script, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Generated temporary script: {temp_script}")
    print("Compiling with PyInstaller... (This may take a minute)")

    # Run PyInstaller
    # --onefile: Create a single exe
    # --noconsole: Don't show the command prompt window when opening the app
    # --name: The name of the output exe
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name", app_name,
        temp_script
    ]
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild successful!")
        print(f"Your application is located in the 'dist' folder: dist/{app_name}.exe")
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
    finally:
        # Cleanup temporary files
        if os.path.exists(temp_script):
            os.remove(temp_script)
        if os.path.exists(f"{app_name}.spec"):
            os.remove(f"{app_name}.spec")
        # Start cleanup of build folder if wanted, but PyInstaller leaves it by default.
        if os.path.exists("build"):
            shutil.rmtree("build", ignore_errors=True)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python creator.py <AppName> <TargetURL>")
        # Interactive mode fallback
        name = input("Enter App Name: ")
        url = input("Enter Target URL: ")
        if name and url:
            create_kiosk_app(name, url)
        else:
            print("Invalid input.")
    else:
        create_kiosk_app(sys.argv[1], sys.argv[2])
