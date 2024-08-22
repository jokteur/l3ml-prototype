# -*- mode: python ; coding: utf-8 -*-

import sys
sys.setrecursionlimit(5000)
block_cipher = None


a = Analysis(['l3ml.py'],
             pathex=['D:\\Documents\\Chuv\\Work2020\\TestApp'],
             binaries=[],
             datas=[],
             hiddenimports=['pkg_resources.py2_warn', 'pydicom'],
             hookspath=['hook-bokeh.py'],
             runtime_hooks=[],
             excludes=['astropy', 'PyQt5', 'matplotlib'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='l3ml',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='l3ml')
