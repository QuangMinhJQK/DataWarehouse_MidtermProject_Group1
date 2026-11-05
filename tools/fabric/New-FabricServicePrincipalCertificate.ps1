[CmdletBinding()]
param(
    [string]$Subject = "CN=FabricDataWarehouseAutomation",
    [int]$YearsValid = 2,
    [string]$PublicCertificatePath = (Join-Path $PSScriptRoot "local\fabric-service-principal.cer")
)

$ErrorActionPreference = "Stop"

if ($YearsValid -lt 1) {
    throw "YearsValid must be at least 1."
}

$certificateDirectory = Split-Path -Parent $PublicCertificatePath
if (-not (Test-Path -LiteralPath $certificateDirectory)) {
    New-Item -ItemType Directory -Path $certificateDirectory -Force | Out-Null
}

$notAfter = (Get-Date).AddYears($YearsValid)
$certificate = New-SelfSignedCertificate `
    -Subject $Subject `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -KeyAlgorithm RSA `
    -KeyLength 2048 `
    -HashAlgorithm SHA256 `
    -KeyExportPolicy NonExportable `
    -NotAfter $notAfter

Export-Certificate `
    -Cert $certificate `
    -FilePath $PublicCertificatePath `
    -Type CERT | Out-Null

[pscustomobject]@{
    Thumbprint = $certificate.Thumbprint
    Subject = $certificate.Subject
    NotAfter = $certificate.NotAfter
    PublicCertificatePath = (Resolve-Path -LiteralPath $PublicCertificatePath).Path
} | Format-List

Write-Host "Upload only the .cer file to the Entra app registration."
Write-Host "The private key remains in Cert:\CurrentUser\My and is not exported."
