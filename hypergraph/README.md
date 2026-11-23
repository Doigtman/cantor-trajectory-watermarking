# Graphe hyperpromptal — registre expérimental

**Statut :** architecture de recherche en cours de définition (2026-11-23). Ce répertoire ne remplace ni l'article original ni le prototype audio.

Chaque **sommet** est une page autonome `vertices/<id>/README.md` : prompt réutilisable, état des travaux, provenance, sources et liens vers les autres sommets. Un sommet peut avoir **plusieurs sources**. Une même source peut avoir plusieurs successeurs. Les liens d'origine sont dirigés source → cible ; les dépendances transversales peuvent former des cycles, et ne doivent pas être confondues avec les arêtes de provenance.

**Point de départ :** [sommet source S0](vertices/S0/README.md) → [sommet audio A1](vertices/A1/README.md) → [sommet de conception H1](vertices/H1/README.md). Les arêtes effectives sont dans [graph.json](graph.json), et non déduites de cette phrase. La relation A1 → H1 indique ici une succession de travail, pas une dépendance logique exclusive. S0 est également source de H1.

## Navigation et création

1. Lire `graph.json` pour connaître les sommets et les liens ; ouvrir la page de n'importe quel sommet.
2. Pour créer un successeur, attribuer un ID stable, copier `templates/vertex.md` vers `vertices/<id>/README.md`, rédiger un prompt **autonome**, puis enregistrer toutes ses sources et leurs versions dans `graph.json`.
3. Ajouter les pièces et brouillons sous `vertices/<id>/drafts/` ou `documents/`, avec provenance, date et statut ; les transcriptions intégrales ne sont ajoutées que si elles existent réellement. Les résumés ne sont jamais présentés comme transcriptions.
4. Faire évoluer les relations par ajouts typés, sans effacer leur historique ; chaque nouvelle relation peut avoir un statut provisoire.
5. Créer une branche Git par opération significative, et une PR pour revue. Les branches Git sont des environnements de modification, **pas** des sommets ; les sommets sont des pages persistantes, consultables depuis n'importe quelle branche contenant leur version.
6. Après chaque session, terminer sur un sommet lisible indépendamment, avec tâches exécutables, limites et références vers les autres sommets.

## Opérations futures réservées

- **Fork de sommet** : créer un nouvel ID et une relation de dérivation sans écraser l'original.
- **Copie et taille de sous-graphe** : préserver les IDs d'origine comme références externes ; générer de nouveaux IDs pour les copies, et conserver une table de correspondance.
- **Changement de racine** : choisir un autre sommet de référence sans réécrire rétroactivement la provenance réelle.
- **Pseudo-historique** : reconstruction explicitement signalée, avec sources et niveau de confiance ; jamais substituée à l'historique Git.
- **Audits aléatoires** : échantillonnage reproductible (graine, sélection, résultats) des dépendances, cohérence temporelle, et contradictions ; une vérification aléatoire n'est pas une preuve de cohérence globale.
- **Typage progressif** : supervision, formalisation, texture conceptuelle, auto-référence, graph-friendly ; tous ces objets restent provisoires.

**Contrainte de conception :** ne pas imposer que les relations de recherche forment un arbre. Le graphe de provenance peut rester acyclique ; le graphe de dépendances et les références peuvent contenir des cycles.
