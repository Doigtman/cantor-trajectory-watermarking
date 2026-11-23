# DET-001 — Calibration et sécurité du détecteur

- **Parents :** AUD-001 ; feuille de route D, E.
- **Dépendances :** extraction audio ; signal et clés ; protocole de calibration sans fuite.
- **Objectif :** détecter une signature avec taux de faux positifs mesuré, puis examiner imitation, recopie et désynchronisation.
- **Entrées/sorties :** tableaux de scores par enregistrement et par bloc ; décision explicite à un seuil fixé.
- **Hypothèses :** corrélation entre 9 scores ; décorrélation imparfaite malgré les labels HMAC ; vulnérabilité de la clé dérivée de `fp="0"`.
- **Formalisation :** problème statistique spécifié, modèle d'adversaire encore à définir.
- **Statut :** `spécifié` ; aucune calibration nouvelle validée.
- **Sources :** Partie II §§3, 5, 8.2, 9 du README ; code `verify`.
- **Tests prévus :** nulls externes à la clé testée, bootstrap par enregistrement (non par bloc dépendant), contrôle de split train/calibration/test, attaques copie-collage et ré-encodage.
- **Risques :** confusion score z / p-value ; selection des hyperparamètres sur le test ; exagération des garanties cryptographiques.
- **Prochaine action :** tester distribution de scores avec de nombreuses clés et sources indépendantes ; évaluer stabilité avant de fixer un seuil.

# HYP-001 — Supervision évolutive des branches

- **Parents :** `HYPERPROMPT.md` ; `research/ROADMAP.md` ; AUD-001.
- **Dépendances :** registre de nœuds et traçabilité Git ; les branches peuvent exister indépendamment.
- **Objectif :** faire coévoluer recherches watermarking et définition de l'hyperprompt, y compris un hyperprompt de l'hyperprompt.
- **Entrées/sorties :** demandes et observations ; nœuds typés, versions, dépendances, décisions et résultats.
- **Hypothèse :** la supervision et le degré de définition peuvent être raffinés sans perdre la provenance.
- **Formalisation :** esquisse de schéma ; pas de sémantique formelle, d'autonomie vérifiée ou de typage démontré.
- **Statut :** `spécifié` pour le registre ; auto-enrichissement encore `idée`.
- **Sources :** `HYPERPROMPT.md`, section 5, et feuille de route F–G.
- **Tests :** revue de complétude des nœuds, cohérence des liens parent/dépendances, états documentés, non-réécriture des originaux.
- **Risques :** dépendances circulaires non traitées, erreurs d'automatisation, branche sans état expérimental fiable.
- **Prochaine action :** proposer un schéma JSON versionné (dont `supervision`: autonomie, relecture, guidage, degré de précision en évolution) ; ne pas prétendre réaliser une autonomie permanente sans infrastructure d'exécution.

## Modes de supervision à typer (proposition, non état actuel)

`autonome`, `supervisé-dirigé`, `supervisé-fouillé`, `supervisé-diagonal`, `en-cours-de-définition`. Un nœud peut changer de type au fil d'une revue explicite et conserver l'historique de ces changements. Ces étiquettes sont des propositions conceptuelles, pas des garanties d'exécution ni une échelle ordinale déjà formalisée.
