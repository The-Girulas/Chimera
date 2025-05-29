# Analyse des Stratégies Freqtrade

Ce document résume les concepts clés extraits de différentes stratégies trouvées dans `user_data/strategies`. L'objectif est d'identifier des idées applicables pour construire des stratégies robustes pour différents régimes de marché (tendance, latéral, opportunité), en gardant à l'esprit l'optimisation du ratio Profit/Drawdown.

## Stratégie : `AdaptiveTrendRider.py` (Notre Référence Actuelle)

*   **Type :** Tendance (Long/Short)
*   **Indicateurs :** Supertrend (direction), ADX (force), Volume MA (confirmation), ATR (trailing stop).
*   **Entrée :** Accord Supertrend + ADX > Seuil + Volume > Moyenne Volume.
*   **Sortie :** Inversion Supertrend.
*   **Stoploss :** Trailing Stop ATR personnalisé (via `custom_stoploss` et `trailing_stop=True`). Paramètres optimisés.
*   **ROI :** Désactivé (100%).
*   **Concepts :**
    *   **Tendance :** Combinaison Supertrend/ADX efficace. Trailing stop ATR performant pour suivre la tendance.
    *   **Latéral :** Probablement sensible aux faux signaux Supertrend/ADX en range.
    *   **Opportunité :** Capture bien les fortes tendances.
*   **Pistes :** Améliorer le Win Rate (filtres d'entrée ?), affiner la sortie (confirmation ?).
*   **Référence Backtest (Optimisé 2025-04-29 20:26):** +274.69% Profit, 19.55% Drawdown, Sortino 9.21, Win Rate 29.1%.

## Stratégie : `ADXMomentum.py`

*   **Type :** Tendance (Long Only par défaut)
*   **Indicateurs :** ADX (14), PLUS_DI/MINUS_DI (25), Momentum (MOM 14), SAR (calculé mais non utilisé).
*   **Entrée (Long) :** ADX > 25 & MOM > 0 & PLUS_DI > 25 & PLUS_DI > MINUS_DI.
*   **Sortie (Long) :** ADX > 25 & MOM < 0 & MINUS_DI > 25 & PLUS_DI < MINUS_DI. (Sortie agressive sur faiblesse momentum).
*   **Stoploss :** Fixe -25%.
*   **ROI :** Minimum 1%.
*   **Concepts :**
    *   **Tendance :** Utilisation ADX/DI classique.
    *   **Opportunité/Momentum :** Utilisation MOM pour timer entrées/sorties.
    *   **Latéral :** Probablement peu performant.
*   **Pistes :** Utiliser SAR pour stop suiveur, optimiser périodes/seuils, ajouter filtres, revoir la logique de sortie (ex: sortie sur baisse ADX).

## Stratégie : `BBRSI.py`

*   **Type :** Retour à la moyenne / Range (Long Only par défaut).
*   **Indicateurs :** RSI (14), Bandes de Bollinger (BB 20, 1sd pour signaux, 4sd calculée mais non utilisée).
*   **Entrée (Long) :** RSI > 25 & Close < Bande Inférieure BB (1sd). (Condition RSI > 25 un peu étrange pour du retour à la moyenne).
*   **Sortie (Long) :** RSI > 95 & Close > Bande Supérieure BB (1sd). (Condition RSI extrême).
*   **Stoploss :** Fixe -36% (très large).
*   **ROI :** Table ROI active avec plusieurs paliers visant des profits rapides.
*   **Concepts :**
    *   **Latéral :** Logique typique BB+RSI pour trader le range.
    *   **Tendance :** Probablement peu performante en tendance forte.
    *   **Opportunité :** Capture potentiellement des rebonds rapides sur les bandes.
*   **Pistes :** Utiliser BB 4sd pour entrées, ajuster seuils RSI (ex: <30 / >70), ajouter filtre ADX (< seuil) pour activer en range, stoploss dynamique (ATR), revoir ROI.

## Stratégie : `CombinedBinHAndCluc.py`

*   **Type :** Hybride / Opportunité (Long Only par défaut, timeframe 5m).
*   **Indicateurs :** BB (40, 2sd), BB (20, 2sd), EMA (50), Volume MA (30), calculs spécifiques (bbdelta, closedelta, tail).
*   **Entrée (Long) :** Combinaison (OU) de deux logiques :
    *   *BinHV45 :* Conditions complexes sur volatilité BB, variation prix, mèche basse, position vs BB inférieure veille (vise rebond sur forte baisse ?).
    *   *ClucMay72018 :* Prix < EMA50 & Prix < 0.985 * BB Inférieure (20, 2sd) & Volume < 20 * Moyenne Volume (vise retour à la moyenne).
*   **Sortie (Long) :** Simple : Close > BB Médiane (20, 2sd).
*   **Stoploss :** Fixe -5%.
*   **ROI :** Minimum 5%.
*   **Concepts :**
    *   **Latéral / Retour Moyenne :** Logique ClucMay72018 et sortie sur BB médiane.
    *   **Opportunité :** Logique BinHV45 et combinaison de deux systèmes.
    *   **Tendance :** Filtre EMA50 pour éviter achats en tendance haussière forte, mais non conçue pour suivre la tendance.
*   **Pistes :** Séparer les logiques, tester autres indicateurs de survente (RSI, Stoch), sorties plus dynamiques (trailing stop, BB supérieure), optimiser paramètres.

## Stratégie : `Combined_Indicators.py`

*   **Type :** Hybride / Opportunité (Long Only par défaut, timeframe 1m). Variante de `CombinedBinHAndCluc.py`.
*   **Indicateurs :** Identiques : BB (40, 2sd), BB (20, 2sd), EMA (50), Volume MA (30), calculs spécifiques (bbdelta, closedelta, tail).
*   **Entrée (Long) :** Combinaison (OU) des logiques BinHV45 et ClucMay72018, avec des seuils légèrement différents de la version 5m.
*   **Sortie (Long) :** Identique : Close > BB Médiane (20, 2sd).
*   **Stoploss :** Fixe -6.58%.
*   **ROI :** Minimum 1.5%.
*   **Trailing Stop :** **Activé** (standard) : `trailing_stop = True`, `trailing_stop_positive = 0.0198`, `trailing_stop_positive_offset = 0.03082`, `trailing_only_offset_is_reached = True`.
*   **Concepts :**
    *   **Latéral / Retour Moyenne :** Logique ClucMay72018 et sortie sur BB médiane.
    *   **Opportunité :** Logique BinHV45, combinaison de systèmes, timeframe très court.
    *   **Tendance :** Filtre EMA50. Le trailing stop standard pourrait aider à suivre une tendance courte.
*   **Pistes :** Comparer performance vs `CombinedBinHAndCluc.py` (impact timeframe et trailing stop), optimiser paramètres 1m, tester sur timeframes plus longs.

## Stratégie : `AdxSmas.py`

*   **Type :** Tendance (Long Only par défaut).
*   **Indicateurs :** ADX (14), SMA (3), SMA (6).
*   **Entrée (Long) :** ADX > 25 & Croisement SMA(3) > SMA(6).
*   **Sortie (Long) :** ADX < 25 & Croisement SMA(6) > SMA(3).
*   **Stoploss :** Fixe -25%.
*   **ROI :** Minimum 10%.
*   **Concepts :**
    *   **Tendance :** Croisement de MM filtré par ADX. Sortie logique sur affaiblissement tendance + croisement inverse.
    *   **Latéral :** Filtre ADX évite les entrées en range.
*   **Pistes :** Optimiser périodes ADX/SMAs, tester EMAs, stoploss dynamique, logique Short, autres confirmations.

## Stratégie : `CrossEMAStrategy.py`

*   **Type :** Tendance (Long Only par défaut).
*   **Indicateurs :** EMA (28), EMA (48), Stochastic RSI.
*   **Entrée (Long) :** Croisement EMA(28) > EMA(48) & Stoch RSI < Seuil Achat (0.8).
*   **Sortie (Long) :** Croisement EMA(28) < EMA(48) & Stoch RSI > Seuil Vente (0.2).
*   **Stoploss :** Inactif (-99%).
*   **ROI :** Inactif (100%).
*   **Trailing Stop :** Désactivé.
*   **Concepts :**
    *   **Tendance :** Suivi de tendance classique par croisement EMAs, filtré par StochRSI pour éviter conditions extrêmes.
    *   **Latéral :** Probablement beaucoup de faux signaux.
*   **Pistes :** Activer/optimiser stoploss, tester seuils StochRSI, ajouter filtres (ADX, Volume), optimiser périodes EMAs, logique Short.

## Stratégie : `Divergences.py`

*   **Type :** Opportunité / Contre-Tendance (Long Only par défaut).
*   **Indicateurs :** Détection de pattern de prix "divergent" (`bullish_div`, `bearish_div`), RSI (14). *Beaucoup d'autres indicateurs calculés mais non utilisés (CCI, ADX, Stoch, MACD, MFI, BB, EMAs, SAR, TEMA, Hilbert).*
*   **Entrée (Long) :** RSI <= 40 & Pattern `bullish_div` détecté sur le prix.
*   **Sortie (Long) :** Pattern `bearish_div` détecté sur le prix.
*   **Stoploss :** Fixe -10%.
*   **ROI :** Inactif (100%).
*   **Trailing Stop :** **Activé** (standard) : `trailing_stop = True`, `trailing_stop_positive = 0.05`, `trailing_stop_positive_offset = 0.2`, `trailing_only_offset_is_reached = True`.
*   **Concepts :**
    *   **Opportunité / Contre-Tendance :** Détection de patterns de prix suggérant un retournement, filtré par RSI.
    *   **Tendance / Latéral :** Non applicable.
*   **Pistes :** **Implémenter la vraie détection de divergence Prix/Indicateur (RSI, MACD)**, ajouter filtres de confirmation, optimiser stoploss/trailing, logique Short.

## Stratégie : `EMABreakout.py`

*   **Type :** Tendance / Breakout (Long Only par défaut, timeframe 5m).
*   **Indicateurs :** EMA (période optimisable, défaut 90), MACD (filtre optionnel). *RSI, SAR, BB, SMA calculés mais non utilisés.*
*   **Entrée (Long) :** Clôture > EMA & (Optionnel: MACD Hist >= 0).
*   **Sortie (Long) :** Clôture < EMA (peut être désactivé via `sell_hold`).
*   **Stoploss :** Fixe -33.3%.
*   **ROI :** Table ROI active.
*   **Trailing Stop :** **Activé** (standard) : `trailing_stop = True`, `trailing_stop_positive = 0.172`, `trailing_stop_positive_offset = 0.212`, `trailing_only_offset_is_reached = False`.
*   **Concepts :**
    *   **Tendance / Breakout :** Logique simple de cassure d'EMA, potentiellement filtrée par MACD.
    *   **Latéral :** Risque de faux signaux.
*   **Pistes :** Optimiser période EMA, tester filtre MACD, ajouter filtres (ADX, Volume), tester sorties alternatives, ajuster stoploss/trailing, logique Short.

## Stratégie : `FastSupertrend.py` (Identique à `SuperTrend.py`)

*   **Type :** Tendance (Long Only par défaut).
*   **Indicateurs :** Supertrend x 3 (paramètres distincts p1/m1, p2/m2, p3/m3 pour l'achat), Supertrend x 3 (paramètres distincts p1/m1, p2/m2, p3/m3 pour la vente).
*   **Entrée (Long) :** Les 3 Supertrends "buy" sont 'up'.
*   **Sortie (Long) :** Les 3 Supertrends "sell" sont 'down'.
*   **Stoploss :** Fixe -26.5%.
*   **ROI :** Table ROI active.
*   **Trailing Stop :** **Activé** (standard) : `trailing_stop = True`, `trailing_stop_positive = 0.05`, `trailing_stop_positive_offset = 0.144`, `trailing_only_offset_is_reached = False`.
*   **Concepts :**
    *   **Tendance :** Confluence de plusieurs Supertrends pour confirmer la tendance et filtrer les signaux.
    *   **Latéral :** Moins de signaux probables, potentiellement moins fiables.
*   **Pistes :** Optimiser les 6 jeux de paramètres Supertrend, ajouter filtres (ADX, Volume, EMA), comparer vs Supertrend simple/double, logique Short, stoploss dynamique.

## Stratégie : `Ichimoku.py`

*   **Type :** Tendance / Opportunité (Long Only par défaut, timeframe 5m).
*   **Indicateurs :** Ichimoku (Tenkan, Kijun, Senkou A/B, Cloud Color).
*   **Entrée (Long) :** Croisement Tenkan > Kijun & Nuage est Rouge (Condition inhabituelle, vise retournement précoce ?).
*   **Sortie (Long) :** Aucune logique de signal définie (repose sur ROI/Stop/Trailing).
*   **Stoploss :** Fixe -10%.
*   **ROI :** Inactif (100%).
*   **Trailing Stop :** **Activé** (standard) : `trailing_stop = True`, `trailing_stop_positive = 0.01`, `trailing_stop_positive_offset = 0.02`, `trailing_only_offset_is_reached = True`.
*   **Concepts :**
    *   **Tendance :** Ichimoku est un système de tendance complet.
    *   **Opportunité :** Logique d'entrée spécifique visant un retournement.
*   **Pistes :** Implémenter sorties Ichimoku classiques (croisement TK, sortie nuage, Chikou), utiliser logique d'entrée standard (croisement TK au-dessus/dans nuage vert), ajouter Chikou Span, utiliser niveaux Ichimoku pour SL/TP, logique Short.

## Stratégie : `MACDStrategy.py`

*   **Type :** Tendance / Momentum (Long Only par défaut, timeframe 5m).
*   **Indicateurs :** MACD (12, 26, 9), CCI (20).
*   **Entrée (Long) :** MACD > Signal & CCI <= Seuil Achat (défaut -50).
*   **Sortie (Long) :** MACD < Signal & CCI >= Seuil Vente (défaut 100).
*   **Stoploss :** Fixe -30%.
*   **ROI :** Table ROI active.
*   **Trailing Stop :** Désactivé (paramètres présents).
*   **Concepts :**
    *   **Tendance / Momentum :** MACD pour direction/momentum.
    *   **Opportunité / Contre-Tendance (Filtre) :** CCI pour timer entrées/sorties sur niveaux "bas"/"hauts" relatifs à la tendance MACD.
*   **Pistes :** Optimiser seuils CCI, périodes MACD, activer/optimiser Trailing Stop, ajouter filtres (ADX, EMA), logique Short, tester autres timeframes.

## Stratégie : `NostalgiaForInfinityNextGen.py` (Analyse Conceptuelle - Fichier trop volumineux)

*   **Type :** Probablement Hybride / Opportunité (typiquement timeframe 5m).
*   **Indicateurs (Probables) :** Large éventail (EMAs, BB, RSI, Stoch, CCI, MFI, ADX, Volume, indicateurs custom comme EWO, CMF, Chopiness), souvent sur timeframe principal et informatif (ex: 1h).
*   **Entrée (Long) :** Logique très complexe combinant de nombreuses conditions (>20 typiquement) avec des gardes/protections spécifiques pour chaque scénario (tendance 1h, RSI 1h, "safe dip", "safe pump").
*   **Sortie (Long) :** Logique complexe combinant signaux indicateurs inverses, `custom_sell` avec paliers profit/RSI, sorties spécifiques "pump", ROI, Trailing Stop.
*   **Stoploss :** Variable, souvent géré par `custom_stoploss` ou désactivé au profit du trailing/signaux de vente.
*   **Concepts :**
    *   **Opportunité :** Définition de nombreux scénarios d'entrée très spécifiques.
    *   **Hybride :** Mélange d'éléments de tendance, retour moyenne, momentum.
    *   **Timeframes Multiples :** Utilisation intensive de paires informatives.
    *   **Gestion Risque Avancée :** Protections spécifiques "dip"/"pump".
*   **Pistes :** Comprendre/tester chaque condition (difficile), optimiser les nombreux paramètres, analyser contribution de chaque condition, simplifier.

## Stratégie : `Guacamole.py`

*   **Type :** Tendance / Momentum / Opportunité (Long Only par défaut, timeframe 5m).
*   **Indicateurs :** KAMA (3, 21), MACD (12, 26, 9), RMI (custom), SAR, Volume MA (24).
*   **Entrée (Long) :** Logique complexe :
    *   *Si pas de trade :* Croisement KAMA & MACD > Signal & MACD > Seuil & MACD Hist > Seuil & RMI croissant & RMI > Seuil & Volume < 20*Moyenne.
    *   *Si trade ouvert :* Close > SAR & RMI >= 75 (re-entry ?).
*   **Sortie (Long) :** RMI < 30 & Profit > -3%.
*   **Stoploss :** Inactif (-99%).
*   **ROI :** Table ROI active (paliers courts).
*   **Trailing Stop :** **Activé** (standard) : `trailing_stop = True`, `trailing_stop_positive = 0.01673`, `trailing_stop_positive_offset = 0.01851`, `trailing_only_offset_is_reached = False`.
*   **Concepts :**
    *   **Tendance / Momentum :** Combinaison KAMA/MACD/RMI.
    *   **Opportunité :** Logique d'entrée/sortie conditionnelle (trade ouvert/fermé), sortie sur RMI oversold.
*   **Pistes :** Clarifier/tester logique re-entry, simplifier/optimiser conditions entrée, tester sorties plus robustes (KAMA, MACD), stoploss réaliste, logique Short.

## Stratégie : `BB_RPB_TSL.py`

*   **Type :** Hybride / Opportunité (Long Only par défaut, timeframe 5m). Très complexe.
*   **Indicateurs :** Très nombreux (BB, RMI, CCI, SRSI, RSI, EMAs, SMAs, KAMA, MACD, EWO, CTI, CMF, Williams %R, SAR, PMAX, MomDiv, T3, Heikin Ashi, indicateurs 1h, etc.).
*   **Entrée (Long) :** Combinaison (OU) de 24 conditions activables/désactivables, chacune avec ses propres gardes/protections (tendance 1h, RSI 1h, etc.). Vise divers scénarios (dip, breakout, retournement...).
*   **Sortie (Long) :** Logique `custom_sell` très complexe avec paliers profit/RSI, conditions "pump", "descending SMA", trailing custom, stoploss custom, etc. `populate_sell_trend` est vide.
*   **Stoploss :** Inactif (-99%), mais géré via `custom_stoploss` multi-niveaux et `custom_sell`.
*   **ROI :** Table ROI active.
*   **Trailing Stop :** Désactivé (paramètres présents).
*   **Concepts :**
    *   **Opportunité / Hybride :** Exploitation de multiples configurations via conditions spécifiques.
    *   **Timeframes Multiples :** Utilisation intensive d'indicateurs 1h.
    *   **Gestion Risque Avancée :** Multiples logiques de sortie/stoploss personnalisées.
*   **Pistes :** Simplification, analyse de contribution des conditions, robustesse (risque sur-optimisation), logique Short.

## Stratégie : `CCIStrategy.py`

*   **Type :** Retour à la moyenne / Range (Long Only par défaut, timeframe 1m).
*   **Indicateurs :** CCI (170, 34), MFI (14), CMF (20), SMAs (25, 50, 100, 200) sur timeframe 5m re-échantillonné. *RSI calculé mais non utilisé.*
*   **Entrée (Long) :** Double CCI < -100 & CMF < -0.1 & MFI < 25 & Filtres SMA 5m (achète dip si tendance 5m pas trop baissière).
*   **Sortie (Long) :** Double CCI > 100 & CMF > 0.3 & Filtres SMA 5m (sort sur overbought si tendance 5m haussière).
*   **Stoploss :** Fixe -2%.
*   **ROI :** Minimum 10%.
*   **Trailing Stop :** **Activé** (standard) : `trailing_stop = True`, `trailing_stop_positive = 0.01`, `trailing_stop_positive_offset = 0.02`, `trailing_only_offset_is_reached = True`.
*   **Concepts :**
    *   **Range / Retour Moyenne :** Utilisation multiple d'indicateurs oversold/overbought (CCI, MFI, CMF).
    *   **Timeframes Multiples :** SMAs 5m pour filtrer signaux 1m.
*   **Pistes :** Tester impact indicateurs individuellement, optimiser périodes/seuils, tester filtres tendance, ajuster stoploss, logique Short.

## Stratégie : `ElliotV8_original.py`

*   **Type :** Hybride / Opportunité (Long Only par défaut, timeframe 5m).
*   **Indicateurs :** EMA (variable), HMA (50), EWO (50, 200), RSI (14), RSI Fast (4), RSI Slow (20).
*   **Entrée (Long) :** Combine 2 scénarios (OU) basés sur EWO haut ou bas, filtrés par RSI et position par rapport à l'EMA achat.
*   **Sortie (Long) :** Combine 2 scénarios (OU) basés sur la position par rapport à HMA 50, utilisant l'EMA vente et le RSI.
*   **Stoploss :** Fixe -32%.
*   **ROI :** Table ROI active.
*   **Trailing Stop :** **Activé** (standard) : `trailing_stop = True`, `trailing_stop_positive = 0.001`, `trailing_stop_positive_offset = 0.02`, `trailing_only_offset_is_reached = True`.
*   **Concepts :**
    *   **Opportunité :** Utilisation EWO pour timing basé sur théorie des vagues.
    *   **Tendance (Filtre/Sortie) :** HMA 50 pour adapter la sortie au contexte.
*   **Pistes :** Explorer théorie Elliott, optimiser périodes EWO/EMAs/HMA, simplifier conditions RSI, ajuster stoploss/trailing, logique Short.

## Stratégie : `EMAVolume.py`

*   **Type :** Tendance (Long Only par défaut, timeframe 15m).
*   **Indicateurs :** EMA (13), EMA (34), Volume MA (10). *Autres EMAs calculées mais non utilisées.*
*   **Entrée (Long) :** Croisement EMA(13) > EMA(34) & Volume > Moyenne Volume (10).
*   **Sortie (Long) :** Croisement EMA(13) < EMA(34).
*   **Stoploss :** Fixe -20%.
*   **ROI :** Minimum 50%.
*   **Trailing Stop :** Désactivé.
*   **Concepts :**
    *   **Tendance :** Croisement EMAs classique.
    *   **Confirmation :** Filtre de volume sur l'entrée.
*   **Pistes :** Optimiser périodes EMAs/Volume MA, ajouter filtres (ADX, RSI), stoploss dynamique/trailing, revoir ROI, logique Short.

## Stratégie : `AwesomeMacd.py`

*   **Type :** Tendance / Momentum (Long Only par défaut, timeframe 1h).
*   **Indicateurs :** MACD (12, 26, 9), Awesome Oscillator (AO). *ADX calculé mais non utilisé.*
*   **Entrée (Long) :** MACD > 0 & AO > 0 & Croisement AO > 0.
*   **Sortie (Long) :** MACD < 0 & AO < 0 & Croisement AO < 0.
*   **Stoploss :** Fixe -25%.
*   **ROI :** Minimum 10%.
*   **Trailing Stop :** Désactivé.
*   **Concepts :**
    *   **Tendance / Momentum :** Combine MACD et AO pour confirmer le momentum. Entrée sur croisement zéro de l'AO avec MACD aligné.
*   **Pistes :** Utiliser ADX comme filtre, optimiser périodes MACD/AO, stoploss dynamique/trailing, logique Short, comparer vs MACD ou AO seuls.

## Stratégie : `Combined_NFIv6_SMA.py`

*   **Type :** Hybride / Opportunité (Long Only par défaut, timeframe 5m). Très complexe.
*   **Indicateurs :** Très large éventail (EMAs, SMAs, BB, RSI, MFI, CMF, CTI, SRSI, MACD, EWO, Williams %R, Heikin Ashi, indicateurs 1h, protections custom).
*   **Entrée (Long) :** Combinaison (OU) de 24 conditions activables/désactivables, chacune avec ses propres gardes/protections (tendance 1h, RSI 1h, "safe dip", "safe pump", etc.). Vise divers scénarios.
*   **Sortie (Long) :** Combinaison de `custom_sell` (très complexe : paliers profit/RSI, conditions "pump", "descending SMA", trailing custom, stoploss custom) et `populate_sell_trend` (8 conditions activables/désactivables).
*   **Stoploss :** Inactif (-99%), mais géré via `custom_sell` et `custom_stoploss` (simple).
*   **ROI :** Désactivé (10).
*   **Trailing Stop :** **Activé** (standard).
*   **Concepts :**
    *   **Opportunité / Hybride :** Exploitation de multiples configurations via conditions spécifiques.
    *   **Timeframes Multiples :** Utilisation intensive d'indicateurs 1h.
    *   **Gestion Risque Avancée :** Multiples logiques de sortie/stoploss personnalisées.
*   **Pistes :** Simplification, analyse de contribution des conditions, robustesse (risque sur-optimisation), logique Short.

## Stratégie : `ClucHAnix.py`

*   **Type :** Hybride / Opportunité (Long Only par défaut, timeframe 1m).
*   **Indicateurs :** Heikin Ashi, BB (40, 2sd sur HA), EMA (3, 50 sur HA), Volume MA (30), ROCR (28 sur HA), Fisher RSI (14), ROCR (168 sur HA 1h).
*   **Entrée (Long) :** Combine 2 scénarios (OU) basés sur rebond BB/HA ou retour moyenne EMA/BB, filtrés par ROCR 1h.
*   **Sortie (Long) :** Conditions sur Fisher RSI, bougies HA descendantes, position vs EMA(3) et BB médiane.
*   **Stoploss :** **Personnalisé** multi-niveaux basé sur profit.
*   **ROI :** Inactif (100%).
*   **Trailing Stop :** Désactivé.
*   **Concepts :**
    *   **Retour Moyenne / Range :** Logique d'entrée BB/HA.
    *   **Opportunité :** Capture de dips spécifiques.
    *   **Timeframes Multiples :** Filtre ROCR 1h.
    *   **Heikin Ashi :** Lissage des prix.
    *   **Gestion Risque Avancée :** Stoploss personnalisé.
*   **Pistes :** Tester impact filtre 1h, simplifier/optimiser conditions Cluc, tester autres indicateurs, comparer vs bougies standard, logique Short.

## Stratégie : `Schism.py`

*   **Type :** Hybride / Opportunité (Long Only par défaut, timeframe 5m).
*   **Indicateurs :** RMI (custom, 21/5 et 8/4), ROC (6), RSI (6 sur ROC), RSI (14 sur 1h), ADR (sur 1h).
*   **Entrée (Long) :** Logique complexe :
    *   *Si pas de trade :* RSI 1h > Seuil & Close près du plus bas 3j (ADR) & Tendance RMI locale baissière & RMI lent > Seuil & RMI rapide < Seuil & RSI(ROC) < Seuil.
    *   *Si trade ouvert (re-entry ?) :* Tendance RMI locale haussière & Profit actuel > Profit pic * facteur & RMI lent > Seuil dynamique.
*   **Sortie (Long) :** Logique complexe conditionnelle : Profit < Seuil dynamique & Tendance RMI locale baissière & (RMI lent croise sous 50 si gain OU sous 10 si perte) & (Conditions sur autres trades ouverts si applicable).
*   **Stoploss :** Fixe -40% (mais sortie custom agit comme stop dynamique).
*   **ROI :** Table ROI active.
*   **Trailing Stop :** Désactivé.
*   **Concepts :**
    *   **Opportunité / Hybride :** Combine retour moyenne (achat près du plus bas) avec filtres de tendance/momentum (RMI, RSI 1h).
    *   **Timeframes Multiples :** Utilisation RSI et ADR 1h.
    *   **Gestion de Portefeuille :** Sortie influencée par les autres trades.
    *   **Gestion Risque Avancée :** Sortie/stoploss dynamique complexe.
*   **Pistes :** Simplification logique entrée/sortie, tester composants isolément, robustesse, logique Short.

---

# Synthèse des Concepts et Pistes d'Amélioration

L'analyse de ces stratégies met en lumière plusieurs concepts et techniques applicables à différents régimes de marché. L'objectif principal reste d'optimiser le ratio **Profit Total / Drawdown Maximum**.

## 1. Stratégies de Tendance

*   **Objectif :** Capturer les grands mouvements directionnels.
*   **Concepts Clés :**
    *   **Identification Direction/Force :** Supertrend, ADX > seuil, Croisement DI+/DI-.
    *   **Confirmation :** Volume > Moyenne Mobile Volume, Momentum > 0 (pour long) / < 0 (pour short).
    *   **Gestion de Position :** **Trailing Stop Loss (ATR ou SAR)** semble crucial pour laisser courir les profits tout en protégeant contre les retournements. Le Trailing ATR de `AdaptiveTrendRider` a montré d'excellents résultats après optimisation.
    *   **Sortie :** Inversion de l'indicateur de tendance (Supertrend, DI), baisse de la force de tendance (ADX < seuil), inversion du momentum. La simple inversion Supertrend peut être améliorée avec confirmation (ex: clôture au-delà de la ligne).
*   **Pistes d'Amélioration (Focus Profit/Drawdown) :**
    *   **Améliorer le Win Rate :** Ajouter des filtres d'entrée plus stricts (ex: EMA long terme pour confirmer la tendance de fond, autres indicateurs de confirmation). **Important :** Ré-optimiser *tous* les paramètres après ajout d'un filtre.
    *   **Affiner la Sortie :** Tester des sorties basées sur la confirmation (clôture), la perte de momentum (MOM), ou la baisse de l'ADX pour potentiellement sortir plus tôt avant un retournement complet.
    *   **Optimisation Stop Loss :** Le multiplicateur ATR du trailing stop a un impact majeur. Une optimisation fine est nécessaire.

## 2. Stratégies de Range / Retour à la Moyenne

*   **Objectif :** Profiter des oscillations dans un marché latéral.
*   **Concepts Clés :**
    *   **Identification Range :** ADX < seuil (à tester comme filtre).
    *   **Niveaux Extrêmes :** Atteinte des Bandes de Bollinger (inférieure pour achat, supérieure pour vente).
    *   **Confirmation :** Indicateurs d'Oversold/Overbought (RSI < 30, Stochastique < 20 pour achat ; RSI > 70, Stochastique > 80 pour vente). La logique `BBRSI` avec RSI > 25 pour acheter est atypique et mériterait d'être revue.
    *   **Sortie :** Atteinte de la bande opposée ou de la ligne médiane des BB, atteinte d'un niveau RSI/Stochastique neutre ou opposé, ROI rapide.
    *   **Stop Loss :** Souvent larges et fixes, ce qui peut être dangereux si une tendance démarre. Un stop basé sur l'ATR ou la volatilité (largeur des BB) pourrait être plus adaptatif.
*   **Pistes d'Amélioration (Focus Profit/Drawdown) :**
    *   **Filtrage :** N'activer la logique que si le marché est effectivement en range (ADX bas).
    *   **Seuils Indicateurs :** Optimiser les niveaux RSI/Stochastique et les écarts-types des BB.
    *   **Stop Loss Dynamique :** Remplacer les stops fixes larges par des stops ATR ou basés sur la volatilité.
    *   **Gestion des Sorties :** Éviter de sortir trop tôt (ex: sur la médiane BB) si un mouvement plus ample semble possible.

## 3. Stratégies d'Opportunité / Hybrides

*   **Objectif :** Capturer des configurations spécifiques ou combiner différentes logiques.
*   **Concepts Clés :**
    *   **Combinaison :** Utiliser des logiques différentes pour l'entrée (ex: `CombinedBinHAndCluc`).
    *   **Patterns Spécifiques :** Détection de divergences, de patterns de chandeliers, de conditions de survente/surachat extrêmes combinées à d'autres facteurs.
    *   **Timeframes Multiples :** Utiliser des indicateurs sur des timeframes plus longs pour filtrer les signaux sur timeframe court.
*   **Pistes d'Amélioration (Focus Profit/Drawdown) :**
    *   **Clarifier la Logique :** Si combinaison, s'assurer que les logiques ne se contredisent pas ou ne se cannibalisent pas. Tester chaque logique séparément d'abord.
    *   **Robustesse :** Vérifier que les "opportunités" ne sont pas trop rares ou trop spécifiques à une période passée (risque de sur-optimisation).
    *   **Gestion du Risque :** Adapter le stop loss et la sortie à la nature de l'opportunité visée.

## Conclusion Générale

L'analyse montre une variété d'approches. Notre stratégie `AdaptiveTrendRider` optimisée est une base solide pour le **suivi de tendance**. Pour améliorer son Win Rate, l'ajout de filtres (comme l'EMA 20/50 ou 50/200) suivi d'une **nouvelle hyperoptimisation complète** est la prochaine étape logique. Pour les marchés **latéraux**, des stratégies comme `BBRSI` offrent des pistes mais nécessitent des ajustements (seuils RSI, filtre ADX, stoploss dynamique). Les stratégies **hybrides** peuvent être puissantes mais demandent une conception et une validation rigoureuses pour éviter la sur-optimisation. Dans tous les cas, l'optimisation des paramètres *après* modification de la logique et la surveillance constante du ratio **Profit/Drawdown** sont essentielles.

</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
user_data/strategy_analysis_summary.md

# VSCode Open Tabs
user_data/strategies/AdaptiveTrendRider.py
user_data/strategy_analysis_summary.md

# Current Time
4/29/2025, 10:16:57 PM (Europe/Paris, UTC+2:00)

# Context Window Usage
775,974 / 1,000K tokens used (78%)

# Current Mode
ACT MODE
</environment_details>
