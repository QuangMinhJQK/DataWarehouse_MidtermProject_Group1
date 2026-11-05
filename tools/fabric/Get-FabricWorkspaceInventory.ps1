[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [Guid]$TenantId,
    [Parameter(Mandatory)]
    [Guid]$ApplicationId,
    [Parameter(Mandatory)]
    [string]$CertificateThumbprint,
    [Parameter(Mandatory)]
    [Guid]$WorkspaceId
)

$ErrorActionPreference = "Stop"

Import-Module Az.Accounts -ErrorAction Stop

Connect-AzAccount `
    -ServicePrincipal `
    -Tenant $TenantId `
    -ApplicationId $ApplicationId `
    -CertificateThumbprint $CertificateThumbprint `
    -WarningAction SilentlyContinue | Out-Null

$accessToken = (Get-AzAccessToken -ResourceUrl "https://api.fabric.microsoft.com").Token
if ($accessToken -is [securestring]) {
    $accessToken = [System.Net.NetworkCredential]::new("", $accessToken).Password
}
if ([string]::IsNullOrWhiteSpace($accessToken)) {
    throw "Fabric access token was empty."
}

$headers = @{
    Authorization = "Bearer $accessToken"
}
$uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/items"

try {
    $response = Invoke-RestMethod -Method Get -Uri $uri -Headers $headers -ContentType "application/json"
}
catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    throw "Fabric List Items request failed with HTTP $statusCode. Verify tenant API settings, app permissions, workspace access, and certificate configuration."
}

$items = @($response.value) | ForEach-Object {
    [pscustomobject]@{
        Id = $_.id
        DisplayName = $_.displayName
        Type = $_.type
        WorkspaceId = $WorkspaceId
    }
}

if ($items.Count -eq 0) {
    Write-Output "No Fabric items were returned for workspace $WorkspaceId."
}
else {
    $items | Sort-Object Type, DisplayName | Format-Table -AutoSize
}
