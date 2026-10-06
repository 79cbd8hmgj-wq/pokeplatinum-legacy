# Lane A Evidence-Backed Review Decisions

This decision layer records only statuses justified by completed technical review.
It does not promote nonblank candidates to valid_render, usable, or alternate.

## Summary

- Decisions recorded: **340**
- Reject / blank render: **150**
- Decode issue (image decode failure or Ranger reconstruction limitation): **190**

## Policy

- Blank renders are rejected because they contain no visible donor art, unless the
  Ranger cell references tiles missing from its own group (renderer limitation):
  those are decode_issue / ranger_reconstruction_issue, never reject.
- Decode failures are marked decode_issue because an actual decode attempt failed.
- Decodable nonblank assets remain pending visual inspection.
- This file is an override/decision layer; it does not modify Platinum resources.
