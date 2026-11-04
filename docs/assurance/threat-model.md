# Threat model

## Assets

Bid CPM, bidder name, ad-unit code, and timing. On a crawl, also HTTP bodies, cookies, and page scripts. The fixture dataset is synthetic and labeled, but it uses the same field names, so a later mix-up with crawl logs would mislead a model.

## Actors

The researcher on the host. A publisher page and its third parties, only during a crawl. An adapter callable supplied by the researcher. GitHub as the source host.

## Flows

| Flow | Leaves the host? | Notes |
| --- | --- | --- |
| `hb.auction` bid request and response | No | Callables run in process. |
| Win notice and impression URL | No | The URL is stored. Nothing fetches it. |
| `ScriptUtils` / `HeaderBiddingCommand` | The crawl already did | The script only reads `pbjs` in the page. |
| Dashboard export | No | Computed from the three fixture profiles. |
| Profile script injection | Into the page, on a crawl | Researcher-supplied JavaScript. |

## Abuse cases

A crawl of a site the researcher does not have permission to measure. The auction module cannot do that. The crawl Job can. The dashboard still requires a human to launch it.

A page that poisons `pbjs.getBidResponses()` so the log contains false CPMs. The harvest trusts the page. Treat crawl JSON as untrusted input before it is used as training labels.

An injected script (`inject_script`, testing preset) that runs in the page. Keep it short and review it. The dashboard rejects scripts longer than 2000 characters. That is a size cap, not a sandbox.

A dependency update in `environment.yaml` that changes browser or instrumentation behavior. The auction path does not import those packages. The crawl path does.

Recording a win URL and later fetching it would notify a bidder. This code does not fetch it. A future change that does should be explicit and off by default.

## Out of scope

This document does not model a production ad server, a real exchange, or payment to a publisher.
