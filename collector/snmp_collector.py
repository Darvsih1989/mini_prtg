import asyncio
import sqlite3
from datetime import datetime

from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine, CommunityData, UdpTransportTarget,
    ContextData, ObjectType, ObjectIdentity, get_cmd
)

from storage.db import DB_FILE, init_db

MAX_32BIT = 2 ** 32

# --------------------------------
# SNMP GET helper
# --------------------------------
async def snmp_get(engine, auth, target, context, oid):
    errInd, errStat, errIdx, varBinds = await get_cmd(
        engine, auth, target, context,
        ObjectType(ObjectIdentity(oid))
    )
    if errInd or errStat:
        return None
    for _, val in varBinds:
        return int(val)
    return None

# --------------------------------
# Interface discovery
# --------------------------------
async def get_interfaces(ip, community):
    from pysnmp.hlapi.v3arch.asyncio import walk_cmd

    engine = SnmpEngine()
    auth = CommunityData(community, mpModel=1)
    target = await UdpTransportTarget.create((ip, 161))
    context = ContextData()

    indexes, names, aliases = [], [], []

    async for _, _, _, varBinds in walk_cmd(
        engine, auth, target, context,
        ObjectType(ObjectIdentity("1.3.6.1.2.1.2.2.1.1")),
        lexicographicMode=False
    ):
        for _, v in varBinds:
            indexes.append(int(v))

    async for _, _, _, varBinds in walk_cmd(
        engine, auth, target, context,
        ObjectType(ObjectIdentity("1.3.6.1.2.1.2.2.1.2")),
        lexicographicMode=False
    ):
        for _, v in varBinds:
            names.append(str(v))

    async for _, _, _, varBinds in walk_cmd(
        engine, auth, target, context,
        ObjectType(ObjectIdentity("1.3.6.1.2.1.31.1.1.1.18")),
        lexicographicMode=False
    ):
        for _, v in varBinds:
            aliases.append(str(v))

    interfaces = []
    for i in range(len(indexes)):
        interfaces.append({
            "index": indexes[i],
            "name": names[i],
            "alias": aliases[i] if i < len(aliases) and aliases[i] else names[i]
        })

    return interfaces

# --------------------------------
# Traffic collector
# --------------------------------
async def collect_interface(ip, community, idx, name, interval):
    init_db()

    engine = SnmpEngine()
    auth = CommunityData(community, mpModel=1)
    target = await UdpTransportTarget.create((ip, 161))
    context = ContextData()

    OID_IN = f"1.3.6.1.2.1.2.2.1.10.{idx}"
    OID_OUT = f"1.3.6.1.2.1.2.2.1.16.{idx}"

    prev_in = prev_out = None

    while True:
        await asyncio.sleep(interval)
        ts = datetime.now().strftime("%H:%M:%S")

        cin = await snmp_get(engine, auth, target, context, OID_IN)
        cout = await snmp_get(engine, auth, target, context, OID_OUT)

        if cin is None or cout is None:
            continue

        if prev_in is None:
            prev_in, prev_out = cin, cout
            continue

        din = (cin - prev_in) % MAX_32BIT
        dout = (cout - prev_out) % MAX_32BIT

        rx = din * 8 / 1_000_000
        tx = dout * 8 / 1_000_000

        prev_in, prev_out = cin, cout

        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO traffic VALUES (?, ?, ?, ?)",
            (ts, name, rx, tx)
        )
        conn.commit()
        conn.close()
