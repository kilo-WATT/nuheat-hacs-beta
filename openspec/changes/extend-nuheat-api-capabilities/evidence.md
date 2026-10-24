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

## Follow-up request to complete remaining tasks

2026-10-24: The user requested completion of all pending work. A fresh public
documentation search did not resolve H/P/E/R. A targeted connected-email search
for NuHeat/Chemelex API correspondence returned no messages. No vendor response
or new applicable protocol/hold/energy/relative contract can be claimed.

A concise [vendor request](vendor-request.md) is prepared for user review and
recipient authorization. It has not been sent. No additional runtime changes,
account probes, thermostat commands or production operations were performed in
this follow-up. The twelve dependent tasks remain unchecked; requesting their
completion does not provide the missing external evidence.

## Public issue outreach and newly located prior evidence

2026-10-24: At the user's explicit request, posted an account-free comment to
@PatrickHendrickx on the original Home Assistant issue, not by email:
https://github.com/home-assistant/core/issues/175923#issuecomment-6380330250
The comment was re-read and its text verified after posting.

Reading the original issue uncovered relevant vendor answers missed in the
earlier documentation/email search. Patrick stated that v2 explicit holds have
a maximum of 24 hours in
https://github.com/home-assistant/core/issues/175923#issuecomment-5102611902
and described v1 as Signature-only, with v2 supporting both models, in
https://github.com/home-assistant/core/issues/175923#issuecomment-4966456273.
The outreach now asks about the 24-versus-23-hour discrepancy and a supported
Conductor energy endpoint rather than assuming all v1 endpoints cover it.

This narrows the missing evidence: a v2 duration answer does exist, contrary to
the earlier record's implication, but conflicts with the guide and does not
settle exact boundary/clock or retained-expiry policy. Gate H remains unresolved,
as do P/E/R. No new runtime or thermostat behavior was changed. Awaiting reply.
