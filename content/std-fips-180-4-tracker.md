---
title: "FIPS 180-4 tracker"
navtitle: Tracker
section: Standards
group: "Data and integrity / FIPS 180-4"
order: 13
summary: Gaps between rustinfer's SHA-256 use and FIPS 180-4; only test coverage is open.
---

# FIPS 180-4 tracker

From the [audit](std-fips-180-4-audit.html) of 2026-11-13.

| id | gap | required by | status | notes |
|---|---|---|---|---|
| SHA256-1 | The known-answer test covers only the one-block "abc" message | §5.1.1 (padding), §6.2.2 (multi-block computation) | Open | Add the empty message, NIST's two-block example (`abcdbcdecdefdefg…nopq`, 448 bits) and lengths of 55, 56, 63 and 64 bytes, where the padding moves to a second block. It would catch a dependency bump that breaks padding, which the single vector might not. No issue covers it |
