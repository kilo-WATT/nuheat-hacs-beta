# Vendor confirmation draft — not sent

Use the public v1/v2 API names below. No account names, thermostat serials,
tokens, callback URLs or private correspondence are needed. Record public links
or an authorized paraphrase of the answer with date and applicable API version.
An unanswered question is not a negative answer or a completed gate.

## H — explicit timed hold

1. Does the guide's 23-hour window apply to v2 `PUT /api/v2/Mode/Hold` with
   `holdUntil`, as well as v1 `holdSetPointDateTime`?
2. Is exactly 23 hours accepted? Is duration measured at server receipt in UTC,
   and what clock-skew tolerance, minimum lead time or rounding applies?
3. Is the limit the same for all supported thermostat models/firmware? Can
   longer holds legitimately be returned by the API?
4. Can changing the temperature retain an existing longer expiry without
   creating a new hold, and how should such a command be encoded?

## P — change notifications

1. Which SignalR protocol/version and negotiation/transport endpoints are
   supported at `/v2/notificationsHost`? Is there a current async-client example?
2. What is the supported token transport and refresh/reauthorization lifecycle?
   Can the same `openapi` authorization be used without new scopes/registration?
3. Confirm `Subscribe`, event method names, argument types, event ordering,
   duplicate delivery, resubscription and account/device filtering guarantees.
4. Which heartbeat, connection, retry and concurrent-session limits apply?

## E — energy logs

1. What timezone defines day/hour buckets, and how are missing/repeated DST
   hours and week starts represented? Are buckets complete or partial?
2. Confirm relay-on minute bounds, kWh scaling, tariff/currency fields, and
   whether zero kWh can mean an unconfigured load rather than no usage.
3. Can past buckets be corrected? What retention, update delay and reset rules
   apply, and are day/week/month reports overlapping views of the same data?
4. Which models/permissions support these endpoints, and is energy always an
   estimate calculated from configured load rather than metered consumption?

## R — relative temperature

1. Swagger describes `temperatureType` 0 = Absolute and 1 = Relative. Does
   Relative add to the current target, sensed floor temperature, air temperature
   or another reference? Is the reference selected atomically by the server?
2. Is the signed integer delta in hundredths Celsius, including negative values?
   What rounding and resulting-range validation apply?
3. Which Hold/Manual, next-schedule/explicit-expiry and Permanent Hold combinations
   are supported? Can a relative command preserve existing mode and hold expiry?
4. Does a rejected 401 guarantee that no delta was applied, and is any request
   idempotency mechanism supported for ambiguous transport failures?

## Evidence record template

Gate: H / P / E / R

Status: unanswered / partially confirmed / confirmed / contradicted

Date and API/model applicability:

Public source or authorized nonprivate paraphrase:

Confirmed boundaries and synthetic fixture expectations:

Unanswered points and runtime behavior still blocked:
