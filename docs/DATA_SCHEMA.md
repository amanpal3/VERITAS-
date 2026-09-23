# Data Schema - VERITAS

## Raw Sources
1. **FIR / Police Reports**: Unstructured text with incident summary, dates, suspect names, locations.
2. **Call Detail Records (CDRs)**: Caller MSISDN, Receiver MSISDN, Timestamp, Duration, Cell Tower ID.
3. **Financial Records**: Sender Account, Receiver Account, Amount, Currency, Timestamp, Transaction Type.
4. **Surveillance / Field Intel**: Suspect spotted with associate at location, Vehicle plate number.

## Intermediate Processed Schemas
Standardized JSON objects output by AI extraction before loading into Neo4j.
