#!/usr/bin/env python3
"""
Script pour vérifier et actualiser les liens M3U toutes les heures
"""
import requests
import sys
from datetime import datetime

TIMEOUT = 10
RETRIES = 2

def check_url(url):
    """Vérifie si une URL est accessible"""
    for attempt in range(RETRIES):
        try:
            response = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
            if response.status_code < 400:
                return True
        except requests.exceptions.RequestException:
            pass
        
        try:
            response = requests.get(url, timeout=TIMEOUT, stream=True)
            if response.status_code < 400:
                return True
        except requests.exceptions.RequestException:
            pass
    
    return False

def refresh_m3u(filename):
    """Actualise et valide les liens du fichier M3U"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Fichier {filename} non trouvé")
        return False
    
    working_count = 0
    broken_count = 0
    processed = 0
    new_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        
        if line.startswith('#EXTINF:'):
            new_lines.append(line)
            i += 1
            
            # La ligne suivante devrait être l'URL
            if i < len(lines):
                url_line = lines[i].rstrip('\n').strip()
                
                if url_line and (url_line.startswith('http://') or url_line.startswith('https://')):
                    processed += 1
                    print(f"[{processed}] Vérification: {url_line[:60]}...")
                    
                    if check_url(url_line):
                        print(f"    ✅ OK - Lien valide")
                        working_count += 1
                        new_lines.append(url_line)
                    else:
                        print(f"    ❌ ERREUR - Lien inaccessible")
                        broken_count += 1
                        new_lines.append(url_line)
                else:
                    new_lines.append(lines[i].rstrip('\n'))
                i += 1
        else:
            new_lines.append(line)
            i += 1
    
    # Sauvegarder le fichier mis à jour
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines) + '\n')
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")
        return False
    
    print(f"\n{'='*50}")
    print(f"✅ RAPPORT DE RAFRAÎCHISSEMENT")
    print(f"{'='*50}")
    print(f"Chaînes vérifiées: {processed}")
    print(f"Liens valides: {working_count}")
    print(f"Liens inaccessibles: {broken_count}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    return True

if __name__ == '__main__':
    filename = 'TTR.m3u'
    success = refresh_m3u(filename)
    sys.exit(0 if success else 1)
