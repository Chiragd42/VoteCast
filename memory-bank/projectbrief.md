# Project Brief

## Overview
VoteCast is a Python-based, multi-client polling platform built on a multi-server architecture. Clients connect to a leader server, create or join poll groups, and run distributed votes. The system uses reliable multicast patterns, leader election, and replicated state across servers.

## Goals
- Provide reliable group creation, membership, and voting across multiple clients.
- Maintain availability via a leader + backup server model with leader election.
- Ensure votes are reliably multicast and results are shared with participants.

## Core Requirements
- Support discovery of servers and leader election (Hirschberg-Sinclair algorithm).
- Provide client registration/authentication tokens.
- Allow creation/join/leave of groups and starting votes per group.
- Reliably multicast vote requests and results to group members.
- Replicate server state to newly elected leaders.

## Scope Notes
- CLI-driven server and client.
- UDP sockets for communication.
- Python runtime with minimal dependencies (click for server CLI). 

## Recent Enhancements
- **Client-Server Communication**: Fixed VOTE_ACK message handling to ensure proper server-side vote processing
- **Voting Fault Tolerance**: Enhanced leader state validation to trigger elections when needed
- **Ordered Reliable Multicast**: Improved FO multicast logic to wait for all client acknowledgments
- **State Replication**: Fixed set/list conversion issues to prevent data corruption during leader handoff
- **Client Notification**: Added proper notification when single server remains after crash
- **Server Unavailability**: Added clear "No servers available" message when all servers crash
- **Logging**: Reduced excessive FO multicast logging for cleaner output
- **Multi-Device Compatibility**: Verified system works across different devices on same network

## Exam Readiness Status
✅ **All critical functionality working**
✅ **Fault tolerance mechanisms operational**
✅ **Clean logging and error messages**
✅ **Multi-device testing support confirmed**
✅ **15-minute exam demonstration ready**

## Technical Stack
- **Language**: Python 3
- **Communication**: UDP sockets with multicast
- **CLI Framework**: click (server)
- **Networking**: Multicast group 224.1.1.1:5007
- **Platform**: Cross-platform (Linux, macOS, Windows)

## Key Features
- **Dynamic Discovery**: Servers automatically discover each other via multicast
- **Leader Election**: Hirschberg-Sinclair algorithm ensures single leader
- **Fault Tolerance**: Automatic failover when leader crashes
- **Reliable Multicast**: FO multicast ensures all clients receive votes
- **State Replication**: Leader state replicated to backups
- **Client Management**: Token-based authentication and group membership