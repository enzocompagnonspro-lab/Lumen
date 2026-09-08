# LUMEN-LIVING-SYSTEM-02 — Journey Engine

## Added
- Canonical Carte du Voyage as a live scene.
- Seven governed chamber hotspots.
- Persistent Journey state in localStorage.
- Vision progress driven by the five distinct article sections of the approved foundational reading.
- Pensee unlocks only after Vision completion.
- Library and Article can open Journey; Journey can return to Knowledge or Sanctuary.
- Browser E2E harness writes state, reloads with the same Chrome profile, and verifies persistence.

## Governance
The canonical map is not rewritten. Real progress appears only in the interactive drawer/pulse layer. Future chambers remain locked until content and rules are validated.


## Hotfix 1.5.2
La certification de persistance utilise desormais un serveur HTTP local et un rechargement dans le navigateur. Le test ne depend plus de `file://` ni de deux processus Chrome partageant un profil.
