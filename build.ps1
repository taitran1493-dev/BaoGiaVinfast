$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$id = '1MKogwivNMhcznr01LBG71b4Es5keuPvO87EUCl9vKx8'
curl.exe -sL "https://docs.google.com/spreadsheets/d/$id/gviz/tq?tqx=out:csv&sheet=Data" -o data.csv
curl.exe -sL "https://docs.google.com/spreadsheets/d/$id/gviz/tq?tqx=out:csv&sheet=KEY" -o key.csv
$utf8 = New-Object System.Text.UTF8Encoding($false)
$snap = [ordered]@{
  data = [IO.File]::ReadAllText("$PSScriptRoot\data.csv", $utf8)
  key  = [IO.File]::ReadAllText("$PSScriptRoot\key.csv", $utf8)
  at   = (Get-Date -Format 'HH:mm dd/MM/yyyy')
}
$json = ($snap | ConvertTo-Json -Compress) -replace '</', '<\/'
$html = [IO.File]::ReadAllText("$PSScriptRoot\src.html", $utf8)
$html = $html.Replace('/*__SNAPSHOT__*/null', $json)
[IO.File]::WriteAllText("$PSScriptRoot\dashboard.html", $html, $utf8)
"Built dashboard.html ($([math]::Round($html.Length/1KB)) KB)"
