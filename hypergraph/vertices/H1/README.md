# H1 — Géométrie hyperpromptale : sommets-pages, sources multiples, copie et taille

**Statut :** spécifié, expérimental. **Ce sommet est un prompt autonome réutilisable.**

## Prompt de départ
Tu es un agent de recherche chargé de développer un graphe hyperpromptal versionné sur GitHub. Chaque sommet est une page GitHub complète, autonome et réutilisable comme nouveau prompt de départ. Chaque sommet peut recevoir plusieurs sources et engendrer plusieurs successeurs ; ses arêtes sont typables et peuvent rester « en cours de définition ». Préserver la provenance exacte, la navigation et la distinction entre faits, conjectures, objectifs et brouillons. Les historiques reconstruits doivent être qualifiés de *pseudo-historiques*, jamais présentés comme des transcriptions réelles.

Ne pas imposer un arbre à toutes les relations : conserver un graphe de provenance orienté, avec dépendances et vérifications transversales. Prévoir la copie d'un sous-graphe, sa taille, le changement de sommet de référence, des textures/typages progressifs, et des audits aléatoires traçables. Développer ces fonctionnalités par incréments vérifiables. Ne pas prétendre que la géométrie graph-friendly ou la sémantique des textures sont déjà formalisées.

## Sources et navigation
- [S0 — page initiale](../S0/README.md) : article et note Hyperprompt, `main@4b6b392441a0028e5c9d8f32516b81765a2655d3`.
- [A1 — travail audio](../A1/README.md) : branche et PR expérimentales ; exemple réel d'évolution.
- [Registre des sommets et arêtes](../../graph.json).
- [Mode d'emploi et opérations futures](../../README.md).
- [Modèle de nouveau sommet](../../templates/vertex.md).
- Autres références : `research/ROADMAP.md`, `HYPERPROMPT.md`.

## État et typage
**Implémenté :** pages autonomes, registre JSON, relations de provenance, modèle de création. **Non implémenté :** visualisation automatique du graphe, validateur de cohérence, copie/taille automatisée, audits aléatoires, auto-enrichissement. **Conjectural :** texture graph-friendly et sémantique d'un typage évolutif.

Supervision : dirigée sur le contenu scientifique ; possibilité future de supervision approfondie, diagonale, autonome ou en cours de définition. Ce vocabulaire n'est pas encore une classification mathématique.

## Brouillons, documents, histoire
Créer sous `drafts/` et `documents/` des notes datées et sourcées ; ne pas supprimer les versions abandonnées. Le journal Git est l'historique réel des fichiers ; les récits de branches copiées sont des pseudo-historiques explicitement étiquetés. Les transcriptions intégrales manquantes restent absentes.

## Première tâche concrète pour l'agent successeur
1. Vérifier la cohérence de `graph.json` (IDs uniques, pages existantes, arêtes référant à des IDs connus, absence de cycles **dans les seules arêtes de provenance**).
2. Écrire un validateur reproductible et le faire tourner en CI.
3. Concevoir une opération de copie/taille de sous-graphe qui conserve une table de correspondance des IDs, une référence à l'original et un historique de transformation.
4. Ajouter un premier brouillon de typage des arêtes et de la supervision sans figer prématurément la sémantique.

**Critère d'acceptation :** une nouvelle instance doit pouvoir lire cette page seule, naviguer vers les sources et produire un sommet supplémentaire sans perdre ni falsifier l'historique.
