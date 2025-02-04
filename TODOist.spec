# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['E:\\Repo\\TODOist\\TODOist.py'],
    pathex=[],
    binaries=[],
    datas=[('E:\\Repo\\TODOist\\label_encoder.pkl', '.'), ('E:\\Repo\\TODOist\\onehot_encoder.pkl', '.'), ('E:\\Repo\\TODOist\\svm_model.pkl', '.'), ('E:\\Repo\\TODOist\\tasks.db', '.'), ('E:\\Repo\\TODOist\\vectorizer.pkl', '.'), ('E:\\Repo\\TODOist\\pl_core_news_sm-3.8.0', 'pl_core_news_sm-3.8.0/')],
    hiddenimports=['sklearn','sklearn.feature_extraction.text','sklearn.utils.sparsefuncs'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TODOist',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='E:\\Repo\\TODOist\\icon.ico',  
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TODOist',
)
