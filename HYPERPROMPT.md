# Hyperprompt : formalisation arborescente — présentation publique

**Auteur :** Jean Camille d’Ornano (« Doigtman »)  
**Origine :** note de recherche du 21 octobre 2026, intégrée au dépôt e-Soleau du 23 octobre 2026.  
**Statut :** programme de recherche ; plusieurs propriétés visées restent à formaliser ou démontrer.

> Cette page est une présentation publique adaptée de la note historique, et non sa transcription intégrale. La mention « privée » dans l'enveloppe d'origine décrivait l'intention de publication à cette date, désormais modifiée par l'auteur.

## 1. Définition

Soit \(P\) l'ensemble des prompts. Un **hyperprompt** est un arbre enraciné dont les nœuds sont des prompts (ou familles de prompts). Un nœud correspond à une suite finie de prompts \((p_1,\ldots,p_k)\), représentant une continuation possible d'un dialogue avec un modèle.

Chaque nœud \(s\) porte un ensemble de dépendances \(\mathrm{dep}(s)\), inclus dans l'ensemble de ses ancêtres : vide (sans contexte), complet (entièrement contextuel), ou intermédiaire (dépendance partielle).

## 2. Auto-enrichissement

La règle de génération des descendants est elle-même exprimée par un hyperprompt attaché à la branche. L'objectif est un système susceptible de développer, conserver et raffiner ses propres branches et résultats. **Il s'agit d'un principe de conception, non d'une propriété démontrée.**

## 3. Relation avec les fractales de Cantor

Un ensemble de Cantor à subdivision entière se représente par les chemins infinis d'un arbre de chiffres autorisés. L'hyperprompt est également un objet arborescent. Les rapprochements proposés portent notamment sur la troncature à profondeur finie, la granularité et la possibilité d'une compression conservant une structure identifiable.

## 4. Décomposition et recombinaison

Un hyperprompt peut être organisé en facteurs \(H=H_1\oplus H_2\oplus\cdots\), étudiés séparément lorsque leurs interfaces sont fixées. Dans le cadre du tatouage numérique : détecteur mathématique abstrait, mécanisme d'insertion/extraction et gestion des paramètres cachés constituent des facteurs possibles.

## 5. Langage de graphes de concepts

Le projet envisage un langage dont les nœuds sont des concepts, étiquetés par un ensemble partiellement ordonné mesurant leur degré de précision, d'une idée encore vague jusqu'à une définition mathématique. Les nœuds peuvent eux-mêmes être des graphes. L'auto-référence, les raffinements et les conditions de cohérence font partie du programme de recherche ; aucune théorie complète n'est affirmée ici.

## 6. Exécution autonome : objectif ouvert

L'objectif est qu'un hyperprompt puisse guider son propre déroulement, intégrer les résultats produits et proposer de nouveaux prompts, avec conservation de la provenance dans l'arbre. Cette autonomie **n'a pas été établie** dans la note initiale.

## 7. Premier exemple : tatouage par trajectoires de Cantor

L'article [A General Framework for Cantor-Trajectory Signal Watermarking](README.md) est présenté comme une première branche de ce programme. Le prototype audio [fractal_wm.py](fractal_wm.py) illustre une partie du cadre, sans constituer une implémentation complète des hyperprompts.

---

*Cette page peut être étendue ultérieurement en article autonome. La note e-Soleau originale reste un document historique distinct.*
