# Vulnerability disclosure

Report a defect in this repository to the maintainer of `code4johnm/headerbidding`. Use a private GitHub security advisory on that repository if the report describes a way to read crawl data, run injected script beyond the researcher host, or fetch a win notice that the code currently only stores.

Include the commit, the command you ran, and the file you believe is wrong. Do not send contents of `datadir/`, cookies, or bid logs from real sites in the first message.

There is no bug bounty and no external coordinator. The maintainer triages the report, confirms it against the auction tests or a crawl log, and ships a patch on `master` with a `CHANGELOG` line. The auction workflow should be green on that commit before the advisory is closed.

A page that returns strange Prebid data is not, by itself, a vulnerability in this repository. The harvest trusts the page on purpose.

Out of date: this process was written for the research tree. It is not an enterprise PSIRT.
