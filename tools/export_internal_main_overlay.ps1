param(
    [Parameter(Mandatory = $true)]
    [string]$TargetRepo,

    [string]$SourceRepo = (Get-Location).Path,

    [string]$BaseRef = "upstream/main",

    [string]$OverlayRef = "internal/main"
)

$ErrorActionPreference = "Stop"

function Resolve-AbsolutePath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

$sourceRepoPath = Resolve-AbsolutePath $SourceRepo
$targetRepoPath = Resolve-AbsolutePath $TargetRepo

if (-not (Test-Path -LiteralPath $sourceRepoPath)) {
    throw "Source repo path not found: $sourceRepoPath"
}

if (-not (Test-Path -LiteralPath $targetRepoPath)) {
    throw "Target repo path not found: $targetRepoPath"
}

Push-Location $sourceRepoPath
try {
    $gitRoot = git rev-parse --show-toplevel
    if (-not $gitRoot) {
        throw "Not a git repository: $sourceRepoPath"
    }

    $changedFiles = git diff --name-status "$BaseRef..$OverlayRef" | ForEach-Object {
        if (-not $_) { return }
        $parts = $_ -split "\s+"
        if ($parts.Count -lt 2) { return }
        [pscustomobject]@{
            Status = $parts[0]
            Path = $parts[-1]
        }
    }

    if (-not $changedFiles) {
        Write-Host "No changed files found between $BaseRef and $OverlayRef."
        return
    }

    foreach ($entry in $changedFiles) {
        $relativePath = $entry.Path
        $targetFile = Join-Path $targetRepoPath $relativePath
        $targetDir = Split-Path -Parent $targetFile

        switch ($entry.Status) {
            "D" {
                if (Test-Path -LiteralPath $targetFile) {
                    Remove-Item -LiteralPath $targetFile -Force
                    Write-Host "Removed $relativePath"
                }
            }
            default {
                if (-not (Test-Path -LiteralPath $targetDir)) {
                    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
                }
                $content = git show "$OverlayRef:$relativePath"
                if ($LASTEXITCODE -ne 0) {
                    throw "Failed to export $relativePath from $OverlayRef"
                }
                $text = ($content -join [Environment]::NewLine)
                [System.IO.File]::WriteAllText($targetFile, $text, [System.Text.Encoding]::UTF8)
                Write-Host "Exported $relativePath"
            }
        }
    }

    Write-Host "Overlay export complete."
}
finally {
    Pop-Location
}
