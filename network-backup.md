# Network Backup Orchestrator

**Enterprise-grade multi-vendor network configuration backup automation**

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Automated backup solution for heterogeneous network environments, supporting multiple vendor platforms and complex firewall configurations. Built to handle production infrastructure with 10+ network devices across different vendors.

**Key Features:**
- Multi-vendor support (Cisco NX-OS, IOS, ASA, ISE appliances)
- ASA multi-context firewall backup
- Automated SFTP upload to centralized backup server
- Date-based backup archival
- PyQt5 GUI with pre-flight credential validation
- Production-hardened with timing adjustments for slow CLI devices

## The Problem

Managing network backups manually across multiple vendors and device types is:
- **Time-consuming**: Individual SSH sessions to each device
- **Error-prone**: Manual commands risk typos in critical configurations
- **Inconsistent**: Different engineers follow different procedures
- **Unreliable**: No validation that backups actually succeeded

In enterprise environments with Cisco Nexus switches, ASR routers, ISE appliances, and multi-context ASA firewalls, this becomes a significant operational burden.

## The Solution

A unified Python orchestration tool that:
1. **Validates credentials** before attempting any backups (prevents partial failures)
2. **Connects to all devices** sequentially with vendor-appropriate commands
3. **Handles edge cases** like slow CLI response times (ISE appliances)
4. **Backs up complex configurations** including ASA multi-context setups
5. **Uploads to backup server** via secure SFTP
6. **Archives old backups** with date-based organization
7. **Provides clear feedback** on success/failure for each device

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Backup Orchestrator                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Credential  │  │   Device     │  │   Backup     │     │
│  │  Validation  │→ │  Connection  │→ │   Upload     │     │
│  │     (GUI)    │  │   Handler    │  │   (SFTP)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
           ↓                    ↓                    ↓
    ┌──────────┐         ┌──────────┐        ┌──────────┐
    │  Cisco   │         │   Cisco  │        │  Linux   │
    │  Nexus   │         │    ASA   │        │  Backup  │
    │ Switches │         │ Firewall │        │  Server  │
    └──────────┘         └──────────┘        └──────────┘
    ┌──────────┐         ┌──────────┐
    │   Cisco  │         │   Cisco  │
    │    ASR   │         │    ISE   │
    │  Routers │         │ Appliance│
    └──────────┘         └──────────┘
```

## Technical Highlights

### Multi-Vendor Support

Handles vendor-specific quirks and CLI behaviors:
- **Cisco NX-OS**: Nexus switch configurations
- **Cisco IOS**: ASR router configurations  
- **Cisco ASA**: Multi-context firewall backups
- **Cisco ISE**: Identity Services Engine (with timing adjustments)
- **Linux**: Backup server SFTP integration

### ASA Multi-Context Backup

Cisco ASA firewalls support multiple security contexts (virtual firewalls). This tool:
1. Backs up the system configuration
2. Iterates through each context (SYSTEM, MGMT, DMZ, BACKEND, FRONTEND)
3. Changes to each context and captures its unique configuration
4. Saves each context as a separate timestamped file

```python
def asa_connection_handler(...):
    contexts = ["SYSTEM", "MGMT", "DMZ", "BACKEND", "FRONTEND"]
    for context in contexts:
        conn.send_command(f"changeto context {context}")
        output = conn.send_command_timing("show running-config")
        # Save context-specific configuration
```

### Production Hardening

The evolution from v1.0 to v5.0 includes real-world fixes:

**v4.7**: Auto-discovery of username from Windows environment
**v4.8**: Keyboard interrupt handling (Ctrl+C) for graceful shutdown
**v4.9**: Pre-flight credential validation to prevent partial failures
**v5.0**: ISE timing adjustments for devices with slow CLI response

```python
# ISE appliances require additional time for CLI processing
if hostname.startswith("ISE-"):
    time.sleep(10)  # Ensures complete output capture
```

### Pre-Flight Validation

PyQt5 GUI performs comprehensive checks before backup execution:
1. **VPN connectivity check**: Pings backup server
2. **Credential validation**: Tests authentication on sample devices
3. **Error handling**: Clears passwords and displays specific failure reasons
4. **User feedback**: Clear success/error messages

This prevents the frustration of discovering authentication failures halfway through a 20-device backup job.

## Installation

### Prerequisites

- Python 3.7+
- Windows environment (script uses Windows-specific paths)
- VPN access to network infrastructure
- Appropriate SSH credentials for devices

### Required Libraries

```bash
pip install netmiko paramiko PyQt5
```

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/network-backup-orchestrator.git
cd network-backup-orchestrator
```

2. Customize device inventory in `network-backup-orchestrator.py`:
```python
device_names = {
    "10.0.0.10": "YOUR-DEVICE-01",
    "10.0.0.11": "YOUR-DEVICE-02",
    # Add your devices here
}
```

3. Update device groups:
```python
nexus_switches = ["10.0.0.10", "10.0.0.12"]
asr_routers = ["10.0.0.40"]
# Configure your topology
```

## Usage

### Basic Operation

```bash
python network-backup-orchestrator.py
```

### Workflow

1. **Launch**: Script opens PyQt5 credential manager GUI
2. **Enter credentials**: Personal password, ISE admin password, backup server password
3. **Validation**: Automatic pre-flight checks (VPN, authentication)
4. **Backup**: Sequential connection to all configured devices
5. **Upload**: Configurations transferred to backup server via SFTP
6. **Archive**: Previous backups moved to dated archive folder

### Output Structure

```
C:\Users\{username}\Documents\NetworkBackups\
├── todayBackup\              # Current backup files
│   ├── CORE-SW-01_20240310_143022.cfg
│   ├── ISE-PRIMARY_20240310_143045.cfg
│   └── ASA-FW-01_SYSTEM_20240310_143110.cfg
├── backupArchive\            # Historical backups
│   ├── 20240309_backup\
│   ├── 20240308_backup\
│   └── 20240307_backup\
└── logs\                     # SFTP operation logs
    └── 20240310_143022_paramiko_SFTP.log
```

## Configuration

### Device Inventory

Update the `device_names` dictionary with your infrastructure:

```python
device_names = {
    "10.0.0.10": "CORE-SW-01",      # Nexus switch
    "10.0.0.20": "ISE-PRIMARY",     # ISE appliance
    "10.0.0.30": "ASA-FW-01",       # ASA firewall
    # Add your devices
}
```

### ASA Contexts

Modify the `contexts` list for your ASA configuration:

```python
contexts = ["SYSTEM", "MGMT", "DMZ", "BACKEND", "FRONTEND"]
```

### Backup Server

Update SFTP server details:

```python
backup_server_ip = "10.0.0.50"
backup_server_user = "backupuser"
```

## Error Handling

### Common Issues

**VPN Connection Failed**
- Ensure VPN is active before running script
- Verify connectivity: `ping 10.0.0.50`

**Authentication Failed**
- Verify credentials are current
- Check account lockout status
- Confirm ISE uses separate admin password

**ISE Timeout Issues**
- ISE appliances have slow CLI response
- Script includes 10-second delays (v5.0 fix)
- Extend timeout if needed: `timeout=120`

**Partial Backup Completion**
- Check logs in `logs/` directory
- Review specific device error messages
- Verify device accessibility via manual SSH

## Lessons Learned

### What Worked Well

1. **Pre-flight validation prevents wasted time**: Catching auth failures before starting saves 15+ minutes
2. **GUI improves adoption**: Operations team prefers GUI over command-line prompts
3. **Timing adjustments critical**: ISE required v5.0 fix after months of intermittent failures
4. **Multi-context ASA backup**: Often overlooked, but essential for complete firewall recovery

### Production Evolution

The script evolved through real operational challenges:
- **v1.0**: Basic functionality, manual credential entry
- **v4.7**: Username auto-discovery reduced errors
- **v4.8**: Ctrl+C handling after accidental interruptions
- **v4.9**: GUI validation after too many partial backup failures
- **v5.0**: ISE timing fixes after extensive troubleshooting

### Technical Debt

Current limitations (opportunities for improvement):
- **Hardcoded device IPs**: Should use external configuration file (YAML/JSON)
- **Sequential execution**: Parallel connections would reduce runtime
- **Limited error recovery**: Partial failures don't retry
- **No notification system**: Should email on completion/failure
- **Windows-only paths**: Linux/Mac support requires path refactoring

## Future Enhancements

Potential improvements for extended functionality:

- [ ] YAML/JSON configuration file for device inventory
- [ ] Parallel device connections (threading/asyncio)
- [ ] Email notifications on success/failure
- [ ] Automated scheduling (Windows Task Scheduler integration)
- [ ] Diff generation (compare current vs. previous backup)
- [ ] Configuration compliance checking
- [ ] Support for additional vendors (Juniper, Arista, Palo Alto)
- [ ] Web dashboard for backup history
- [ ] Automated restoration workflow

## Use Cases

### Scheduled Backups

Integrate with Windows Task Scheduler for daily/weekly automated backups:

```bash
# Task Scheduler command
python C:\path\to\network-backup-orchestrator.py
```

### Pre-Change Backups

Run before maintenance windows to capture known-good configurations:

```bash
# Manual execution before changes
python network-backup-orchestrator.py
```

### Disaster Recovery

Timestamped backups enable point-in-time restoration:
- Archive structure preserves historical configurations
- SFTP upload ensures off-device storage
- Multi-context ASA backups enable granular recovery

## Contributing

Contributions welcome! Areas of interest:
- Cross-platform path handling (Linux/Mac support)
- Additional vendor support
- Performance improvements (parallel execution)
- Enhanced error recovery

## License

MIT License - See LICENSE file for details

## Author

**Gabriele Saronni**  
Network Engineer & Automation Developer  
[LinkedIn](https://linkedin.com/in/gabriele-s-54514173) | [GitHub](https://github.com/gsaronni)

*Built from real operational needs in enterprise telecommunications infrastructure. Battle-tested in production environments with 10+ devices across multiple vendors.*
