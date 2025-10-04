"""
Network Device Backup Orchestrator
Author: Gabriele Saronni

Automated backup solution for multi-vendor network infrastructure.
Supports Cisco Nexus, ASR900, ISE, ASA Firewall (multi-context), and Linux backup servers.

Version History:
- 20220405 v1.0   - Initial release
- 20230120 v4.7   - Auto-discover username, fixed ASR900 timing issues with send_command_timing
- 20230626 v4.8   - Added Ctrl+C exception handling, fixed devices with slow CLI response
- 20230714 v4.9   - Removed GUI dependency for headless operation, added password validation
- 20230908 v5.0   - Fixed ISE timing issues with sleep delays for slow CLI responses

Usage:
    python network-backup-orchestrator.py

Features:
    - Multi-vendor device support (Cisco NX-OS, IOS, ASA, ISE, Linux)
    - Automated SFTP upload to backup server
    - Configuration archival with date-based organization
    - Pre-flight connection validation via GUI
    - ASA multi-context backup support
"""

import time
import os
import shutil
import sys
from datetime import datetime
import paramiko
from netmiko import Netmiko
from credential_manager_gui import QApplication, MainWindow


def archive_backup(path, now):
    """
    Archives today's backups into date-stamped folder.
    
    Creates backup archive directory structure and moves current backups
    into organized historical storage.
    
    Args:
        path: Base path for backup storage
        now: datetime object for folder naming
    """
    dir_name = now.strftime("%Y%m%d_backup")
    archive_path = os.path.join(path, 'backupArchive', dir_name)
    
    try:
        os.makedirs(archive_path)
    except FileExistsError:
        pass
    
    today_backup = os.path.join(path, 'todayBackup')
    files = os.listdir(today_backup)
    
    for file in files:
        src = os.path.join(today_backup, file)
        dst = os.path.join(archive_path, file)
        shutil.move(src, dst)
    
    print(f"Archived {len(files)} backup files to {dir_name}")


def upload_to_server(path, server_ip, linux_user, linux_password, now):
    """
    Uploads configuration backups to remote Linux server via SFTP.
    
    Establishes SSH connection, transfers all files from todayBackup directory,
    and logs the operation for audit purposes.
    
    Args:
        path: Base path containing todayBackup folder
        server_ip: IP address of backup server
        linux_user: SSH username
        linux_password: SSH password
        now: datetime object for log naming
    """
    log_name = now.strftime("%Y%m%d_%H%M%S_paramiko_SFTP.log")
    log_path = os.path.join(path, 'logs', log_name)
    
    paramiko.util.log_to_file(log_path)
    
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=server_ip, username=linux_user, password=linux_password)
    
    print(f"Connection established to backup server {server_ip}")
    
    sftp = ssh_client.open_sftp()
    
    backup_dir = os.path.join(path, 'todayBackup')
    file_count = 0
    
    with os.scandir(backup_dir) as entries:
        for entry in entries:
            if entry.is_file():
                local_path = entry.path
                remote_path = entry.name
                sftp.put(local_path, remote_path)
                file_count += 1
                print(f"Uploaded: {entry.name}")
    
    print(f"Successfully uploaded {file_count} files")
    
    # Verify upload
    stdin, stdout, stderr = ssh_client.exec_command("ls -l")
    print("\nRemote directory listing:")
    print(stdout.read().decode())
    
    sftp.close()
    ssh_client.close()


def write_file(content, filename, path):
    """
    Writes configuration content to backup file.
    
    Args:
        content: Configuration text to write
        filename: Target filename
        path: Base path for backup storage
    """
    file_path = os.path.join(path, 'todayBackup', filename)
    
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(content)
        file.write('\n' + '='*80 + '\n')


def connection_handler(hosts, username, password, commands, timestamp, device_names, path, device_type="cisco_nxos"):
    """
    Connects to network devices and retrieves configurations.
    
    Handles Cisco IOS/NX-OS devices with special timing considerations for
    devices with slow CLI response (e.g., ISE appliances).
    
    Args:
        hosts: List of device IP addresses
        username: SSH username
        password: SSH password
        commands: List of commands to execute
        timestamp: datetime object for filename generation
        device_names: Dictionary mapping IPs to hostnames
        path: Base path for backup storage
        device_type: Netmiko device type string
    """
    for host in hosts:
        hostname = device_names[host]
        filename = timestamp.strftime(f"{hostname}_%Y%m%d_%H%M%S.cfg")
        
        try:
            conn = Netmiko(
                host=host,
                username=username,
                password=password,
                device_type=device_type,
                timeout=90
            )
            
            print(f"Logged into {conn.find_prompt()}")
            
            for command in commands:
                output = conn.send_command_timing(command)
                
                # ISE appliances have slower CLI response times
                # Add delay to ensure complete output capture
                if hostname.startswith("ISE-"):
                    time.sleep(10)
                
                write_file(output, filename, path)
            
            conn.disconnect()
            print(f"Backup completed: {hostname}")
            
        except Exception as e:
            print(f"Error connecting to {hostname} ({host}): {str(e)}")


def asa_connection_handler(username, password, host, commands_system, timestamp, device_names, path):
    """
    Connects to Cisco ASA firewall and backs up multi-context configuration.
    
    ASA firewalls support multiple security contexts (virtual firewalls).
    This function backs up the system configuration and each individual context.
    
    Args:
        username: SSH username
        password: SSH password
        host: ASA management IP
        commands_system: Commands for system context
        timestamp: datetime object for filename generation
        device_names: Dictionary mapping IPs to hostnames
        path: Base path for backup storage
    """
    contexts = ["SYSTEM", "MGMT", "DMZ", "BACKEND", "FRONTEND"]
    hostname = device_names[host]
    
    try:
        conn = Netmiko(
            host=host,
            username=username,
            password=password,
            device_type="cisco_asa"
        )
        
        print(f"Logged into {conn.find_prompt()}")
        
        # Backup system context
        filename = timestamp.strftime(f"{hostname}_%Y%m%d_%H%M%S.cfg")
        for command in commands_system:
            output = conn.send_command(command)
            write_file(output, filename, path)
        
        # Backup each security context
        for context in contexts:
            context_filename = timestamp.strftime(f"{hostname}_{context}_%Y%m%d_%H%M%S.cfg")
            
            conn.send_command(f"changeto context {context}")
            conn.send_command("write memory")
            
            # Get running configuration
            output = conn.send_command_timing("show running-config")
            write_file(output, context_filename, path)
            
            print(f"Backup completed: {hostname} - {context} context")
        
        conn.disconnect()
        
    except Exception as e:
        print(f"Error connecting to ASA {hostname} ({host}): {str(e)}")


def create_folder_structure(path):
    """
    Creates required directory structure for backup operations.
    
    Args:
        path: Base path for backup storage
    """
    folders = ['logs', 'todayBackup', 'backupArchive']
    
    for folder in folders:
        folder_path = os.path.join(path, folder)
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)
            print(f"Created directory: {folder_path}")


def main(timestamp, base_path):
    """
    Main orchestration function for network backup operations.
    
    Workflow:
        1. Create folder structure
        2. Launch GUI for credential input
        3. Connect to devices and retrieve configurations
        4. Upload backups to remote server
        5. Archive old backups
    
    Args:
        timestamp: datetime object for file naming
        base_path: Base path for backup storage
    """
    print("="*80)
    print("Network Device Backup Orchestrator")
    print("Starting backup process...")
    print("="*80)
    
    create_folder_structure(base_path)
    
    # Launch GUI for credential collection
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
    
    # Retrieve credentials from GUI
    personal_user = os.environ.get("USERNAME", "admin").lower()
    personal_password = window.personal_psw_entry.text()
    ise_password = window.ise_psw_entry.text()
    linux_password = window.backup_server_psw_entry.text()
    
    # Device inventory
    device_names = {
        "10.0.0.10": "CORE-SW-01",
        "10.0.0.11": "CORE-SW-02",
        "10.0.0.12": "DIST-SW-01",
        "10.0.0.13": "DIST-SW-02",
        "10.0.0.20": "ISE-PRIMARY",
        "10.0.0.21": "ISE-SECONDARY",
        "10.0.0.30": "ASA-FW-01",
        "10.0.0.31": "ASA-FW-02",
        "10.0.0.40": "EDGE-RTR-01",
        "10.0.0.50": "BACKUP-SERVER"
    }
    
    # Device groups
    nexus_switches = ["10.0.0.10", "10.0.0.12", "10.0.0.13"]
    asr_routers = ["10.0.0.40", "10.0.0.11"]
    ise_appliances = ["10.0.0.20", "10.0.0.21"]
    asa_firewalls = ["10.0.0.30", "10.0.0.31"]
    
    # Commands
    cisco_commands = ["terminal length 0", "show running-config", "exit"]
    asa_commands = ["terminal pager 0", "write memory"]
    
    # Backup server details
    backup_server_ip = "10.0.0.50"
    backup_server_user = "backupuser"
    
    # Execute backups
    print("\n--- Backing up ASR Routers ---")
    connection_handler(asr_routers, personal_user, personal_password, cisco_commands, 
                      timestamp, device_names, base_path, device_type="cisco_ios")
    
    print("\n--- Backing up Nexus Switches ---")
    connection_handler(nexus_switches, personal_user, personal_password, cisco_commands, 
                      timestamp, device_names, base_path, device_type="cisco_nxos")
    
    print("\n--- Backing up ISE Appliances ---")
    connection_handler(ise_appliances, "admin", ise_password, cisco_commands, 
                      timestamp, device_names, base_path, device_type="cisco_nxos")
    
    print("\n--- Backing up ASA Firewalls (Multi-Context) ---")
    for asa in asa_firewalls:
        asa_connection_handler(personal_user, personal_password, asa, asa_commands, 
                              timestamp, device_names, base_path)
    
    print("\n--- Uploading to Backup Server ---")
    upload_to_server(base_path, backup_server_ip, backup_server_user, linux_password, timestamp)
    
    print("\n--- Archiving Previous Backups ---")
    archive_backup(base_path, timestamp)
    
    print("\n" + "="*80)
    print("Backup process completed successfully!")
    print("="*80)


if __name__ == "__main__":
    now = datetime.now()
    local_user = os.environ.get("USERNAME", "admin")
    backup_path = os.path.join("C:\\", "Users", local_user, "Documents", "NetworkBackups")
    
    try:
        main(now, backup_path)
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {str(e)}")
        sys.exit(1)
