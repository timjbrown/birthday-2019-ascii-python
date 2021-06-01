# -*- mode: python -*-

block_cipher = None

added_files = [
    ('level1.txt','.'),
    ('level2.txt','.'),
    ('level3.txt','.'),
    ('level4.txt','.'),
    ('level5.txt','.'),
    ('level6.txt','.'),
    ('level7.txt','.'),
    ('level8.txt','.')
]
a = Analysis(['birthday.py'],
             pathex=['/Users/timbrown/Documents/workspace-python'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='birthday',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
