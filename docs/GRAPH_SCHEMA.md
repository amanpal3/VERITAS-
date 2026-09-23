# Graph Schema - VERITAS

## Node Labels
- `:Person` (id, name, aliases, risk_score, primary_role)
- `:Phone` (number, imsi, provider)
- `:Vehicle` (plate, model, color)
- `:Location` (name, address, coordinates)
- `:Organization` (name, type, registration_no)
- `:BankAccount` (account_no, bank_name)

## Relationship Types
- `[:CALLED {calls_count, total_duration, last_timestamp}]`
- `[:TRANSACTED_WITH {amount, frequency, last_timestamp}]`
- `[:ASSOCIATED_WITH {confidence, source_document}]`
- `[:OWNS]`
- `[:LOCATED_AT {timestamp}]`
- `[:MEMBER_OF {role}]`
