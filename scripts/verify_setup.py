import os
import sys

# Standard directories and files to verify
REQUIRED_DIRS = [
    "raw/marketing",
    "raw/ai_automation",
    "raw/kasbtech_academy",
    "raw/personal",
    "raw/assets",
    "wiki/marketing/sources",
    "wiki/marketing/concepts",
    "wiki/marketing/entities",
    "wiki/ai_automation/sources",
    "wiki/ai_automation/concepts",
    "wiki/ai_automation/entities",
    "wiki/kasbtech_academy/sources",
    "wiki/kasbtech_academy/concepts",
    "wiki/kasbtech_academy/entities",
    "wiki/personal/sources",
    "wiki/personal/concepts",
    "wiki/personal/entities",
    "_templates",
    ".agents/skills"
]

REQUIRED_FILES = [
    "CLAUDE.md",
    "AGENTS.md",
    "requirements.txt",
    "jarvis.py",
    "_templates/source-note.md",
    "_templates/concept-note.md",
    "_templates/entity-note.md",
    "_templates/topic-note.md",
    "wiki/Welcome.md",
    "wiki/index.md",
    "wiki/log.md",
    "wiki/personal/entities/javoxir_aliyev.md"
]

def verify():
    print("==================================================")
    print("[INFO] Jarvis Tizimini Tekshirish Boshlandi...")
    print("==================================================")
    
    missing_dirs = []
    missing_files = []
    
    # 1. Check directories
    for directory in REQUIRED_DIRS:
        if not os.path.isdir(directory):
            missing_dirs.append(directory)
            
    # 2. Check files
    for filepath in REQUIRED_FILES:
        if not os.path.isfile(filepath):
            missing_files.append(filepath)
            
    # 3. Print Report
    failed = False
    
    if missing_dirs:
        print("[ERROR] Quyidagi papkalar topilmadi:")
        for d in missing_dirs:
            print(f"   - {d}")
        failed = True
    else:
        print("[OK] Barcha kerakli papkalar mavjud.")
        
    if missing_files:
        print("[ERROR] Quyidagi fayllar topilmadi:")
        for f in missing_files:
            print(f"   - {f}")
        failed = True
    else:
        print("[OK] Barcha kerakli konfiguratsiya va shablon fayllari mavjud.")
        
    # Check syntax of jarvis.py
    if os.path.exists("jarvis.py"):
        try:
            import py_compile
            py_compile.compile("jarvis.py", doraise=True)
            print("[OK] jarvis.py kodi sintaktik jihatdan to'g'ri (Python compile OK).")
        except Exception as e:
            print(f"[ERROR] jarvis.py faylida sintaktik xatolik aniqlandi: {str(e)}")
            failed = True
            
    print("==================================================")
    if failed:
        print("[ERROR] TEKSHIRUV MUVAFFAQIYATSIZ YAKUNLANDI.")
        print("Iltimos, yuqoridagi xatoliklarni to'g'rilang.")
        sys.exit(1)
    else:
        print("[SUCCESS] JARVIS SOZLAMALARI MUVAFFAQIYATLI YAKUNLANDI!")
        print("\nIshga tushirish uchun:")
        print("  1. pip install -r requirements.txt")
        print("  2. streamlit run jarvis.py")
        print("==================================================")
        sys.exit(0)

if __name__ == "__main__":
    verify()
