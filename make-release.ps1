# Build everything first:
python -m pip install --target=.\src\lib --force --upgrade pyqtconsole

# Package:
$target = ".\python_debug\"

Remove-Item -Recurse -Force -ErrorAction Ignore $target
New-Item -Path $target -Type Directory | Out-Null
Copy-Item -Force -Recurse -Path .\src\* -Exclude "*.ui", "__pycache__", "history.json" -Destination $target
Copy-Item -Force -Recurse -Path .\res -Destination $target
Copy-Item .\README.md, .\LICENSE $target

# Find the version:
$ctx = Get-Content .\src\__init__.py | Select-String -Pattern "def version\(self\)" -Context 0, 1
$parts = $ctx.Context[0].PostContext.Split("(")[1].Trim(")").Split(",").Trim()
$version = Join-String -Separator "." -InputObject $parts[0..2]

if ($parts[3] -match "ALPHA") {
    $version += "a"
}
if ($parts[3] -match "BETA") {
    $version += "b"
}

# Create the zip:
$archive = "python_debug-$version.zip"
Remove-Item -Force -ErrorAction Ignore $archive
Compress-Archive -Path $target -DestinationPath $archive
Write-Output "Created archive $archive."
