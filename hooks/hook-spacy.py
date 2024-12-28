from PyInstaller.utils.hooks import collect_all

# Zbieranie wszystkich zależności dla SpaCy
data = collect_all('spacy')

datas = data[0]
binaries = data[1]
hiddenimports = data[2]