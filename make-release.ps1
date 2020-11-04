if ((python --version) -match "Python 3.8.") {
    python -m pip install --target=.\lib --force --upgrade pyqtconsole
    zip -qr python-debug.zip .\__init__.py .\lib\ .\res\
}
else {
    Write-Output "Cannot build release without Python 3.8."
}
