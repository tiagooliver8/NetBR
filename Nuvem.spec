# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_submodules

# Adiciona o diretório do UPX ao PATH para garantir que o PyInstaller encontre o UPX.exe
os.environ["PATH"] = r"C:\\Users\\t.lima\\CODING\\upx" + os.pathsep + os.environ.get("PATH", "")

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources/*', 'resources'),
        ('config/conf.json', 'config'),
        ('resources/cloud.ico', '.'),
    ],
    hiddenimports=collect_submodules('PySide6'),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Nuvem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='resources/cloud.ico',
)
