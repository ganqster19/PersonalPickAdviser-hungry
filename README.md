# PersonalPickAdviser-hungry
Statistical personal draft analysis tool for League of Legends using Riot API.
# LoL Draft Science: Advanced Matchup Analyzer

## Project Overview
This project is a statistical analysis tool developed to optimize drafting phases in League of Legends. By leveraging **Big Data** from high-ELO (Challenger/Grandmaster) matches and combining it with **Personal Performance Metrics**, it calculates the most optimal champion picks using a weighted scoring algorithm.

## Features
* **Data Mining:** Automated crawler collecting match data via Riot API `match-v5`.
* **Hybrid Scoring Engine:** Uses a physics-inspired formula weighting Global Meta (40%) and Personal Skill (60%).
* **Safety Analysis:** Analyzes win-rate variance to suggest safe blind picks.

## How It Works
1.  **Miner:** Scrapes thousands of matches to build a meta dataset.
2.  **Stats:** Analyzes the user's personal match history for specific matchup proficiency.
3.  **Engine:** Combines both datasets to recommend the best statistical pick against an enemy champion.

## Disclaimer
This project complies with Riot Games' third-party policies. It relies solely on public API data for statistical inference and does not interact with the game client.
