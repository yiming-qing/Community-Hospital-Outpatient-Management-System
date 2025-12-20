#requires -Version 5.1

param(
  [string]$MySqlHost = '127.0.0.1',
  [int]$MySqlPort = 3306,
  [string]$MySqlUser = 'root',
  [string]$MySqlPassword = '',
  [string]$DatabaseName = 'community_hospital',
  [string]$MySqlExePath = '',
  [switch]$IncludeTestData,
  [switch]$AutoSeed
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info([string]$Message) { Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Warn([string]$Message) { Write-Host "[WARN] $Message" -ForegroundColor Yellow }
function Write-Err([string]$Message) { Write-Host "[ERR ] $Message" -ForegroundColor Red }

function Require-Command([string]$Name, [string]$Hint) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    Write-Err "Missing command: $Name"
    Write-Host $Hint
    exit 1
  }
}

function Resolve-MySqlExe([string]$ExplicitPath) {
  if ($ExplicitPath) {
    if (-not (Test-Path $ExplicitPath)) {
      throw "MySqlExePath not found: $ExplicitPath"
    }
    return (Resolve-Path $ExplicitPath).Path
  }

  $cmd = Get-Command "mysql" -ErrorAction SilentlyContinue
  if ($cmd) {
    return $cmd.Source
  }

  $candidates = @(
    "$env:ProgramFiles\\MySQL\\MySQL Server*\\bin\\mysql.exe",
    "$env:ProgramFiles (x86)\\MySQL\\MySQL Server*\\bin\\mysql.exe",
    "$env:ProgramFiles\\MariaDB*\\bin\\mysql.exe",
    "$env:ProgramFiles (x86)\\MariaDB*\\bin\\mysql.exe",
    "C:\\xampp\\mysql\\bin\\mysql.exe",
    "C:\\wamp64\\bin\\mysql\\mysql*\\bin\\mysql.exe"
  )
  foreach ($glob in $candidates) {
    $found = Get-ChildItem -Path $glob -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { return $found.FullName }
  }

  return $null
}

function Update-EnvFile([string]$Path, [hashtable]$Pairs) {
  $lines = @()
  if (Test-Path $Path) {
    $lines = Get-Content -LiteralPath $Path -Encoding UTF8
  }

  foreach ($key in $Pairs.Keys) {
    $value = [string]$Pairs[$key]
    $pattern = "^\s*$([Regex]::Escape($key))\s*="
    $idx = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
      if ($lines[$i] -match $pattern) { $idx = $i; break }
    }
    if ($idx -ge 0) {
      $lines[$idx] = "$key=$value"
    } else {
      $lines += "$key=$value"
    }
  }

  $dir = Split-Path -Parent $Path
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
  Set-Content -LiteralPath $Path -Value $lines -Encoding UTF8
}

function Run-MySqlFile([string]$SqlPath, [string]$Password, [string]$ServerHost, [int]$Port, [string]$User) {
  if (-not (Test-Path $SqlPath)) {
    throw "SQL file not found: $SqlPath"
  }

  $args = @(
    "--protocol=tcp",
    "-h", $ServerHost,
    "-P", "$Port",
    "-u", $User,
    "--default-character-set=utf8mb4"
  )

  Write-Info "Running SQL: $SqlPath"

  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $script:MySqlExe
  $psi.Arguments = ($args | ForEach-Object { if ($_ -match '\s') { '"' + ($_ -replace '"', '\"') + '"' } else { $_ } }) -join ' '
  $psi.UseShellExecute = $false
  $psi.RedirectStandardInput = $true
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true

  $proc = New-Object System.Diagnostics.Process
  $proc.StartInfo = $psi

  $oldPwd = $env:MYSQL_PWD
  try {
    if ($Password) { $env:MYSQL_PWD = $Password }

    if (-not $proc.Start()) {
      throw "Failed to start mysql process."
    }

    # IMPORTANT: write raw bytes to stdin, do NOT pipe strings (PowerShell pipes UTF-16 by default).
    $bytes = [System.IO.File]::ReadAllBytes($SqlPath)
    $proc.StandardInput.BaseStream.Write($bytes, 0, $bytes.Length)
    $proc.StandardInput.Close()

    $stdout = $proc.StandardOutput.ReadToEnd()
    $stderr = $proc.StandardError.ReadToEnd()
    $proc.WaitForExit()

    if ($stdout) { Write-Host $stdout }
    if ($stderr) { Write-Host $stderr }
    if ($proc.ExitCode -ne 0) {
      throw "mysql exited with code $($proc.ExitCode)."
    }
  } finally {
    if ($null -eq $oldPwd) {
      Remove-Item Env:MYSQL_PWD -ErrorAction SilentlyContinue
    } else {
      $env:MYSQL_PWD = $oldPwd
    }
  }
}

try {
  $root = $PSScriptRoot
  if (-not $root) { $root = (Get-Location).Path }

  Write-Info "Project root: $root"

  $script:MySqlExe = Resolve-MySqlExe $MySqlExePath
  if (-not $script:MySqlExe) {
    Write-Err "Missing command: mysql"
    Write-Host "Fix options:"
    Write-Host "1) Install MySQL 8.0 Server/Client, then add its bin to PATH (e.g. C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin)"
    Write-Host "2) Or re-run with: -MySqlExePath \"C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysql.exe\""
    exit 1
  }
  Write-Info "Using mysql: $script:MySqlExe"

  Require-Command -Name "python" -Hint "Install Python 3 and make sure python is in PATH."
  Require-Command -Name "npm" -Hint "Install Node.js (with npm) and make sure npm is in PATH."

  $schema = Join-Path $root "database\schema.sql"
  $initData = Join-Path $root "database\init_data.sql"
  $testData = Join-Path $root "database\test_data.sql"

  if ($DatabaseName -ne 'community_hospital') {
    Write-Warn "DatabaseName is overridden to 'community_hospital' (SQL scripts use this fixed name)."
    $DatabaseName = 'community_hospital'
  }

  if (-not $PSBoundParameters.ContainsKey('MySqlPassword')) {
    $sec = Read-Host -Prompt "MySQL password (leave blank if none)" -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    try {
      $MySqlPassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    } finally {
      [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
  }

  # 1) Init database
  Write-Info "Init MySQL: $MySqlUser@${MySqlHost}:$MySqlPort / DB=$DatabaseName"
  if ($PSBoundParameters.ContainsKey('MySqlPassword') -and $MySqlPassword) {
    Write-Warn "You passed -MySqlPassword; it may appear in PowerShell history and will be written to backend/.env (plaintext)."
  }
  Run-MySqlFile -SqlPath $schema -Password $MySqlPassword -ServerHost $MySqlHost -Port $MySqlPort -User $MySqlUser
  Run-MySqlFile -SqlPath $initData -Password $MySqlPassword -ServerHost $MySqlHost -Port $MySqlPort -User $MySqlUser
  if ($IncludeTestData) {
    Run-MySqlFile -SqlPath $testData -Password $MySqlPassword -ServerHost $MySqlHost -Port $MySqlPort -User $MySqlUser
  }

  # 2) Write backend/.env for MySQL
  $backendEnv = Join-Path $root "backend\.env"
  $userEnc = [System.Uri]::EscapeDataString($MySqlUser)
  $passEnc = [System.Uri]::EscapeDataString($MySqlPassword)
  $dbEnc = [System.Uri]::EscapeDataString($DatabaseName)

  $dbUrl = "mysql+pymysql://${userEnc}:${passEnc}@${MySqlHost}:$MySqlPort/${dbEnc}?charset=utf8mb4"
  if (-not $MySqlPassword) {
    Write-Warn "No MySQL password provided; backend/.env will use an empty password in DATABASE_URL."
    $dbUrl = "mysql+pymysql://${userEnc}:@${MySqlHost}:$MySqlPort/${dbEnc}?charset=utf8mb4"
  }

  Update-EnvFile -Path $backendEnv -Pairs @{
    "FLASK_ENV" = "development"
    "AUTO_SEED" = ($(if ($AutoSeed) { "1" } else { "0" }))
    "DATABASE_URL" = $dbUrl
    "JWT_SECRET_KEY" = "change-me"
    "SECRET_KEY" = "dev-secret"
  }
  Write-Info "Wrote backend config: $backendEnv"

  # 3) Install backend deps (venv)
  $backendDir = Join-Path $root "backend"
  $venvDir = Join-Path $backendDir ".venv"
  $venvPython = Join-Path $venvDir "Scripts\\python.exe"
  $venvPip = Join-Path $venvDir "Scripts\\pip.exe"

  if (-not (Test-Path $venvPython)) {
    Write-Info "Creating venv: $venvDir"
    Push-Location $backendDir
    python -m venv .venv
    Pop-Location
  }

  Write-Info "Installing backend dependencies (venv)..."
  Push-Location $backendDir
  & $venvPip install -r requirements.txt

  # 4) Start backend (new window)
  $backendCmd = "Set-Location `"$backendDir`"; & `"$venvPython`" run.py"
  Write-Info "Starting backend: http://localhost:5000 ..."
  Start-Process -FilePath "powershell" -ArgumentList @("-NoExit", "-Command", $backendCmd) | Out-Null
  Pop-Location

  # 5) Start frontend (new window)
  Write-Info "Starting frontend: http://localhost:5173 ..."
  $frontendDir = Join-Path $root "frontend"
  if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
    Write-Info "First run: installing frontend dependencies..."
    Push-Location $frontendDir
    npm install
    Pop-Location
  }
  $frontendCmd = "Set-Location `"$frontendDir`"; npm run dev"
  Start-Process -FilePath "powershell" -ArgumentList @("-NoExit", "-Command", $frontendCmd) | Out-Null

  Write-Info "Done: MySQL initialized + backend/frontend started. Close the two new windows to stop."
  Write-Info "Default accounts: admin/admin123, reception/reception123, patient1/patient123"
} catch {
  Write-Err $_.Exception.Message
  exit 1
}
