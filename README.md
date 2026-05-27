# Polymarket "Bracket" Strategy Bot (System 7)

## Objective

Build a low-risk, automated scanner and execution bot for Polymarket that identifies and captures "Bracket" arbitrage opportunities. 

A Bracket opportunity occurs when the combined Ask price of both the "Yes" and "No" tokens in a binary market is strictly less than $1.00 (after accounting for fees). By buying both sides simultaneously, the bot locks in a guaranteed payout of $1.00 upon market resolution, regardless of the outcome.

## Core Logic

$$\text{Total Cost} = \text{Ask}_{\text{Yes}} + \text{Ask}_{\text{No}}$$
$$\text{If Total Cost} < \$1.00 - \text{Target Profit Margin}: \text{Execute Buy on Both}$$

## Current Phase

This repository is currently in the **specification and architecture phase**.
Initial implementation will focus on the **Scanner** (identifying opportunities) before implementing the **Executor** (placing trades).

## Safety Notice

While this strategy has zero directional risk, it carries **execution risk** (leg-in risk). If one side of the trade fills and the other fails, the bot is left with an unhedged directional position. The execution engine must handle simultaneous routing and fallback cancellations.
