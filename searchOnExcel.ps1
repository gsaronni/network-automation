# PowerShell script to check if IPs exist in an Excel file
# Searches all sheets and shows exact locations

# Excel file path 
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$excelFileName = "yourFile.xlsx" 
$excelPath = "C:\Users\yourUser\theRestOfThePath"

# Check if file exists
if (-not (Test-Path $excelPath)) {
    Write-Host "Error: Excel file not found at: $excelPath" -ForegroundColor Red
    Write-Host "Please check the file path and filename." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}

# Get IPs from user
Write-Host "`n=== IP Address Checker ===" -ForegroundColor Cyan
Write-Host "Paste your IP addresses (one per line)" -ForegroundColor Yellow
Write-Host "Press Enter on a blank line when done`n" -ForegroundColor Yellow

$ipsToCheck = @()
do {
    $input = Read-Host
    if ($input -ne "") {
        $ipsToCheck += $input.Trim()
    }
} while ($input -ne "")

if ($ipsToCheck.Count -eq 0) {
    Write-Host "`nNo IPs provided. Exiting." -ForegroundColor Red
    exit
}

Write-Host "`nSearching for $($ipsToCheck.Count) IP(s) in: $excelFileName" -ForegroundColor Cyan
Write-Host "Please wait...`n" -ForegroundColor Yellow

# Create Excel COM object
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false

try {
    $workbook = $excel.Workbooks.Open($excelPath)
    $sheetCount = $workbook.Worksheets.Count
    
    Write-Host "Scanning $sheetCount sheet(s)...`n" -ForegroundColor Cyan
    
foreach ($ip in $ipsToCheck) {
        $found = $false
        $allLocations = @()
        
        # Search through all sheets using Excel's Find method (much faster!)
        for ($sheetIndex = 1; $sheetIndex -le $sheetCount; $sheetIndex++) {
            $worksheet = $workbook.Worksheets.Item($sheetIndex)
            $sheetName = $worksheet.Name
            $usedRange = $worksheet.UsedRange
            
            # Use Excel's Find method
            $firstFound = $usedRange.Find($ip, [Type]::Missing, [Type]::Missing, 1) # 1 = xlWhole (exact match)
            
            if ($firstFound -ne $null) {
                $found = $true
                $currentFound = $firstFound
                $firstAddress = $firstFound.Address()
                
                do {
                    $location = "Sheet: '$sheetName' | Cell: $($currentFound.Address(0,0)) | Row: $($currentFound.Row)"
                    $allLocations += $location
                    
                    # Find next occurrence
                    $currentFound = $usedRange.FindNext($currentFound)
                    
                    # Stop if wrapped around to the first match
                    if ($currentFound -eq $null -or $currentFound.Address() -eq $firstAddress) {
                        break
                    }
                } while ($true)
            }
        }
        
        if ($found) {
            Write-Host "[FOUND] $ip" -ForegroundColor Green
            foreach ($loc in $allLocations) {
                Write-Host "  └─ $loc" -ForegroundColor Gray
            }
        } else {
            Write-Host "[NOT FOUND] $ip" -ForegroundColor Red
        }
        Write-Host ""
    }
}
catch {
    Write-Host "Error: $_" -ForegroundColor Red
}
finally {
    $workbook.Close($false)
    $excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
}

Write-Host "Search complete!" -ForegroundColor Cyan
Read-Host "`nPress Enter to exit"
