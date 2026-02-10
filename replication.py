def send_replicate_state(server, new_leader):
    # Ensure all sets are converted to lists before sending
    state = {
        "type": "REPL_STATE",
        "clients": {cid: {"token": client["token"], "addr": client["addr"]} for cid, client in server.clients.items()},
        "groups": {name: {"owner": group["owner"], "members": list(group["members"])} for name, group in server.groups.items()},
        "votes": server.votes,
        "S": server.S,
        "fo_pending": server.fo_pending,
    }
    server.send(new_leader, state)


def replicate_state_apply(server, msg):
    # Merge clients
    for cid, client in msg["clients"].items():
        server.clients[cid] = {"token": client["token"], "addr": tuple(client["addr"])}

    # Merge groups - CRITICAL FIX: Ensure members are always sets
    for name, group in msg["groups"].items():
        if name not in server.groups:
            # Convert list to set for proper set operations
            server.groups[name] = {"owner": group["owner"], "members": set(group["members"])}
        else:
            # Ensure existing members is a set before updating
            if not isinstance(server.groups[name]["members"], set):
                server.groups[name]["members"] = set(server.groups[name]["members"])
            # Update with new members (set operation)
            server.groups[name]["members"].update(set(group["members"]))
            # Update owner if needed
            server.groups[name]["owner"] = group["owner"]

    # Merge votes
    for vote_id, vote in msg["votes"].items():
        server.votes[vote_id] = vote

    # Merge FO state
    for g, seq in msg["S"].items():
        server.S[g] = max(server.S.get(g, 0), seq)

    for key, pending in msg["fo_pending"].items():
        if key not in server.fo_pending:
            server.fo_pending[key] = pending
        else:
            # Optional: merge pending sets if you want
            server.fo_pending[key]["pending"].update(pending.get("pending", set()))
            server.fo_pending[key]["deadline"] = max(server.fo_pending[key]["deadline"], pending["deadline"])

    # Notify clients about new leader
    tell_clients_about_new_leader(server)


def tell_clients_about_new_leader(server):
    for cid, client in server.clients.items():
        server.leader_send(client["addr"], {"type": "NEW_LEADER", "id": server.id})