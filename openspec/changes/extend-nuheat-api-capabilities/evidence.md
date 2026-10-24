# Capability evidence and outstanding gates

2026-10-24. Public-document review only; no vendor message was sent. The user
authorized local apply, a separate beta commit on the existing preparation
branch, and a final read-only live check. This does not confirm API semantics or
authorize implementing controls that fail this proposal's gates.

## H — hold duration: unresolved

The [guide](https://api.nam.mynuheat.com/) describes a 23-hour window using
v1 `holdSetPointDateTime`. The reviewed v2 Swagger `ModeHold.holdUntil` has a
date-time type without duration or boundary metadata. No applicable answer
settles the v2 exact boundary, clock tolerance or retaining longer existing
holds. The documented restriction is real; its full proposed enforcement
contract is unverified. No new cap, expiry clipping or hold rewrite was added.

## P — notifications: unresolved

The guide documents `/v2/notificationsHost`, `Subscribe`, `Unsubscribe` and a
`Notify` callback. Its JavaScript example includes a token in the connection
URL. It does not prove the precise currently supported protocol/negotiation,
token rotation, retry/session limits or isolated async-client lifecycle.
No transport dependency was selected, connection attempted or option enabled.
Existing polling and delayed command reconciliation are unchanged.

## E — energy reporting: unresolved

v1 Swagger describes relay minutes and estimated energy/charge fields grouped
by day, week or month. The guide does not resolve the proposal's timezone/DST,
bucket corrections, load configuration and missing-versus-zero contract.
No reporting entities, polling, inferred power, cost or history imports were
added. These omissions prevent inaccurate statistics, not a working thermostat.

## R — relative adjustment: partially documented, gate unresolved

v2 Swagger `eTemperatureType` documents 0 = Absolute and 1 = Relative, described
as adding to current thermostat temperature. The reference temperature remains
ambiguous for our action, as do signed scaling and the full mode/expiry
preservation contract. The existing SDK rejects explicit interpretation and
continues to use its validated absolute calls. No relative writes were tried.

## Next evidence

[vendor-questions.md](vendor-questions.md) contains the unsent questions and an
answer template. An authorized vendor response or applicable updated public
documentation can resolve a gate. Separately scoped isolated API tests can
supplement that evidence; they must not silently alter production or use prior
completed hardware approvals. Tasks 2.1, 3.1, 4.1 and 5.1 remain unchecked until
their required evidence exists. Their dependent implementation tasks are also
unchecked. Diagnostics is independent and does not need these gates.

Sources: [public guide](https://api.nam.mynuheat.com/),
[v1 Swagger](https://api.nam.mynuheat.com/swagger/v1/swagger.json),
[v2 Swagger](https://api.nam.mynuheat.com/swagger/v2/swagger.json).
