#Requires -Version 5.1
<#
.SYNOPSIS
    Build script for creating the Mindful Organizer MSIX package.

.DESCRIPTION
    This script automates the full build pipeline:
      1. Run PyInstaller to produce the application bundle
      2. Create the MSIX layout directory structure
      3. Copy built application files and assets
      4. Generate PRI (Package Resource Index) resources
      5. Package everything into an .msix file using makeappx.exe
      6. Optionally sign the package with signtool.exe
      7. Optionally validate with the Windows App Certification Kit

.PARAMETER SkipBuild
    Skip the PyInstaller build step (use existing dist output).

.PARAMETER Sign
    Sign the MSIX package after creation. Requires -CertPath.

.PARAMETER CertPath
    Path to the .pfx code-signing certificate.

.PARAMETER CertPassword
    Password for the .pfx certificate. If omitted, you will be prompted.

.PARAMETER Validate
    Run the Windows App Certification Kit after packaging.

.EXAMPLE
    .\build_msix.ps1
    .\build_msix.ps1 -Sign -CertPath ".\cert.pfx"
    .\build_msix.ps1 -SkipBuild -Validate
#>

[CmdletBinding()]
param(
    [switch]$SkipBuild,
    [switch]$Sign,
    [string]$CertPath = "",
    [string]$CertPassword = "",
    [switch]$Validate
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
$ErrorActionPreference = "Stop"

$ProjectRoot    = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$SpecFile       = Join-Path $ProjectRoot "mindful_organizer.spec"
# The spec emits dist/Hearth/hearth.exe (matching AppxManifest Executable="Hearth\hearth.exe").
$DistDir        = Join-Path $ProjectRoot "dist" "Hearth"
$WindowsStore   = Join-Path $ProjectRoot "windows_store"
$AssetsDir      = Join-Path $WindowsStore "assets"
$ManifestFile   = Join-Path $WindowsStore "AppxManifest.xml"

$LayoutDir      = Join-Path $ProjectRoot "msix_layout"
$OutputMsix     = Join-Path $ProjectRoot "dist" "Hearth.msix"

$AppName        = "Hearth"
$AppVersion     = "1.1.0.0"

# Windows SDK paths -- adjust if your SDK is installed elsewhere
$SdkBinRoot     = "C:\Program Files (x86)\Windows Kits\10\bin"
$SdkVersion     = "10.0.22621.0"
$SdkBin         = Join-Path $SdkBinRoot $SdkVersion "x64"
$MakeAppx       = Join-Path $SdkBin "makeappx.exe"
$MakePri        = Join-Path $SdkBin "makepri.exe"
$SignTool       = Join-Path $SdkBin "signtool.exe"
$AppCertKit     = "C:\Program Files (x86)\Windows Kits\10\App Certification Kit\appcert.exe"

# ---------------------------------------------------------------------------
# Helper: write a section header
# ---------------------------------------------------------------------------
function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
}

# ---------------------------------------------------------------------------
# Step 1: Build with PyInstaller
# ---------------------------------------------------------------------------
if (-not $SkipBuild) {
    Write-Step "Step 1: Building application with PyInstaller"

    # Verify PyInstaller is available
    $pyinstaller = Get-Command "pyinstaller" -ErrorAction SilentlyContinue
    if (-not $pyinstaller) {
        Write-Error "PyInstaller not found. Install it with: pip install pyinstaller"
        exit 1
    }

    # Verify the spec file exists
    if (-not (Test-Path $SpecFile)) {
        Write-Error "Spec file not found at: $SpecFile"
        exit 1
    }

    # Clean previous build artifacts
    $buildDir = Join-Path $ProjectRoot "build"
    if (Test-Path $buildDir) {
        Write-Host "Cleaning previous build directory..."
        Remove-Item -Recurse -Force $buildDir
    }
    if (Test-Path $DistDir) {
        Write-Host "Cleaning previous dist output..."
        Remove-Item -Recurse -Force $DistDir
    }

    # Run PyInstaller
    Write-Host "Running PyInstaller with spec file: $SpecFile"
    Push-Location $ProjectRoot
    & pyinstaller --clean --noconfirm $SpecFile
    Pop-Location

    if ($LASTEXITCODE -ne 0) {
        Write-Error "PyInstaller build failed with exit code $LASTEXITCODE"
        exit 1
    }

    # Verify the build output exists
    if (-not (Test-Path $DistDir)) {
        Write-Error "Expected build output not found at: $DistDir"
        exit 1
    }

    Write-Host "PyInstaller build completed successfully." -ForegroundColor Green
}
else {
    Write-Step "Step 1: Skipping PyInstaller build (using existing output)"

    if (-not (Test-Path $DistDir)) {
        Write-Error "No existing build found at: $DistDir. Run without -SkipBuild first."
        exit 1
    }
}

# ---------------------------------------------------------------------------
# Step 2: Create MSIX layout directory
# ---------------------------------------------------------------------------
Write-Step "Step 2: Creating MSIX layout directory"

if (Test-Path $LayoutDir) {
    Write-Host "Removing existing layout directory..."
    Remove-Item -Recurse -Force $LayoutDir
}

New-Item -ItemType Directory -Path $LayoutDir -Force | Out-Null
Write-Host "Layout directory created at: $LayoutDir"

# ---------------------------------------------------------------------------
# Step 3: Copy built application files and assets
# ---------------------------------------------------------------------------
Write-Step "Step 3: Copying files to MSIX layout"

# Copy the PyInstaller output (the entire application bundle)
$appLayoutDir = Join-Path $LayoutDir $AppName
Write-Host "Copying application files to: $appLayoutDir"
Copy-Item -Recurse -Force $DistDir $appLayoutDir

# Copy the AppxManifest.xml to the layout root
Write-Host "Copying AppxManifest.xml..."
Copy-Item -Force $ManifestFile (Join-Path $LayoutDir "AppxManifest.xml")

# Copy visual assets to the layout
$layoutAssetsDir = Join-Path $LayoutDir "assets"
Write-Host "Copying visual assets to: $layoutAssetsDir"
if (Test-Path $AssetsDir) {
    Copy-Item -Recurse -Force $AssetsDir $layoutAssetsDir
}
else {
    Write-Warning "Assets directory not found at: $AssetsDir"
    Write-Warning "Creating placeholder assets directory. You must add required images before submission."
    New-Item -ItemType Directory -Path $layoutAssetsDir -Force | Out-Null
}

Write-Host "File copy complete." -ForegroundColor Green

# ---------------------------------------------------------------------------
# Step 4: Generate PRI (Package Resource Index) resources
# ---------------------------------------------------------------------------
Write-Step "Step 4: Generating Package Resource Index (PRI)"

if (Test-Path $MakePri) {
    # Create the PRI configuration file
    $priConfigFile = Join-Path $LayoutDir "priconfig.xml"

    Push-Location $LayoutDir
    & $MakePri createconfig /cf $priConfigFile /dq en-US /o
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "makepri createconfig failed. PRI generation skipped."
    }
    else {
        # Generate the resources.pri file
        & $MakePri new /pr $LayoutDir /cf $priConfigFile /of (Join-Path $LayoutDir "resources.pri") /o
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "makepri new failed. PRI generation skipped."
        }
        else {
            Write-Host "PRI resources generated successfully." -ForegroundColor Green
        }

        # Clean up the config file (not needed in the final package)
        Remove-Item -Force $priConfigFile -ErrorAction SilentlyContinue
    }
    Pop-Location
}
else {
    Write-Warning "makepri.exe not found at: $MakePri"
    Write-Warning "Ensure the Windows 10 SDK ($SdkVersion) is installed."
    Write-Warning "Skipping PRI generation. The package may not pass Store validation without it."
}

# ---------------------------------------------------------------------------
# Step 5: Create the MSIX package
# ---------------------------------------------------------------------------
Write-Step "Step 5: Creating MSIX package"

# Ensure the output directory exists
$outputDir = Split-Path -Parent $OutputMsix
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

if (Test-Path $MakeAppx) {
    Write-Host "Packaging with makeappx.exe..."
    & $MakeAppx pack /d $LayoutDir /p $OutputMsix /o

    if ($LASTEXITCODE -ne 0) {
        Write-Error "makeappx.exe pack failed with exit code $LASTEXITCODE"
        exit 1
    }

    Write-Host "MSIX package created: $OutputMsix" -ForegroundColor Green
}
else {
    Write-Error @"
makeappx.exe not found at: $MakeAppx

To resolve this, install the Windows 10 SDK:
  1. Open Visual Studio Installer
  2. Select "Individual components"
  3. Search for "Windows 10 SDK ($SdkVersion)"
  4. Install it

Alternatively, install from:
  https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
"@
    exit 1
}

# ---------------------------------------------------------------------------
# Step 6 (Optional): Sign the MSIX package
# ---------------------------------------------------------------------------
if ($Sign) {
    Write-Step "Step 6: Signing MSIX package"

    if (-not (Test-Path $SignTool)) {
        Write-Error "signtool.exe not found at: $SignTool"
        exit 1
    }

    if ([string]::IsNullOrEmpty($CertPath)) {
        Write-Error "Certificate path required for signing. Use -CertPath parameter."
        exit 1
    }

    if (-not (Test-Path $CertPath)) {
        Write-Error "Certificate file not found at: $CertPath"
        exit 1
    }

    $signArgs = @(
        "sign",
        "/fd", "SHA256",
        "/a",
        "/f", $CertPath
    )

    if (-not [string]::IsNullOrEmpty($CertPassword)) {
        $signArgs += "/p"
        $signArgs += $CertPassword
    }

    # Add timestamp server for production signing
    $signArgs += "/tr"
    $signArgs += "http://timestamp.digicert.com"
    $signArgs += "/td"
    $signArgs += "SHA256"

    $signArgs += $OutputMsix

    Write-Host "Signing package..."
    & $SignTool @signArgs

    if ($LASTEXITCODE -ne 0) {
        Write-Error "signtool.exe signing failed with exit code $LASTEXITCODE"
        exit 1
    }

    Write-Host "Package signed successfully." -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "Skipping signing (use -Sign -CertPath <path> to sign)." -ForegroundColor Yellow
    Write-Host "Note: The package must be signed before Store submission or sideloading." -ForegroundColor Yellow
}

# ---------------------------------------------------------------------------
# Step 7 (Optional): Validate with Windows App Certification Kit
# ---------------------------------------------------------------------------
if ($Validate) {
    Write-Step "Step 7: Running Windows App Certification Kit"

    if (Test-Path $AppCertKit) {
        $reportFile = Join-Path $ProjectRoot "dist" "certification_report.xml"

        Write-Host "Running certification tests (this may take several minutes)..."
        & $AppCertKit test -appxpackagepath $OutputMsix -reportoutputpath $reportFile

        if ($LASTEXITCODE -eq 0) {
            Write-Host "Certification tests PASSED." -ForegroundColor Green
        }
        else {
            Write-Warning "Certification tests completed with issues. Review the report at:"
            Write-Warning "  $reportFile"
        }
    }
    else {
        Write-Warning "Windows App Certification Kit not found at: $AppCertKit"
        Write-Warning "Install it from the Windows SDK to run validation."
    }
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Step "Build Complete"

Write-Host "  Application bundle: $DistDir"
Write-Host "  MSIX layout:        $LayoutDir"
Write-Host "  MSIX package:       $OutputMsix"
Write-Host ""

if (-not $Sign) {
    Write-Host "  REMINDER: Sign the package before distribution:" -ForegroundColor Yellow
    Write-Host "    .\build_msix.ps1 -SkipBuild -Sign -CertPath .\your_cert.pfx" -ForegroundColor Yellow
    Write-Host ""
}

if (-not $Validate) {
    Write-Host "  REMINDER: Validate before Store submission:" -ForegroundColor Yellow
    Write-Host "    .\build_msix.ps1 -SkipBuild -Validate" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Done." -ForegroundColor Green
