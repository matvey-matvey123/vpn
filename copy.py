import shutil

SOURCE = "working.txt"
FILES = [
    "1019410.txt",
    "1033910.txt",
    "1026810.txt",
    "1080810.txt",
    "1063010.txt",
    "1042310.txt",
    "1061910.txt",
    "1077610.txt",
    "1054310.txt",
    "1016910.txt",
]

for f in FILES:
    shutil.copy(SOURCE, f)
    print(f"Скопировано в {f}")

print("Готово!")
