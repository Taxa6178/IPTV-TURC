# Workflow de Mise à Jour Automatique des Liens IPTV

## 📋 Description

Ce workflow GitHub Actions met à jour automatiquement les liens IPTV dans le fichier `TTR.m3u` toutes les **30 minutes**.

## ⚙️ Fonctionnement

1. **Vérification des liens** : Le script Python vérifie la validité de chaque lien IPTV
2. **Rapport** : Un rapport détaillé est généré montrant les liens valides/invalides
3. **Commit automatique** : Les modifications (si détectées) sont commit automatiquement

## 📁 Fichiers créés

- `.github/workflows/update-iptv-links.yml` : Configuration du workflow
- `scripts/update_iptv_links.py` : Script Python de validation des liens

## 🚀 Utilisation

### Déclenchement automatique
Le workflow s'exécute automatiquement toutes les 30 minutes grâce à la tâche planifiée (cron).

### Déclenchement manuel
Vous pouvez déclencher le workflow manuellement depuis l'onglet **Actions** de GitHub.

## 📊 Sortie

Le workflow génère un rapport montrant :
- ✓ Nombre de liens valides
- ✗ Nombre de liens invalides
- Nom de chaque chaîne TV avec son statut

## ⚠️ Limitations actuelles

Le script actuel **vérifie uniquement** les liens mais ne les remplace pas automatiquement. Pour implémenter le remplacement automatique, vous devriez :

1. Maintenir une **base de données des liens de secours** pour chaque chaîne
2. Utiliser une **API** ou un **service de scraping** pour obtenir de nouveaux liens
3. Mettre en place une **logique de remplacement** dans le script

## 🔧 Améliorations possibles

Pour rendre le système plus robuste :

```python
# Ajouter une base de données de liens alternatifs
BACKUP_LINKS = {
    "ATV": ["https://backup1.com/atv", "https://backup2.com/atv"],
    # ... autres chaînes
}
```

## 📝 Notes

- Les commits sont signés par "GitHub Action"
- Aucun commit n'est créé si aucune modification n'est détectée
- Les logs sont visibles dans l'onglet **Actions** → **Runs** → **Update IPTV Links**

## ❓ Questions fréquentes

**Q: Pourquoi certains liens ne sont pas vérifiés?**
R: Certains serveurs peuvent bloquer les vérifications HEAD. Vous pouvez modifier le script pour utiliser des requêtes GET.

**Q: Comment modifier la fréquence de mise à jour?**
R: Modifiez la ligne `- cron: '*/30 * * * *'` dans `.github/workflows/update-iptv-links.yml`
- `*/15` = toutes les 15 minutes
- `0 * * * *` = toutes les heures

**Q: Comment arrêter le workflow?**
R: Désactivez-le depuis l'onglet **Actions** ou supprimez le fichier `.github/workflows/update-iptv-links.yml`
