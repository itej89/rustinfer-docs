---
title: "ISO 8601-1:2019 requirements"
navtitle: Requirements
section: Standards
group: "Data and integrity / ISO 8601-1:2019"
order: 31
summary: The rules of the RFC 3339 profile of ISO 8601 for a UTC timestamp with milliseconds, which is all rustinfer's scope asks of ISO 8601.
---

# ISO 8601-1:2019 requirements

**ISO 8601-1:2019 is paywalled and was not obtained.** Every requirement below is
from a secondary source: **RFC 3339** (`specs/data/rfc3339.txt`, July 2002), which
§1.4 of the SRS names as the profile used and to which it limits the scope ("UTC
date-time with milliseconds in the RFC 3339 profile"). Section numbers are RFC
3339's. Nothing is said here about ISO 8601 beyond what RFC 3339 states of it.

| id | source | requirement |
|---|---|---|
| D1 | RFC 3339 §5.6 (secondary source) | `date-time = full-date "T" full-time`; `full-date = date-fullyear "-" date-month "-" date-mday`; `partial-time = time-hour ":" time-minute ":" time-second [time-secfrac]`; `time-secfrac = "." 1*DIGIT`. rustinfer's profile fixes the fraction at three digits. |
| D2 | RFC 3339 §5.6, §4.1 (secondary source) | `time-offset = "Z" / time-numoffset`; rustinfer's scope is UTC, written "Z". |
| D3 | RFC 3339 §5.6 (secondary source) | `date-fullyear = 4DIGIT`; `date-month` 01-12; `date-mday` 01-28, 29, 30 or 31 "based on month/year"; `time-hour` 00-23; `time-minute` 00-59; `time-second` 00-58, 59 or 60 "based on leap second rules". |
| D4 | RFC 3339 §5.7 (secondary source) | The day maximum per month, with February 29 in a leap year; "time-second may have the value "60" at the end of months in which a leap second occurs"; "this profile of ISO 8601 only allows values between "00" and "23" for the hour". |
| D5 | RFC 3339 §5.6 NOTE (secondary source) | "T" and "Z" may be lower case, but "Applications that generate this format SHOULD use upper case letters"; a specification "MAY further limit" them to upper case. |
| D6 | RFC 3339 §5.1 (secondary source) | When all timestamps have the same precision and offset, "the timestamps can be sorted as strings" chronologically. |
