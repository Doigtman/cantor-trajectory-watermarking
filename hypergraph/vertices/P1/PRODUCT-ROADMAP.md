# Feuille de route du produit d'authenticité — brouillon

## P0 — Définir la promesse
Utilisateur : enregistrer, marquer, exporter, puis vérifier. Séparer « fichier strictement identique », « watermark reconnu » et « contenu présumé inchangé ». Afficher un verdict **indéterminé** quand les tests ne permettent pas de conclure. Modèle de menace : auteur honnête, compresseur bénin, falsificateur non détenteur des clés, détenteur de clés compromises.

## P1 — MVP cryptographique
Signature Ed25519 d'un manifeste versionné liant empreinte du fichier, format, identité de clé et métadonnées déclaratives. Génération de clés sûre ; jamais de clé privée dans Git. Vérification hors ligne, erreurs compréhensibles, tests unitaires. Attention : un enregistrement manipulé avant signature peut être signé valablement.

## P2 — Intégration watermark audio
Marquage et vérification via `fractal_wm.py`, avec résultats statistiques **séparés** du verdict de signature. Calibrer la fausse alarme sur des sources indépendantes, et tester mp3/aac/opus, décalage, coupe, rééchantillonnage, gain et bruit. Évaluer audibilité et temps d'exécution.

## P3 — Détection de falsification sous transformations permises
Spécifier une classe d'équivalence de transformations bénignes (par exemple transcodage contrôlé) et une classe d'attaques. Tester la possibilité de signer une représentation canonique robuste ou des caractéristiques authentifiées ; documenter les ambiguïtés, collisions, manipulations locales et impossibilités éventuelles. **Objectif de recherche, pas garantie.**

## P4 — Application téléchargeable
CLI et interface graphique, packages Windows/macOS/Linux si réalisables, builds reproductibles et releases GitHub avec sommes de contrôle et signatures d'artefacts. Documentation d'installation, avertissements, format de preuve stable.

## P5 — Image et vidéo
Adapter l'architecture des transformées (audio : temps-fréquence ; image : transformées spatiales/fréquentielles ; vidéo : temps-espace-fréquence). La DFT est une famille d'outils possible, pas une preuve que les garanties audio se transfèrent automatiquement.

## Critères de sortie
Chaque version indique explicitement les transformations supportées, les données d'essai, le protocole de calibration, les taux d'erreur mesurés et les attaques non couvertes. Aucun verdict « non trafiqué » fondé sur le seul watermark.
