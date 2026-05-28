# Workflow de Mise à Jour Automatique des Liens IPTV

## 📋 Description

Ce workflow GitHub Actions met à jour automatiquement les liens IPTV dans le fichier `TTR.m3u` toutes les **30 minutes**.

## ⚙️ Fonctionnement

1. **Vérification des liens** : Le script Python vérifie la validité de chaque lien IPTV
2. **Remplacement automatique** : Les liens invalides sont remplacés par des alternatives valides
3. **Commit automatique** : Les modifications (si détectées) sont commit automatiquement

## 📁 Fichiers créés

- `.github/workflows/update-iptv-links.yml` : Configuration du workflow
- `scripts/update_iptv_links.py` : Script Python de validation et remplacement des liens

## 🚀 Utilisation

### Déclenchement automatique
Le workflow s'exécute automatiquement toutes les 30 minutes grâce à la tâche planifiée (cron).

### Déclenchement manuel
Vous pouvez déclencher le workflow manuellement depuis l'onglet **Actions** → **Update IPTV Links** → **Run workflow**.

## 📊 Fonctionnalités

✓ Vérifie la validité de chaque lien IPTV
✓ Remplace automatiquement les liens invalides par des alternatives
✓ Base de données de 15+ liens de secours par chaîne
✓ Gestion des timeouts et erreurs de connexion
✓ Logs détaillés avec rapport complet
✓ Commit automatique des modifications
✓ Pas de commit si aucune modification

## 🔧 Base de données des liens de secours

Le script contient une base de données `BACKUP_LINKS` avec des alternatives pour :

- ATV
- ATV Avrupa
- SHOW TURK / SHOW MAX
- TV8
- NOW
- Minika (Cocuk, GO)
- Show TV
- Kanal D
- TRT (1 HD, 2, Müzik, etc.)
- TGRT Haber
- Et plus...

## 📈 Améliorations futures

1. Ajouter plus de liens de secours
2. Intégrer un système de scraping pour récupérer les derniers liens
3. Envoyer des notifications en cas de problème
4. Maintenir un historique des changements

## 🔗 Logs et monitoring

Les logs du workflow sont visibles dans :
**GitHub** → **Actions** → **Update IPTV Links** → Sélectionner la dernière exécution

## ⚠️ Important

- Le workflow nécessite des permissions de `contents: write` pour commit les changements
- Les changements sont push automatiquement sur `main`
- Aucun fichier n'est modifié si tous les liens sont valides

## ❓ FAQ

**Q: Comment modifier la fréquence?**
R: Editez `.github/workflows/update-iptv-links.yml` et changez `- cron: '*/30 * * * *'`:
- `*/15` = toutes les 15 minutes
- `0 * * * *` = toutes les heures
- `0 0 * * *` = une fois par jour

**Q: Comment ajouter des liens de secours?**
R: Modifiez le dictionnaire `BACKUP_LINKS` dans `scripts/update_iptv_links.py`

**Q: Comment désactiver le workflow?**
R: Désactivez-le depuis **Actions** ou supprimez `.github/workflows/update-iptv-links.yml`
