import math
import time
from typing import Optional

from ring import build_ring


def _ensure_ring_ready(server, *, candidate_id: Optional[str] = None) -> bool:
    """Try to ensure ring neighbors are set.

    Returns True when both neighbors exist.
    This is intentionally minimal and side-effect-safe: we only
    (a) ensure self is in membership, (b) optionally add a candidate id,
    (c) rebuild the ring from the current membership view.
    """
    if server.id not in server.servers:
        server.servers.add(server.id)
    if candidate_id:
        server.servers.add(candidate_id)
    if server.left is None or server.right is None:
        build_ring(server)
    return server.left is not None and server.right is not None


def hs_start(server, *, manual: bool = False):
    if server.election_in_progress:
        server.log("Election already in progress!")
        return

    # Do not run HS with a single node; wait for discovery of a peer
    if len(server.servers) <= 1:
        server.log("Cannot start HS: only one server in view")
        server.election_in_progress = False
        return

    if server.left is None or server.right is None:
        # Ensure ring is ready before starting election
        if not _ensure_ring_ready(server):
            server.log("Cannot start HS: ring not ready after rebuild")
            server.election_in_progress = False
            server.phase = 0
            return

    server.election_in_progress = True
    server.election_done.clear()
    server.leader = None
    server.is_leader = False
    server.phase = 0
    server.election_started_at = time.time()
    server.log(server.color_text("Starting Hirschberg-Sinclair election...", server.COLOR_GREEN))
    hs_send_neighbors(server)
    if manual:
        server.election_done.wait(timeout=10)


def hs_send_neighbors(server):
    distance = 2 ** server.phase
    server.pending_replies = 2

    for direction in ("LEFT", "RIGHT"):
        msg = {
            "type": "HS_ELECTION",
            "id": server.id,
            "phase": server.phase,
            "direction": direction,
            "hop": distance
        }
        neighbor = server.left if direction == "LEFT" else server.right
        if neighbor is None:
            server.log(f"HS send skipped: neighbor None for direction {direction}")
            server.pending_replies -= 1
            continue
        server.send(neighbor, msg)

    # If both neighbors missing, abort election
    if server.pending_replies <= 0:
        # Abort: no neighbors available
        server.election_in_progress = False
        server.phase = 0
        server.leader = server.leader or None
        server.election_done.set()


def hs_election(server, msg):
    cid = msg.get("id")
    hop = msg.get("hop")
    direction = msg.get("direction")

    if cid is None or hop is None or direction is None or direction not in ["LEFT", "RIGHT"]:
        server.log(f"Error: Invalid HS_ELECTION: {msg}")
        return

    # If ring isn't built yet (common on late join), build it and continue.
    if not _ensure_ring_ready(server, candidate_id=cid):
        server.log(f"HS_ELECTION: ring not ready yet; rebuilding and retrying later")
        # Trigger a fresh election if we're not already in one; avoids deadlock.
        if not server.election_in_progress and len(server.servers) > 1:
            hs_start(server)
        return

    neighbor = server.left if direction == "LEFT" else server.right

    if cid < server.id:
        # Swallow message from lower IDs or start own election
        if not server.election_in_progress:
            hs_start(server)
        return

    if hop > 1:
        msg["hop"] -= 1
        server.send(neighbor, msg)
    else:
        reply = {
            "type": "HS_REPLY",
            "id": cid,
            "direction": msg["direction"]
        }
        server.send(neighbor, reply)


def hs_reply(server, msg):
    cid = msg.get("id")
    direction = msg.get("direction")

    if cid is None or direction is None or direction not in ["LEFT", "RIGHT"]:
        server.log(f"Error: Invalid HS_REPLY: {msg}")
        return

    if not _ensure_ring_ready(server, candidate_id=cid):
        server.log("HS_REPLY: ring not ready yet; rebuilding and retrying later")
        if not server.election_in_progress and len(server.servers) > 1:
            hs_start(server)
        return

    neighbor = server.left if direction == "LEFT" else server.right

    if cid != server.id:
        server.send(neighbor, msg)
        return

    server.pending_replies -= 1

    if server.pending_replies == 0:
        server.phase += 1
        if 2 ** server.phase >= len(server.servers):
            hs_declare_leader(server)
        else:
            hs_send_neighbors(server)


def hs_declare_leader(server):
    server.log(server.color_text("HS: I am the leader", server.COLOR_GREEN))
    server.leader = server.id
    server.is_leader = True
    server.election_in_progress = False
    server.election_done.set()
    server.election_started_at = None
    msg = {"type": "HS_LEADER", "id": server.id}
    server.send(server.left, msg)


def hs_leader(server, msg):
    cid = msg.get("id")

    if cid is None:
        server.log(f"Error: Expected key 'id': {msg}")
        return

    # If this server was the leader before, replicate its whole state to the new leader.
    if server.is_leader and cid != server.id:
        server.send_replicate_state(cid)

    server.leader = cid
    server.is_leader = (server.leader == server.id)
    server.election_in_progress = False
    server.election_done.set()
    server.election_started_at = None
    server.log(server.color_text(f"HS: Leader elected: {server.leader}", server.COLOR_GREEN))

    # CRITICAL FIX: Add null check before sending
    if server.left != cid and server.left is not None:
        server.send(server.left, msg)
