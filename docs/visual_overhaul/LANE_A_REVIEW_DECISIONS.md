# Lane A Evidence-Backed Review Decisions

This decision layer records only statuses justified by completed technical review.
It does not promote nonblank candidates to valid_render, usable, or alternate.

## Summary

- Decisions recorded: **837**
- Reject / blank render: **673**
- Decode issue / failed image decode: **164**

## Policy

- Blank renders are rejected because they contain no visible donor art.
- Decode failures are marked decode_issue because an actual decode attempt failed.
- Decodable nonblank assets remain pending visual inspection.
- This file is an override/decision layer; it does not modify Platinum resources.
