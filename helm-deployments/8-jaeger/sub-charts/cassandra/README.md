
```sh
k port-forward svc/jaeger-cassandra 9042:9042 -n jaeger-cassandra

# connect to cassandra  
cqlsh -u cassandra -p root1234

# connect to jaeger keyspace
cqlsh -u cassandra -p root1234 -k jaeger localhost 9042
```

```sql
CREATE KEYSPACE IF NOT EXISTS jaeger WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
```
