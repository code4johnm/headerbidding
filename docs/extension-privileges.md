# Privileged extension call sites

The instrumentation extension is Manifest V2. Its content security policy
still contains `script-src 'self' 'unsafe-eval'`. That directive is residual
risk. It is required by `Extension/src/lib/js-instruments.ts`, which evaluates
instrumentation object paths such as `window.CanvasRenderingContext2D.prototype`.
Removing `unsafe-eval` would stop JavaScript instrumentation. Manifest V3 is
not a drop-in replacement for the experiment APIs this platform uses.

Call sites below are the privileged operations. Ordinary WebExtension APIs
(`webRequest`, cookies, tabs) are declared in `Extension/bundled/manifest.json`
and are not repeated row by row.

| Call site | API | Why it exists | Guard |
| --- | --- | --- | --- |
| `Extension/src/feature.ts` reads `browser_params.json` | `profileDirIO.readFile` | The background script needs the per-browser configuration written into the profile. | Filename must match `^[A-Za-z0-9._-]{1,128}$` and must not contain `..`. |
| `Extension/src/feature.ts` writes `OPENWPM_STARTUP_SUCCESS.txt` | `profileDirIO.writeFile` | The Python side waits on this marker before treating the browser as ready. | Same filename rule. |
| `Extension/src/loggingdb.ts` writes `extension_port.txt` | `profileDirIO.writeFile` | Publishes the extension's listening port to the profile so the platform can connect. | Same filename rule. |
| `Extension/src/feature.ts` `pre_instrumentation_code` | `eval` | Optional researcher hook before instruments start. | Runs only when `custom_params.allow_pre_instrumentation_eval === true`. Otherwise the code is refused and logged. This gate is in the TypeScript source and applies after the next extension build. |
| `Extension/src/lib/js-instruments.ts` `eval(item.object)` | `eval` | Resolves the object path for an instrumented API. This is why `unsafe-eval` remains. | No additional gate. The object path comes from the crawl configuration, which is researcher-controlled. |
| `Extension/src/callstack-instrument.ts` | `stackDump.onStackAvailable` | Records JavaScript stacks for instrumented property access. `callstack_instrument` is rejected by `validate_browser_params` because the instrument is currently non-functional. | The API only emits stacks to the extension. It does not open sockets. |
| `Extension/src/socket.ts` `SendingSocket.connect` | `sockets.connect` | Background instruments send records to the Python storage controller and logger. | `connect` accepts only `127.0.0.1`, `localhost`, or `::1`, and an integer port from 1 to 65535, before `createTransport`. |
| `Extension/bundled/privileged/sockets/api.js` `createServerSocket` | `nsIServerSocket.init(-1, true, -1)` | Loopback listener for Python-to-extension messages. The second argument already requests loopback-only. | Accepted peers with a non-empty, non-loopback `transport.host` are closed. An empty host is allowed because the listening socket is loopback. |
| `Extension/bundled/privileged/sockets/api.js` `startListening` | serialization types | Forwards messages into the extension. | Only types `j` (JSON) and `n` (raw bytes) are forwarded. Type `d` (dill) is logged and dropped. |

## What this does not contain

Python-to-Python storage records still use dill on `DataSocket` in
`openwpm/storage/storage_controller.py`. That channel is separate from the
extension listener. Dill deserialization of those records remains residual
risk on the research host.

Subresource requests, and `webdriver.get` calls made from inside a command
after the visit URL was accepted, are not filtered by the extension. Visit
URL enforcement is in `TaskManager.execute_command_sequence`.

The extension was not rebuilt with webpack in the hardening change that added
the pre-instrumentation gate. `node --check` covers the privileged `api.js`
files Firefox loads directly.
