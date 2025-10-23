# Tools Documentation

This folder contains utility scripts for managing Python environments and MCP configuration.

## Scripts

### 1. setup-mcp.sh (macOS/Linux)

Automatically detects and configures MCP (Model Context Protocol) for the Arize Tracing Assistant in Cursor IDE.

**What it does:**
- Detects Python and uvx installations on your system
- Tests uvx to ensure it works with arize-tracing-assistant
- Generates the proper MCP configuration file at `.cursor/mcp.json`
- Creates a backup of any existing configuration

**Usage:**

```bash
cd /path/to/your/project
./tools/setup-mcp.sh
```

**After running:**
1. Restart Cursor IDE completely
2. Go to Settings → Tools & MCP
3. Verify arize-tracing-assistant appears and is connected

**Requirements:**
- macOS or Linux
- Python 3.9+ installed
- uvx installed (or the script will prompt you to install it)

**Troubleshooting:**
- If uvx is not found, install it with: `pip install uvx`
- If connection fails, check the generated `.cursor/mcp.json` file
- Try using the absolute path suggestion shown at the end of the script

---

### 2. switch-python.ps1 (Windows)

Switches between different Python versions on Windows systems, managing PATH and py launcher configuration.

**What it does:**
- Auto-installs the requested Python version if not present (via winget)
- Configures py launcher to use the specified version as default
- Creates python3.exe for Unix-style compatibility
- Re-orders system PATH to prioritize the selected Python version
- Backs up your current PATH configuration
- Removes other Python versions from PATH (optional)

**Usage:**

```powershell
# Switch to Python 3.13
.\tools\switch-python.ps1 -Version 3.13

# Switch to Python 3.9
.\tools\switch-python.ps1 -Version 3.9

# Switch to Python 3.11 but keep other Python versions in PATH
.\tools\switch-python.ps1 -Version 3.11 -KeepOtherPythonsInPath
```

**After running:**
1. Close and reopen PowerShell to load the new PATH
2. Verify the switch worked:
   ```powershell
   python -V
   python3 -V
   where python
   ```

**Important:**
- Disable Windows Store Python aliases:
  - Go to Settings → Apps → App execution aliases
  - Turn OFF python.exe and python3.exe

**Requirements:**
- Windows 10/11
- PowerShell 5.1 or later
- winget (for auto-installation)

**Generated files:**
- Creates a log file on your Desktop: `SwitchPython_log_YYYYMMDD_HHMMSS.txt`
- Creates a PATH backup on your Desktop: `PATH_backup_YYYYMMDD_HHMMSS.txt`

---

## Support

For issues or questions:
- setup-mcp.sh: Check Cursor IDE MCP documentation
- switch-python.ps1: Created by Aman Khan - The AI PM Playbook Team

## Notes

- Both scripts include safety features like backups and validation
- Both scripts provide detailed output during execution
- Both scripts are designed to be idempotent (safe to run multiple times)
