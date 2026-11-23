# A1 — Audio v0.2 : épreuve et calibration

**Statut :** tests de fonctionnement réussis ; protocole expérimental créé, robustesse non validée.

## Prompt autonome
Poursuivre l'évaluation du prototype audio v0.2 (trois procédés × trois fractales). Priorités : robustesse aux codecs et désynchronisations, imperceptibilité, fausses alarmes, attaques de recopie et adversaire adaptatif. Distinguer systématiquement résultats, hypothèses et objectifs. Préserver le code original sur main, exécuter les tests, consigner les résultats négatifs, publier les données reproductibles dans GitHub.

## Origines et voisinage
- Source : [S0](../S0/README.md), version initiale `main@4b6b392441a0028e5c9d8f32516b81765a2655d3`.
- Travail concret : [PR #2](https://github.com/Doigtman/cantor-trajectory-watermarking/pull/2), branche `research/audio-v02-calibration-20261123`.
- Successeur : [H1](../H1/README.md) pour la géométrie hyperpromptale.
- Journal : [SESSION-2026-11-23](../../../research/experiences/SESSION-2026-11-23.md).

## Résultats, limites et tests
**Observé :** cinq tests de non-régression réussis sur GitHub Actions. **Non établi :** performance perceptuelle, calibration des faux positifs, robustesse multi-source, sécurité cryptographique. Les exécutions du mini-benchmark n'ont pas produit de rapport exploitable lors de la session initiale.

`python -m unittest discover -s tests -v`

`python -m experiments.audio_v02_benchmark --no-codecs --seconds 2 --seeds 11 --deltas 0.02 --output experiments/results/audio_v02_smoke.json`

## Supervision et brouillons
Supervision actuelle : agent effectuant des modifications sur branche avec PR à relire ; degré de formalisation du protocole en cours de précision. Brouillons et résultats dans `research/experiences/`, sans reconstruction fictive.

## Passation
**Première action :** vérifier le dernier CI, corriger les problèmes d'exécution du benchmark, conserver un JSON brut ; ensuite calibrer des seuils sur données indépendantes. Ne pas fusionner avant revue.
