# System Patterns

## Architecture Overview
- Multi-server cluster using UDP sockets for communication.
- Servers discover peers via multicast and form a logical ring.
- Hirschberg-Sinclair leader election selects a single leader.
- Leader communicates with clients; followers receive replicated state.

## Key Patterns
- **Leader-based coordination**: Only leader handles client requests and multicasts results.
- **State replication**: Leader replicates state to backups and on leader handoff.
- **Reliable multicast (FO)**: Vote requests are reliably multicast with sequence numbers and pending retransmits.
- **FIFO per-sender ordering**: Clients maintain hold-back queues per sender to process votes in order.
- **Heartbeat detection**: Servers send heartbeat messages to detect crashes.

## Component Relationships
- `server.py` manages discovery, election, client handling, replication, and multicast.
- `client.py` discovers leader, registers, manages groups and voting, and handles vote ordering.
- `config.py` provides multicast configuration and buffer sizing.

## Critical Implementation Paths
- Server discovery → ring build → HS election → leader set.
- Client leader discovery → registration → group management → vote lifecycle.
- FO multicast: leader sends vote → client acks → leader finalizes vote and broadcasts results.

## Recent Pattern Enhancements
- **Fault Tolerance**: Enhanced leader state validation with continuous monitoring loop
- **Client Notification**: Added immediate client notification when single server remains after crash
- **Server Discovery**: Improved crash detection and ring rebuilding logic
- **Vote Processing**: Enhanced VOTE_ACK handling with proper duplicate prevention and validation
- **Error Recovery**: Added server unavailability detection with clear user messaging
- **Logging**: Optimized FO multicast logging frequency for better observability

## Robustness Improvements
- **Crash Recovery**: Automatic leader election when servers crash
- **Network Partitions**: Graceful handling of network splits and reunions
- **Client Management**: Proper cleanup and re-authentication on leader changes
- **Vote Integrity**: Server-side validation to prevent duplicate and invalid votes