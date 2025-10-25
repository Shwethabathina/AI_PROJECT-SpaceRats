Space Rats – Adaptive AI Navigation and Target Tracking

Space Rats is an artificial intelligence simulation developed for CS520: Introduction to AI. It models how intelligent bots can localize themselves and track a hidden or moving target in an uncertain, partially observable environment.

Project Overview

The simulation takes place on a 30×30 spaceship grid containing open and closed cells.
A bot must locate and capture a “space rat” that may be stationary or moving randomly.
The challenge lies in reasoning under uncertainty — the bot starts without knowing where it is or where the rat is located and must rely on limited, probabilistic sensor data.

Bot Versions

Bot 1 – Baseline (Stationary Rat):
Uses belief-based reasoning and Breadth-First Search (BFS) to chase the most probable rat location.

Bot 1 – Baseline (Moving Rat):
Same as above, but struggles as the rat moves randomly — highlighting limitations of purely reactive logic.

Bot 2 – Smarter Bot (Stationary Rat):
Introduces utility-based decision-making to balance belief confidence and movement cost, improving efficiency.

Bot 2 – Smarter Bot (Moving Rat):
Implements belief propagation to predict rat motion and adapts dynamically using probabilistic updates.

Core Concepts

Bayesian inference for belief updates

Sensor modeling using exponential decay (controlled by α)

Utility-based decision-making combining probability and movement cost

Motion update modeling for dynamic target tracking

Results

Optimal performance observed at moderate α (0.30–0.55) where sensor feedback is balanced.

Bot 2 demonstrates superior adaptability, reduced wasted movement, and better performance in dynamic environments.

Key Takeaway

The project illustrates how probabilistic reasoning, real-time replanning, and uncertainty handling enable AI agents to make intelligent decisions — concepts relevant to robotics, search and rescue, and autonomous systems.
