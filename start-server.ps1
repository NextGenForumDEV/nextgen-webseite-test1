$port = 8080
$root = $PSScriptRoot
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
try {
    $listener.Start()
    Write-Host ""
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "  Server laeuft auf http://localhost:$port/" -ForegroundColor Green
    Write-Host "  Druecke Strg+C zum Beenden" -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host ""
    Start-Process "http://localhost:$port/"

    while ($listener.IsListening) {
        $context = $listener.GetContext()
        $response = $context.Response
        $localPath = $context.Request.Url.LocalPath.Replace('/', '\')
        if ($localPath -eq '\') { $localPath = '\index.html' }
        $filePath = Join-Path $root $localPath

        if (Test-Path $filePath -PathType Leaf) {
            $bytes = [System.IO.File]::ReadAllBytes($filePath)
            $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
            $response.ContentType = switch ($ext) {
                ".html"  { "text/html; charset=utf-8" }
                ".css"   { "text/css; charset=utf-8" }
                ".js"    { "application/javascript; charset=utf-8" }
                ".json"  { "application/json; charset=utf-8" }
                ".png"   { "image/png" }
                ".jpg"   { "image/jpeg" }
                ".jpeg"  { "image/jpeg" }
                ".gif"   { "image/gif" }
                ".svg"   { "image/svg+xml" }
                ".webp"  { "image/webp" }
                ".ico"   { "image/x-icon" }
                ".woff"  { "font/woff" }
                ".woff2" { "font/woff2" }
                default  { "application/octet-stream" }
            }
            $response.ContentLength64 = $bytes.Length
            $response.OutputStream.Write($bytes, 0, $bytes.Length)
            Write-Host "  200 $localPath" -ForegroundColor DarkGray
        } else {
            $response.StatusCode = 404
            $msg = [System.Text.Encoding]::UTF8.GetBytes("404 - Nicht gefunden: $localPath")
            $response.OutputStream.Write($msg, 0, $msg.Length)
            Write-Host "  404 $localPath" -ForegroundColor Red
        }
        $response.Close()
    }
} finally {
    if ($listener.IsListening) { $listener.Stop() }
}
