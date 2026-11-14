---
title: "FIPS 180-4 requirements"
navtitle: Requirements
section: Standards
group: "Data and integrity / FIPS 180-4"
order: 11
summary: What FIPS 180-4 requires of SHA-256: the message length bound, preprocessing, the hash computation and the form of the digest.
---

# FIPS 180-4 requirements

Source: `specs/data/fips-180-4.pdf` (NIST, *FIPS PUB 180-4, Secure Hash Standard*,
August 2015). Scope from SRS §1.4: SHA-256 only. SHA-1, SHA-224 and the SHA-512
family are out of scope.

| id | section | requirement |
|---|---|---|
| S1 | §1, Figure 1; §6.2 | "SHA-256 may be used to hash a message, M, having a length of ℓ bits, where 0 ≤ ℓ < 2^64." The block size is 512 bits, the word size 32 bits, the digest 256 bits. |
| S2 | §5.1.1 | Padding: append the bit "1", then k zero bits, "where k is the smallest, non-negative solution to the equation ℓ + 1 + k ≡ 448 mod 512", then the 64-bit length ℓ. "The length of the padded message should now be a multiple of 512 bits." |
| S3 | §5.2.1 | The padded message "is parsed into N 512-bit blocks", each "expressed as sixteen 32-bit words". |
| S4 | §5.3.3 | "For SHA-256, the initial hash value, H(0), shall consist of the following eight 32-bit words": `6a09e667 bb67ae85 3c6ef372 a54ff53a 510e527f 9b05688c 1f83d9ab 5be0cd19`. |
| S5 | §4.1.2, §4.2.2, §6.2.2 | The six functions (Ch, Maj, Σ0, Σ1, σ0, σ1), the sixty-four constants K0 to K63, and the hash computation, where "Addition (+) is performed modulo 2^32". |
| S6 | §6.2.2; §3.1 | The digest is H0(N) ‖ H1(N) ‖ … ‖ H7(N), 256 bits; "the big-endian convention is used when expressing both 32- and 64-bit words". A hex digit "is an element of the set {0, 1,…, 9, a,…, f}". |
| S7 | §6 (introduction) | "there may exist alternate computation methods that yield identical results ... Such alternate methods may be implemented in conformance to this standard." (Streaming the message in chunks is such a method only if its result is identical.) |
| S8 | Announcement, item 8 | "Only algorithm implementations that are validated by NIST will be considered as complying with this standard." |

Known-answer values: FIPS 180-4 itself gives no digest values; §A.2 points to NIST's
examples page for them. The "abc" digest used below
(`ba7816bf…f20015ad`) is the one-block example published there and in FIPS 180-2's
appendix; it is a secondary source for the expected value, not a clause of 180-4.
