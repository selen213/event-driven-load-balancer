#!/usr/bin/env python3
"""
Load Balancer Simulation - Event Driven M/M/1/N Queue System

This program simulates a simplified load balancer that distributes requests
across multiple servers. It uses an event driven simulation approach where
events (arrivals and departures) are processed in chronological order

Key components:
- Request: Represents a service request with arrival, service start, and finish times
- Server: Models a single server with a queue (M/M/1/N queue)
- simulate(): Main event driven simulation loop

After time T, no new arrivals occur, but all requests already in the
system (in queue or being served) continue to completion.
"""

import sys
import random
from collections import deque


# Data structures
class Request:
    """Represents a single service request"""
    def __init__(self, arrival_time):
        self.arrival = arrival_time
        self.service_start = None
        self.finish = None


class Server:
    """
    Models an M/M/1/N queue server
    - Qi: Maximum queue size (not including the request in service)
    - mu: Service rate (requests per time unit)
    """
    def __init__(self, Qi, mu):
        self.Qi = Qi                  # queue size (NOT including service)
        self.mu = mu
        self.queue = deque()
        self.busy = False
        self.current = None
        self.next_departure = float('inf')

        # statistics
        self.served = 0
        self.dropped = 0
        self.sum_wait = 0.0
        self.sum_service = 0.0

    def capacity_full(self):
        """Check if server is at full capacity (1 in service + Qi in queue)"""
        total = (1 if self.busy else 0) + len(self.queue)
        return total >= 1 + self.Qi

    def start_service(self, req, t):
        """Begin serving a request"""
        req.service_start = t
        service_time = random.expovariate(self.mu)
        req.finish = t + service_time

        self.current = req
        self.busy = True
        self.next_departure = req.finish

        # Accumulate statistics
        self.sum_wait += req.service_start - req.arrival
        self.sum_service += service_time

    def arrival(self, req, t):
        """Handle arrival of a new request"""
        if not self.busy:
            # Server is idle, start service immediately
            self.start_service(req, t)
        elif not self.capacity_full():
            # Server is busy but queue has space
            self.queue.append(req)
        else:
            # Server and queue are full, drop the request
            self.dropped += 1

    def departure(self, t):
        """Handle departure of a completed request"""
        self.served += 1

        if self.queue:
            # Start serving next request in queue
            nxt = self.queue.popleft()
            self.start_service(nxt, t)
        else:
            # No more requests, server becomes idle
            self.busy = False
            self.current = None
            self.next_departure = float('inf')



# Simulator

def simulate(T, P, lambd, Qs, mus):
    """
    Event driven simulation of load balancer with M servers
    
    Args:
        T: Simulation duration (no new arrivals after T)
        P: List of routing probabilities for each server
        lambd: Arrival rate (requests per time unit)
        Qs: List of queue sizes for each server
        mus: List of service rates for each server
    
    Returns:
        Tuple of (A, B, Tend, Tw, Ts) where:
        - A: Number of served requests
        - B: Number of dropped requests (only due to full queue)
        - Tend: Time when last request finished
        - Tw: Average wait time
        - Ts: Average service time
    """
    M = len(mus)
    servers = [Server(Qs[i], mus[i]) for i in range(M)]

    t = 0.0
    next_arrival = random.expovariate(lambd)

    # Event driven simulation loop
    while True:
        # Disable arrivals at/after time T (including T)
        if next_arrival >= T and next_arrival != float('inf'):
            next_arrival = float('inf')

        # Find next departure event across all servers
        next_departure = min(s.next_departure for s in servers)
        next_event = min(next_arrival, next_departure)

        # Nothing left to process
        if next_event == float('inf'):
            break

        # Move to next event time
        t = next_event

        # Process arrival event (only if strictly before T)
        if next_arrival <= next_departure and next_arrival < T:
            # Route request to a server based on probabilities
            r = random.random()
            acc = 0.0
            chosen = M - 1  # FIX: Safe default for edge cases
            for i in range(M):
                acc += P[i]
                if r <= acc:
                    chosen = i
                    break

            req = Request(t)
            servers[chosen].arrival(req, t)

            # Schedule next arrival
            next_arrival = t + random.expovariate(lambd)

        # Process departure event
        else:
            # FIX: Process ALL departures at this time (no break)
            for s in servers:
                if abs(s.next_departure - t) < 1e-12:
                    s.departure(t)

        # Stop when no arrivals AND system empty
        if next_arrival == float('inf'):
            if all((not s.busy) and len(s.queue) == 0 for s in servers):
                break

    # Compute final statistics
    A = sum(s.served for s in servers)
    B = sum(s.dropped for s in servers)
    Tw = 0.0 if A == 0 else sum(s.sum_wait for s in servers) / A
    Ts = 0.0 if A == 0 else sum(s.sum_service for s in servers) / A

    # Tend = time of last event (last departure)
    Tend = t

    return A, B, Tend, Tw, Ts




# Main

def main():
    args = sys.argv[1:]

    # Basic argument count check
    if len(args) < 5:
        print("Invalid input")
        sys.exit(1)

    try:
        idx = 0
        T = float(args[idx]); idx += 1
        M = int(args[idx]); idx += 1

        # Validate M
        if M <= 0:
            print("Invalid input")
            sys.exit(1)

        # Check if we have enough arguments
        expected_args = 2 + M + 1 + M + M  # T M P1..PM λ Q1..QM μ1..μM
        if len(args) != expected_args:
            print("Invalid input")
            sys.exit(1)

        # Parse probabilities
        P = list(map(float, args[idx:idx+M]))
        idx += M
        
        # Parse arrival rate
        lambd = float(args[idx]); idx += 1

        # Parse queue sizes
        Qs = list(map(int, args[idx:idx+M]))
        idx += M
        
        # Parse service rates
        mus = list(map(float, args[idx:idx+M]))

    except (ValueError, IndexError):
        print("Invalid input")
        sys.exit(1)

    # Validate T is non-negative (T=0 is valid edge case: no arrivals)
    if T < 0:
        print("Invalid input")
        sys.exit(1)

    # Validate probabilities sum to 1
    if abs(sum(P) - 1.0) > 1e-9:
        print("Invalid input")
        sys.exit(1)
    
    # Validate all probabilities are in [0,1]
    if any(p < 0 or p > 1 for p in P):
        print("Invalid input")
        sys.exit(1)
    
    # Validate arrival rate is positive
    if lambd <= 0:
        print("Invalid input")
        sys.exit(1)
    
    # Validate queue sizes are non-negative
    if any(q < 0 for q in Qs):
        print("Invalid input")
        sys.exit(1)
    
    # Validate service rates are positive
    if any(mu <= 0 for mu in mus):
        print("Invalid input")
        sys.exit(1)

    # Run simulation
    A, B, Tend, Tw, Ts = simulate(T, P, lambd, Qs, mus)

    # Output results
    print(f"{A} {B} {Tend:.4f} {Tw:.4f} {Ts:.4f}")


if __name__ == "__main__":
    main()