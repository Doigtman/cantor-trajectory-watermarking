# P1 — Logiciel de marquage et vérification d'authenticité multimédia

**Statut :** spécification initiale ; **sommet autonome** ; aucun logiciel prêt à l'emploi ni garantie de détection des falsifications n'est revendiqué.

## Prompt autonome de départ
Tu es un agent de recherche et développement chargé de livrer, sur GitHub, un logiciel installable permettant de **marquer** un enregistrement audio et de **vérifier** son authenticité, avec extension ultérieure aux images et vidéos. La priorité est l'audio. Séparer rigoureusement l'intégrité cryptographique exacte, la détection d'un watermark robuste et la détection de modifications sémantiques. Définir les transformations autorisées, les adversaires, les taux de faux positifs et faux négatifs, et les limites. Ne jamais qualifier une preuve d'inviolable sans modèle de menace et validation.

**Livrables recherchés :** interface utilisateur simple, outil en ligne de commande, installateur ou exécutable téléchargeable depuis les releases GitHub, format de preuve documenté, clés correctement gérées, tests reproductibles et rapport d'évaluation accessible aux non-spécialistes.

## Arborescence et origines
- Source principale : [H1 — géométrie hyperpromptale](../H1/README.md), branche `hyperprompt/vertex-graph-foundation-20261123`.
- Références scientifiques transversales : [A1 — banc d'essai audio](../A1/README.md) et [S0 — article initial](../S0/README.md). **Ces références ne sont pas des sources supplémentaires de l'arête de provenance de P1.**
- [Registre](../../graph.json), [feuille de route produit](PRODUCT-ROADMAP.md).
- Les arêtes de provenance forment par défaut une arborescence ; synthèses, multiplications et cycles éventuels exigent un type et une justification explicites.

## Contrat de sécurité à examiner
1. **Intégrité exacte :** hachage du fichier canonique signé avec une clé privée ; vérification par clé publique et chaîne de confiance. Toute modification des octets invalide la signature. La signature seule ne prouve ni la vérité du contenu ni l'identité du capteur.
2. **Watermark robuste :** marque détectable après transformations autorisées (compression avec perte, changements de niveau, etc.), à mesurer. Sa persistance ne prouve pas que le contenu n'a pas été manipulé.
3. **Authenticité perceptuelle ou sémantique :** hypothèse de recherche distincte ; définir ce qu'est une falsification et établir expérimentalement la capacité de discrimination sous compression. Aucune garantie absolue n'est actuellement fondée.
4. **Provenance :** identité de la clé, certificat éventuel, moment et conditions de capture ; gérer les clés compromises et les enregistrements signés après manipulation.

## Première tâche de l'agent
Concevoir un MVP d'authentification **exacte** : signer un fichier audio et vérifier sa signature dans un manifeste indépendant. Employer une bibliothèque cryptographique éprouvée (p. ex. Ed25519) et ne pas concevoir de cryptographie maison. Tests : fichier intact accepté, modification d'un octet rejetée, clé erronée rejetée, manifeste corrompu rejeté. Puis brancher le détecteur v0.2 comme indicateur séparé, jamais comme preuve d'absence de falsification.

## Supervision, état et passation
Supervision : conception dirigée et développement expérimental supervisé ; degré de définition évolutif. **Démontré :** rien pour l'authenticité produit. **Existant :** prototype de watermark audio et tests de fonctionnement sur branche de recherche. **Non validé :** robustesse compression, taux d'erreurs, authenticité sémantique, expérience utilisateur, logiciel distribuable.

Conserver les preuves brutes, critiques et résultats négatifs ; publier les prochaines étapes dans un nouveau sommet autonome, sans effacer cette provenance.
