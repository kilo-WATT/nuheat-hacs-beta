# Vendor request — posted on GitHub

Posted to @PatrickHendrickx on 2026-10-24 at the user's explicit request:
https://github.com/home-assistant/core/issues/175923#issuecomment-6380330250

The posted version incorporates his earlier 24-hour v2 answer and asks how it
relates to the guide's 23 hours. It also asks about Conductor energy support,
given his earlier explanation of v1's Signature-only coverage. The original
draft below is retained as preparation history; the linked comment is the
authoritative sent text. No email was sent.

Subject: NuHeat OpenAPI v2 clarification for Home Assistant integration

Hello,

We maintain a NuHeat Home Assistant integration and would like to confirm four
API contracts before adding optional features. This request contains no customer
account information, credentials or thermostat identifiers.

1. **Explicit hold duration:** Does the guide's 23-hour limit apply to v2
   `Mode/Hold.holdUntil`? Is exactly 23 hours accepted, measured in UTC from
   server receipt? Can a temperature change retain an existing longer hold,
   or must that command be rejected?
2. **Change notifications:** For `/v2/notificationsHost`, please confirm the
   SignalR protocol/version, negotiation endpoint, supported token transport
   and renewal, and current `Subscribe`/`Notify` argument format. Is there a
   supported reference client and guidance for reconnect/session limits?
3. **Energy logs:** Which timezone defines hourly/day buckets and DST repeats?
   Can prior buckets be corrected? Can zero estimated kWh mean an unconfigured
   load, and how can it be distinguished from genuine zero consumption? We
   intend to label consumption as estimated and avoid overlapping totals.
4. **Relative adjustments:** Swagger defines `temperatureType` 1 as Relative.
   Does it add to the current target setpoint or a sensed temperature? Is the
   signed delta in hundredths Celsius? Which mode/hold-expiry combinations can
   be preserved, and does a rejected 401 guarantee the delta was not applied?

A link to current documentation or confirmation of these points would help us
keep existing thermostats, holds and automations working correctly.

Thank you.

## Sending status

GitHub posting is complete and verified. Awaiting a reply; posting is not
confirmation of the API contracts. The longer [question inventory](vendor-questions.md)
supplies follow-up details if needed. No private logs, tokens, callback URLs or
live device data were attached.
