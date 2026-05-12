# Event-Driven Load Balancer Simulator

An event-driven simulation of a distributed load balancer system based on M/M/1/N queueing models.

This project was developed as part of a Computer Systems / Queueing Systems assignment at the Technion.

## Overview

The simulator models a load balancer that distributes incoming requests across multiple servers according to configurable routing probabilities.

Each server behaves as an independent:

- M/M/1/N queue
- Finite-capacity queue system
- Exponential arrival and service processes

The system supports:

- Multiple heterogeneous servers
- Probabilistic request routing
- Queue capacity limits
- Request drops when queues are full
- Event-driven simulation architecture
- Statistical analysis of performance metrics

---

## Features

- Event-driven simulation engine
- Multi-server load balancing
- Configurable queue sizes
- Configurable service rates
- Exponential inter-arrival and service times
- Queue overflow handling
- Performance metrics collection
- Extensive automated testing suite

---

## Performance Metrics

The simulator computes:

- `A` — Number of served requests
- `B` — Number of dropped requests
- `Tend` — Time when the final request completed
- `Tw` — Average waiting time before service
- `Ts` — Average service time

---

## System Model

Each server is modeled as:

- Single server queue
- Finite buffer capacity
- FIFO scheduling
- Exponential service distribution

Requests are routed using probability distribution:

P1 + P2 + ... + Pm = 1

---

## Project Structure

```bash
.
├── final.py               # Main simulator implementation
├── simulator              # Executable simulator
├── test_simulator.py      # Automated testing suite
├── makefile               # Build automation
└── dry.pdf                # Theoretical analysis and report
