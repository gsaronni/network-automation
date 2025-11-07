# Network Automation Tools

Production automation tools for enterprise network operations. Built to solve real operational challenges in multi-vendor environments.

[![Python 3.7+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Bash](https://img.shields.io/badge/bash-5.0+-green.svg)](https://www.gnu.org/software/bash/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Projects

### 🔧 F5 BigIP Patching Automation
**Bash automation reducing monthly maintenance overhead from 50 minutes to under 1 minute**

Interactive script for bulk enable/disable of F5 LTM nodes during patching windows. Manages 30+ nodes across multiple partitions (BE-PRO, BE-OMT, FE-DMZ) with support for three distinct patching scenarios.

- **Technology**: Bash, F5 tmsh
- **Impact**: ~20 hours saved annually, eliminated manual errors
- **Use Case**: Monthly maintenance window automation

📖 [View detailed documentation](BIG-IP-F5_LTM_nodes.md)

---

### 🌐 Network Backup Orchestrator
**Multi-vendor configuration backup with automated SFTP upload and archival**

Python-based orchestration tool supporting Cisco Nexus, ASR routers, ISE appliances, and ASA multi-context firewalls. Features PyQt5 GUI for credential management with pre-flight validation.

- **Technology**: Python, Netmiko, Paramiko, PyQt5
- **Vendors Supported**: Cisco NX-OS, IOS, ASA, ISE, Linux
- **Features**: Multi-context ASA backup, automated archival, SFTP upload
- **Evolution**: v1.0 → v5.0 (production-hardened through real operational challenges)

📖 [View detailed documentation](network-backup.md)

---

## Quick Start

### F5 Patching Automation
```bash
chmod +x f5-patching-automation.sh
./f5-patching-automation.sh
```

### Network Backup Orchestrator
```bash
pip install -r requirements.txt
python network-backup-orchestrator.py
```

## Requirements

### F5 Script
- Bash 4.0+
- F5 BigIP with tmsh CLI access

### Python Backup Tool
- Python 3.7+
- Network access to devices
- See `requirements.txt` for Python dependencies

## Philosophy

These tools embody practical network automation:
- **Solve real problems**: Built for actual operational pain points
- **Production-ready**: Battle-tested in enterprise environments
- **Maintainable**: Clear code, comprehensive documentation
- **Progressive**: Simple solutions first, complexity only when needed

## Author

**Gabriele Saronni**  
Network Engineer & Automation Developer

[LinkedIn](https://linkedin.com/in/gabriele-s-54514173) | [GitHub](https://github.com/gsaronni)

---

*Tools developed from real operational experience in enterprise telecommunications infrastructure.*
