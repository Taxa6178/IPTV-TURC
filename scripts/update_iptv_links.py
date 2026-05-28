#!/usr/bin/env python3
"""
Script pour vérifier et mettre à jour les liens IPTV automatiquement
Valide les liens et les remplace par des alternatives si nécessaire
"""

import re
import requests
from pathlib import Path
from datetime import datetime
import logging
import json

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Timeout pour les requêtes HTTP
REQUEST_TIMEOUT = 5

# Base de données des liens alternatifs pour chaque chaîne
BACKUP_LINKS = {
    "ATV": [
        "https://cdn900.canlitv.vin/atv.m3u8",
        "https://cdn501.canlitv.vin/atv.m3u8",
    ],
    "ATV Avrupa": [
        "https://cdn504.canlitv.vin/atvavrupa.m3u8",
        "https://cdn900.canlitv.vin/atvavrupa.m3u8",
    ],
    "SHOW TURK": [
        "https://cdn501.canlitv.vin/showturk.m3u8",
        "https://cdn900.canlitv.vin/showturk.m3u8",
    ],
    "SHOW MAX": [
        "https://cdn900.canlitv.vin/showmax.m3u8",
        "https://cdn501.canlitv.vin/showmax.m3u8",
    ],
    "TV8": [
        "https://tv8.daioncdn.net/tv8/tv8.m3u8",
        "https://cdn900.canlitv.vin/tv8.m3u8",
    ],
    "NOW": [
        "https://cdn502.canlitv.vin/foxtv.m3u8",
        "https://cdn900.canlitv.vin/foxtv.m3u8",
    ],
    "Minika Cocuk": [
        "https://cdn509.canlitv.vin/minikacocuk.m3u8",
        "https://cdn501.canlitv.vin/minikacocuk.m3u8",
    ],
    "Minika GO": [
        "https://cdn501.canlitv.vin/minikago.m3u8",
        "https://cdn509.canlitv.vin/minikago.m3u8",
    ],
    "Show TV": [
        "https://ciner.daioncdn.net/showtv/showtv.m3u8",
        "https://cdn501.canlitv.vin/showturk.m3u8",
    ],
    "Kanal D": [
        "http://live.duhnet.tv/S2/HLS_LIVE/kanalddainp/playlist.m3u8",
        "https://cdn900.canlitv.vin/kanald.m3u8",
    ],
    "TRT 1 HD": [
        "https://trt.daioncdn.net/trt-1/master.m3u8?app=web",
        "https://cdn900.canlitv.vin/trt1.m3u8",
    ],
    "TRT 2": [
        "https://cdn900.canlitv.vin/trt2.m3u8",
        "https://trt.daioncdn.net/trt-2/master.m3u8",
    ],
    "TGRT Haber": [
        "https://canli.tgrthaber.com/tgrt.m3u8",
        "https://cdn900.canlitv.vin/tgrthaber.m3u8",
    ],
}

def check_url_valid(url):
    """
    Vérifie si une URL est accessible
    Retourne True si la URL répond avec un code < 400, False sinon
    """
    try:
        response = requests.head(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        return response.status_code < 400
    except requests.exceptions.Timeout:
        logger.warning(f"Timeout pour {url}")
        return False
    except requests.exceptions.ConnectionError:
        logger.warning(f"Erreur de connexion pour {url}")
        return False
    except Exception as e:
        logger.warning(f"Erreur lors de la vérification de {url}: {e}")
        return False

def find_working_backup_link(channel_name, current_url):
    """
    Cherche un lien de secours valide pour une chaîne
    Retourne le lien valide trouvé ou None
    """
    if channel_name not in BACKUP_LINKS:
        return None
    
    for backup_url in BACKUP_LINKS[channel_name]:
        if backup_url == current_url:
            # Sauter l'URL actuelle
            continue
        
        logger.info(f"  Vérification du lien de secours: {backup_url}")
        if check_url_valid(backup_url):
            logger.info(f"  ✓ Lien de secours valide trouvé!")
            return backup_url
    
    return None

def read_m3u_file(filepath):
    """Lit le fichier M3U et retourne son contenu"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier {filepath}: {e}")
        return None

def write_m3u_file(filepath, content):
    """Écrit le contenu dans le fichier M3U"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Fichier {filepath} mis à jour avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'écriture du fichier {filepath}: {e}")
        return False

def extract_and_process_streams(content):
    """
    Extrait les informations de stream du fichier M3U
    Vérifie chaque lien et le remplace si nécessaire
    Retourne (contenu_modifié, nombre_modifications)
    """
    lines = content.split('\n')
    modified = False
    changes_count = 0
    updated_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Cherche une ligne EXTINF
        if line.startswith('#EXTINF:'):
            metadata = line
            updated_lines.append(lines[i])  # Ajouter la ligne originale avec son indentation
            
            # La ligne suivante devrait être l'URL
            if i + 1 < len(lines):
                url_line = lines[i + 1].strip()
                
                # Vérifie que c'est une URL (commence par http)
                if url_line.startswith('http'):
                    # Extrait le nom du channel
                    match = re.search(r'tvg-name="([^"]*)"', metadata)
                    channel_name = match.group(1) if match else "Unknown"
                    
                    logger.info(f"Vérification: {channel_name}")
                    
                    # Vérifie la validité du lien actuel
                    if check_url_valid(url_line):
                        logger.info(f"  ✓ URL valide: {url_line}")
                        updated_lines.append(lines[i + 1])  # Garder l'URL originale
                    else:
                        logger.warning(f"  ✗ URL invalide: {url_line}")
                        
                        # Cherche un lien de secours
                        backup_link = find_working_backup_link(channel_name, url_line)
                        
                        if backup_link:
                            logger.info(f"  → Remplacement par: {backup_link}")
                            updated_lines.append(backup_link)
                            modified = True
                            changes_count += 1
                        else:
                            logger.warning(f"  ! Aucun lien de secours trouvé, conservation de l'original")
                            updated_lines.append(lines[i + 1])
                    
                    i += 2
                else:
                    updated_lines.append(lines[i + 1])
                    i += 2
            else:
                i += 1
        else:
            updated_lines.append(lines[i])
            i += 1
    
    new_content = '\n'.join(updated_lines)
    return new_content, changes_count, modified

def generate_report(m3u_file):
    """
    Génère un rapport de vérification et mise à jour
    """
    content = read_m3u_file(m3u_file)
    if not content:
        return False
    
    new_content, changes_count, modified = extract_and_process_streams(content)
    
    # Affiche le rapport
    logger.info("\n" + "="*60)
    logger.info("RAPPORT DE MISE À JOUR IPTV")
    logger.info("="*60)
    logger.info(f"Fichier: {m3u_file}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Modifications apportées: {changes_count}")
    logger.info("="*60 + "\n")
    
    # Écrit le fichier mis à jour si des changements ont été apportés
    if modified:
        logger.info("Écriture des modifications...")
        if write_m3u_file(m3u_file, new_content):
            logger.info(f"✓ {changes_count} lien(s) mis à jour avec succès!")
            return True
    else:
        logger.info("Aucune modification nécessaire.")
    
    return modified

def main():
    """Fonction principale"""
    m3u_files = ['TTR.m3u']  # Vous pouvez ajouter d'autres fichiers
    
    logger.info("\n" + "="*60)
    logger.info("DÉMARRAGE DE LA MISE À JOUR DES LIENS IPTV")
    logger.info("="*60)
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("="*60 + "\n")
    
    total_changes = 0
    
    for m3u_file in m3u_files:
        if Path(m3u_file).exists():
            logger.info(f"Traitement de {m3u_file}...\n")
            if generate_report(m3u_file):
                total_changes += 1
        else:
            logger.warning(f"Fichier {m3u_file} non trouvé")
    
    logger.info("\n" + "="*60)
    logger.info("MISE À JOUR TERMINÉE")
    logger.info("="*60 + "\n")

if __name__ == '__main__':
    main()
