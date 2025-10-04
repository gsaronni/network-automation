"""
Credential Manager GUI
Author: Gabriele Saronni

PyQt5-based GUI for secure credential collection and pre-flight validation.

Features:
    - Secure password entry (masked input)
    - VPN connectivity check
    - Device authentication pre-validation
    - User-friendly error messaging
    - Prevents execution on connection failures

This GUI ensures all credentials are valid before initiating backup operations,
preventing partial failures and reducing troubleshooting time.
"""

import os
import subprocess
from netmiko import Netmiko
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit,
    QPushButton, QMessageBox, QVBoxLayout, QWidget
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    """
    Main GUI window for credential collection and validation.
    
    Collects three sets of credentials:
        1. Personal AD credentials (for most network devices)
        2. ISE admin credentials (separate admin account)
        3. Backup server credentials (Linux SFTP)
    
    Validates connectivity and authentication before allowing script to proceed.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Backup - Credential Manager")
        self.setGeometry(0, 0, 320, 200)
        
        self.center_window()
        
        # Set custom icon (optional - will fail gracefully if missing)
        icon_path = os.path.join(os.path.dirname(__file__), "backup_icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Create main widget and layout
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Personal credentials
        layout.addWidget(QLabel("Personal Password:"))
        self.personal_psw_entry = QLineEdit()
        self.personal_psw_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.personal_psw_entry)
        
        # ISE admin credentials
        layout.addWidget(QLabel("ISE Admin Password:"))
        self.ise_psw_entry = QLineEdit()
        self.ise_psw_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.ise_psw_entry)
        
        # Backup server credentials
        layout.addWidget(QLabel("Backup Server Password:"))
        self.backup_server_psw_entry = QLineEdit()
        self.backup_server_psw_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.backup_server_psw_entry)
        
        # Submit button
        submit_button = QPushButton("Validate & Start Backup")
        submit_button.clicked.connect(self.validate_and_submit)
        layout.addWidget(submit_button)
        
        self.setCentralWidget(widget)
    
    def center_window(self):
        """Centers the window on the screen."""
        screen_geometry = QApplication.desktop().screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        
        window_width = self.geometry().width()
        window_height = self.geometry().height()
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.setGeometry(x, y, window_width, window_height)
    
    def validate_and_submit(self):
        """
        Validates credentials and connectivity before proceeding.
        
        Pre-flight checks:
            1. VPN connectivity (ping test to backup server)
            2. Network device authentication (Nexus switch)
            3. ISE authentication (ISE appliance)
            4. Backup server authentication (Linux SFTP)
        
        Only proceeds if ALL checks pass. Clears passwords on failure.
        """
        personal_user = os.environ.get("USERNAME", "admin").lower()
        personal_psw = self.personal_psw_entry.text()
        ise_psw = self.ise_psw_entry.text()
        backup_server_psw = self.backup_server_psw_entry.text()
        
        # Check if any password field is empty
        if not personal_psw or not ise_psw or not backup_server_psw:
            QMessageBox.warning(
                self,
                "Missing Credentials",
                "Please fill in all password fields."
            )
            return
        
        # Pre-flight check: VPN connectivity
        print("Checking VPN connectivity...")
        ping_result = subprocess.run(
            ['ping', '-n', '1', '10.0.0.50'],
            capture_output=True,
            timeout=5
        )
        
        if ping_result.returncode != 0:
            QMessageBox.critical(
                self,
                "VPN Connection Required",
                "Cannot reach backup server.\n\n"
                "Please ensure you are connected to VPN before continuing."
            )
            self.clear_password_fields()
            return
        
        # Pre-flight check: Device authentication
        success_messages = []
        error_messages = []
        
        # Test devices (representative sample from each category)
        test_devices = [
            {
                "ip": "10.0.0.10",
                "hostname": "CORE-SW-01",
                "password": personal_psw,
                "username": personal_user,
                "device_type": "cisco_nxos"
            },
            {
                "ip": "10.0.0.20",
                "hostname": "ISE-PRIMARY",
                "password": ise_psw,
                "username": "admin",
                "device_type": "cisco_nxos"
            },
            {
                "ip": "10.0.0.50",
                "hostname": "BACKUP-SERVER",
                "password": backup_server_psw,
                "username": "backupuser",
                "device_type": "linux"
            }
        ]
        
        print("\nValidating credentials...")
        
        for device in test_devices:
            try:
                print(f"Testing connection to {device['hostname']}...")
                
                conn = Netmiko(
                    host=device['ip'],
                    username=device['username'],
                    password=device['password'],
                    device_type=device['device_type'],
                    timeout=30
                )
                
                # Verify connection by retrieving prompt/hostname
                if device['device_type'] == 'linux':
                    prompt = conn.send_command('hostname')
                else:
                    prompt = conn.find_prompt()
                
                conn.disconnect()
                
                success_messages.append(f"✓ {device['hostname']} authenticated")
                print(f"  Success: {device['hostname']} ({prompt.strip()})")
                
            except Exception as e:
                error_messages.append(
                    f"✗ {device['hostname']}: Authentication failed\n"
                    f"  Error: {str(e)[:50]}..."
                )
                print(f"  Failed: {device['hostname']} - {str(e)}")
        
        # Display results
        if error_messages:
            error_text = "\n\n".join(error_messages)
            QMessageBox.critical(
                self,
                "Authentication Failed",
                "One or more devices failed authentication:\n\n" + error_text +
                "\n\nPlease verify your credentials and try again."
            )
            self.clear_password_fields()
        else:
            success_text = "\n".join(success_messages)
            print("\n" + "="*50)
            print("All pre-flight checks passed!")
            print("="*50)
            # Don't show success dialog - just close and proceed
            self.close()
    
    def clear_password_fields(self):
        """Clears all password fields (security measure on failed auth)."""
        self.personal_psw_entry.clear()
        self.ise_psw_entry.clear()
        self.backup_server_psw_entry.clear()


def main():
    """Standalone GUI launcher for testing."""
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
