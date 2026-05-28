#!/usr/bin/env python3
"""
Script de renouvellement automatique du fichier M3U TTR.m3u
Renouvelle le fichier tous les 30 minutes pour éviter les écrans noirs sur Tuvimate
"""

import time
import os
import subprocess
from datetime import datetime

# Configuration
REFRESH_INTERVAL = 30 * 60  # 30 minutes en secondes
M3U_FILE = "TTR.m3u"
REPO_PATH = os.path.dirname(os.path.abspath(__file__))

def log_message(message):
    """Affiche un message avec timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def refresh_file():
    """Renouvelle le fichier M3U en le validant"""
    try:
        file_path = os.path.join(REPO_PATH, M3U_FILE)
        
        if not os.path.exists(file_path):
            log_message(f"❌ Erreur: {M3U_FILE} non trouvé")
            return False
        
        # Valide que le fichier M3U est valide
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content.startswith('#EXTM3U'):
                log_message("❌ Erreur: Le fichier n'est pas un M3U valide")
                return False
        
        # Renouvelle le timestamp du fichier (touch)
        os.utime(file_path, None)
        log_message(f"✅ {M3U_FILE} renouvelé avec succès")
        return True
        
    except Exception as e:
        log_message(f"❌ Erreur lors du renouvellement: {e}")
        return False

def push_to_github():
    """Pousse les modifications vers GitHub"""
    try:
        os.chdir(REPO_PATH)
        subprocess.run(['git', 'add', M3U_FILE], check=True)
        subprocess.run(['git', 'commit', '-m', f'Auto-refresh: {M3U_FILE} at {datetime.now()}'], 
                      check=False)  # check=False car pas de changement = rien à commit
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        log_message("✅ Modifications poussées vers GitHub")
        return True
    except Exception as e:
        log_message(f"⚠️  Impossible de pousser vers GitHub: {e}")
        return False

def main():
    """Boucle principale de renouvellement"""
    log_message("🚀 Démarrage du script de renouvellement M3U")
    log_message(f"⏱️  Intervalle de renouvellement: 30 minutes")
    
    try:
        while True:
            log_message("🔄 Renouvellement en cours...")
            refresh_file()
            
            # Optionnel: pousser vers GitHub à chaque renouvellement
            # push_to_github()
            
            log_message(f"⏳ Prochain renouvellement dans 30 minutes...")
            time.sleep(REFRESH_INTERVAL)
            
    except KeyboardInterrupt:
        log_message("⛔ Script arrêté par l'utilisateur")
    except Exception as e:
        log_message(f"❌ Erreur fatale: {e}")

if __name__ == "__main__":
    main()
