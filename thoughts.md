Bioinformatics search platform:

```
┌─────────────────────────┬───────────────────────────┬─────────────────────────────┐
│          Pool           │          Source           │              R              │
├─────────────────────────┼───────────────────────────┼─────────────────────────────┤
│ Query compute           │ App Engine                │ per query                   │
├─────────────────────────┼───────────────────────────┼─────────────────────────────┤
│ Data storage + indexing │ Elasticsearch VMs + disks │ per GB-h                    │
├─────────────────────────┼───────────────────────────┼─────────────────────────────┤
│ Idle / baseline         │ ES cluster sitting warm   │ needs amortization decision │
└─────────────────────────┴───────────────────────────┴─────────────────────────────┘
```

The idle ES cluster cost can be either amortized across queries (inflating C/query) or across stored data (inflating C/GB-h), or split it proportionally.

- The ES cluster exists for two reasons: serving queries and holding indexed data. If you had zero data, you wouldn't need the cluster. If you had zero queries, you'd still need storage (but could use cheaper cold storage instead of an ES cluster).
- Amortizing all idle cost into C/query would make low-traffic months look terrible and high-traffic months look efficient. But the cluster size is driven primarily by data volume, not query volume.                                                                                                                                                                                              
- Amortizing all idle cost into C/GB-h ignores that the cluster is kept warm specifically for query latency.
