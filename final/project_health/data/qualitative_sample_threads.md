# Qualitative sample threads

## PRS

### PR-01 #993 | Frequent / Core | Phase I (Jun–Dec '25) | merged
https://github.com/google-gemini/gemini-cli/pull/993 | author `scidomino` (COLLABORATOR) | created 2025-06-12 | closed 2025-06-13 | TTFR 1.0h | labels size/m
+122/-80 LOC, 9 files, linked issues 0, merged by scidomino
**Title:** Code Assist cleanup and docs
**Body:** Renames CCPA->CodeAssist everywhere in the code.
Introduces the CODE_ASSIST_ENDPOINT env var for testing.
Updates README to describe how to enable Code Assist mode.


### PR-02 #13638 | Frequent / Core | Phase I (Jun–Dec '25) | merged
https://github.com/google-gemini/gemini-cli/pull/13638 | author `kevin-ramdass` (CONTRIBUTOR) | created 2025-11-22 | closed 2025-12-01 | TTFR 21.4h | labels size/l
+591/-1 LOC, 10 files, linked issues 1, merged by kevin-ramdass
**Title:** feat: Add startup profiler to measure and record application initialization phases.
**Body:** Summary
Adds startup metrics to telemetry.
Details
Related Issues
Fixes #11485
How to Validate

Enable local telemetry and view startup metrics.
npm start -- --debug to view startup metrics.

Pre-Merge Checklist

 Updated relevant documentation and README (if needed)
 Added/updated tests (if needed)
 Noted breaking changes (if any)
 Validated on required platforms/methods:

 MacOS

 npm run
 npx
 


### PR-03 #4766 | Frequent / Core | Phase I (Jun–Dec '25) | merged
https://github.com/google-gemini/gemini-cli/pull/4766 | author `scidomino` (COLLABORATOR) | created 2025-07-24 | closed 2025-07-25 | TTFR 36.3h | labels size/xl
+965/-1873 LOC, 3 files, linked issues 0, merged by scidomino
**Title:** Make useCompletion.test.ts windows compatible
**Body:** TLDR
Modify useCompletion to have consistent output in windows (with and without glob). Fix tests to be windows compatible.
Dive Deeper
We previously had two tests for this file but there was no reason to so I combined them.
Reviewer Test Plan
I tested these on unix, macos, and windows.
Testing Matrix




🍏
🪟
🐧




npm run
x
x
x


npx
❓
❓
❓


Docker
❓
❓
❓


Podman
❓
-
-


Seatbelt
❓
-
-



Linked 


### PR-04 #7535 | Frequent / Core | Phase I (Jun–Dec '25) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/7535 | author `JayadityaGit` (CONTRIBUTOR) | created 2025-09-01 | closed 2025-09-03 | TTFR none | labels size/xs
+6/-1 LOC, 1 files, linked issues 1, merged by None
**Title:** Fix: ctrl+c tip fix
**Body:** TLDR
This PR refines the behavior of the ctrl+c tip and stream cancellation flow.
Previously, pressing ctrl+c to cancel a stream would always show the tip “Press ctrl+c again to exit”, even though the second ctrl+c only cleared the input. This caused confusion and inconsistency.
Now, the tip and behavior are aligned:

The first ctrl+c cancels the stream and restores the previous prompt.
While the 

- `JayadityaGit` (2025-09-01): After applying the fix from gemini-bot, the flow is now:  When the user presses ctrl+c to cancel a stream, the previous prompt is restored in the input field. (default) At the same time, the tip “Press ctrl+c again to exit” is briefly shown. (default) If the user presses ctrl+c again within the timeframe of tip is shown, the application exits. (new behavior / my change) If no second ctrl+c is pressed in that window, the tip disappears. (default) From there:  The prompt remains in the input field, allowing the user to edit or submit it, or The user can press ctrl+c again later to clear the inpu
- `JayadityaGit` (2025-09-03): Now it seems to be fixed !

### PR-05 #8608 | Frequent / Core | Phase I (Jun–Dec '25) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/8608 | author `mattKorwel` (COLLABORATOR) | created 2025-09-17 | closed 2025-09-17 | TTFR none | labels size/l
+317/-185 LOC, 7 files, linked issues 0, merged by None
**Title:** Mk/promote correct preview
**Body:** 


### PR-06 #4563 | Frequent / Core | Phase I (Jun–Dec '25) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/4563 | author `rmedranollamas` (CONTRIBUTOR) | created 2025-07-20 | closed 2025-07-20 | TTFR none | labels priority/p1, area/core, size/xl
+6978/-32788 LOC, 308 files, linked issues 1, merged by None
**Title:** feat: Add /mcp refresh slash command
**Body:** NOTE: this is a re-implementation of #3529 on the new slash command architecture. is functionally equal (it was easier than resolving that huge merge conflict).
Adds a new slash command /mcp refresh to allow users to reload MCP servers without restarting the Gemini CLI.
This change includes:

A new refeshMcpServers method in the Config class to refresh the tool registry.
A new refreshMcpAction fun


### PR-07 #24027 | Frequent / Core | Phase II (Jan–Apr '26) | merged
https://github.com/google-gemini/gemini-cli/pull/24027 | author `scidomino` (COLLABORATOR) | created 2026-03-27 | closed 2026-03-27 | TTFR 1.3h | labels size/m, status/need-issue
+175/-22 LOC, 5 files, linked issues 0, merged by scidomino
**Title:** feat(core): implement windows sandbox expansion and denial detection
**Body:** Summary
Implement Windows Dynamic Sandbox Expansion (Reactive Heuristic Permission Model).
This PR introduces the ability for the Windows sandbox to reactively detect and report access denials, enabling the agent to request dynamic permission expansions for the file system and network.
Details

Windows Denial Detection: Implemented parseWindowsSandboxDenials in packages/core to identify Windows-sp

- `galdawave` (2026-03-27): Code Review Scope: Pull Request #24027 This PR introduces a robust heuristic model for detecting Windows-specific sandbox denials from shell execution output. It correctly extracts absolute paths (including extended and quoted paths) and enables WindowsSandboxManager as the default on Windows. The test coverage is solid for the logic provided. Metadata Review The PR Title (feat(core): implement windows sandbox expansion and denial detection) strictly adheres to the Conventional Commits specification. The PR Description is well-structured and explains the intent clearly. Nits (Minor Improvement

### PR-08 #23639 | Frequent / Core | Phase II (Jan–Apr '26) | merged
https://github.com/google-gemini/gemini-cli/pull/23639 | author `adamfweidman` (COLLABORATOR) | created 2026-03-24 | closed 2026-03-24 | TTFR 9.3h | labels size/s, status/need-issue
+17/-17 LOC, 3 files, linked issues 0, merged by adamfweidman
**Title:** feat(core): change user-facing auth type from oauth2 to oauth
**Body:** Summary
This PR changes the user-facing authentication type from oauth2 to oauth in the agent configuration to correctly align with the underlying scheme schema. The internal implementation continues to use oauth2 for compatibility.
Details

Updated FrontmatterAuthConfig to expect oauth instead of oauth2.
Updated oauth2AuthSchema to use z.literal('oauth').
Modified convertFrontmatterAuthToConfig t


### PR-09 #21485 | Frequent / Core | Phase II (Jan–Apr '26) | merged
https://github.com/google-gemini/gemini-cli/pull/21485 | author `gundermanc` (MEMBER) | created 2026-03-06 | closed 2026-03-07 | TTFR 0.2h | labels size/m
+51/-7 LOC, 18 files, linked issues 1, merged by gundermanc
**Title:** Disallow underspecified types
**Body:** Summary
Adds a new eslint rule that disallows syntax like the following outside of tests.
typeof myObject['myProperty'] == 'string'
Why
This syntax is almost exclusively used in the codebase as a form of inline type assertion for unpacking properties on an object of unknown or Record<string, unknown> type.
I believe that typeof expression == 'string' is a reasonable type assertion, but using this 


### PR-10 #25352 | Frequent / Core | Phase II (Jan–Apr '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/25352 | author `mini2s` (CONTRIBUTOR) | created 2026-04-14 | closed 2026-05-04 | TTFR 148.3h | labels size/xl, status/need-issue
+1177/-107 LOC, 24 files, linked issues 0, merged by None
**Title:** fix(cli): Massive logs cause scrolling lag and inefficient positioning
**Body:** Summary
Add search and level-based filtering to the debug console so users can narrow console output faster when troubleshooting. This improves both the CLI debug console experience and the devtools client by making high-volume logs easier to inspect.  @cocosheng-g

  
    
    

    2026-04-13.16-58-32.webm
    
  

  

  



  
    
    

    2026-04-13.16-05-36.webm
    
  

  

  


Details

A

- `mini2s` (2026-05-01): Codereview issue has been resolved    @gemini-code-assist

### PR-11 #23630 | Frequent / Core | Phase II (Jan–Apr '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/23630 | author `NTaylorMullen` (COLLABORATOR) | created 2026-03-24 | closed 2026-08-17 | TTFR 17.0h | labels Stale, size/xl, status/need-issue
+1295/-84 LOC, 18 files, linked issues 0, merged by None
**Title:** feat(cli): support Open Plugins MCP servers
**Body:** Summary
Implement support for the Open Plugins MCP Servers specification in Gemini CLI. This allows Open Plugins (plugin.json) to define one or more MCP servers that are automatically discovered and configured when the plugin is loaded.
Details

Manifest Support: Implemented discovery of .mcp.json at the plugin root and support for mcpServers (as a path string, array of paths, or direct record) in


### PR-12 #18179 | Frequent / Core | Phase II (Jan–Apr '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/18179 | author `gundermanc` (MEMBER) | created 2026-02-03 | closed 2026-02-04 | TTFR none | labels priority/p1, size/m
+91/-31 LOC, 9 files, linked issues 0, merged by None
**Title:** Gundermanc/subagent eval
**Body:** Summary

Details

Related Issues

How to Validate

Pre-Merge Checklist


 Updated relevant documentation and README (if needed)
 Added/updated tests (if needed)
 Noted breaking changes (if any)
 Validated on required platforms/methods:

 MacOS

 npm run
 npx
 Docker
 Podman
 Seatbelt


 Windows

 npm run
 npx
 Docker


 Linux

 npm run
 npx
 Docker


### PR-13 #29502 | Frequent / Core | Phase III (May–Sep '26) | merged
https://github.com/google-gemini/gemini-cli/pull/29502 | author `ugorla-dev` (CONTRIBUTOR) | created 2026-09-25 | closed 2026-10-02 | TTFR 164.9h | labels priority/p1, area/core, size/m
+193/-24 LOC, 13 files, linked issues 1, merged by DavidAPierce
**Title:** fix(cli): ensure Enter and Spacebar reliably confirm selection list options
**Body:** Summary
Ensure interactive selection lists (useSelectionList, RadioButtonSelect, ToolConfirmationMessage, and AskUserDialog) reliably confirm options with Enter and Spacebar across terminals (including Windows IDE terminals without Kitty Keyboard Protocol), while preventing InputPrompt from preempting confirmation keystrokes when an interactive prompt or dialog is active.
Details
On terminals wher


### PR-14 #26661 | Frequent / Core | Phase III (May–Sep '26) | merged
https://github.com/google-gemini/gemini-cli/pull/26661 | author `adamfweidman` (COLLABORATOR) | created 2026-05-07 | closed 2026-05-08 | TTFR 22.1h | labels size/s, status/need-issue
+15/-1 LOC, 4 files, linked issues 0, merged by adamfweidman
**Title:** refactor(core): agent session protocol changes
**Body:** Summary
Apply 6 lines of refinements to legacy-agent-session.ts and content-utils.ts (cleanup in finally, stack trace in error meta, and warning on fallback). Added tests to verify the stack trace and warning log. This PR isolates these specific changes to keep the diff footprint minimal.
Details
This PR includes:

legacy-agent-session.ts: Moved _clearActiveStream() to a finally block for robust c


### PR-15 #28712 | Frequent / Core | Phase III (May–Sep '26) | merged
https://github.com/google-gemini/gemini-cli/pull/28712 | author `DavidAPierce` (CONTRIBUTOR) | created 2026-08-06 | closed 2026-08-06 | TTFR 0.1h | labels 
+19/-19 LOC, 9 files, linked issues 0, merged by DavidAPierce
**Title:** chore: bump version to 0.54.2
**Body:** Summary
This PR bumps the package versions across all workspace packages in the monorepo to 0.54.2 via the release versioning script.
Details
All package.json files and package-lock.json are updated to version 0.54.2 to prepare for the v0.54.2 release.
Related Issues
None.
How to Validate

Inspect modified package.json files and package-lock.json to ensure they point to 0.54.2.
Confirm that worksp


### PR-16 #28968 | Frequent / Core | Phase III (May–Sep '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/28968 | author `aniruddhaadak80` (CONTRIBUTOR) | created 2026-08-22 | closed 2026-09-06 | TTFR none | labels priority/p3, area/extensions, size/m, status/pr-nudge-sent
+158/-4 LOC, 2 files, linked issues 1, merged by None
**Title:** fix(core): dedupe symlinked/junctioned skills directories during discovery
**Body:** Summary
Fixes #28944
When a user links their .gemini folder to .agents (Windows junction via \mklink /J .gemini .agents, or a symlink) to follow the open Agent Skills standard while retaining compatibility, the CLI scanned both configured entry points (.gemini/skills and .agents/skills) as if they were separate directories. Since discovery did not resolve aliases to their physical paths, identical


### PR-17 #28842 | Frequent / Core | Phase III (May–Sep '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/28842 | author `Xsidz` (NONE) | created 2026-08-16 | closed 2026-08-16 | TTFR none | labels size/s
+31/-9 LOC, 2 files, linked issues 1, merged by None
**Title:** fix(a2a-server): deep-merge nested settings to prevent user config loss
**Body:** Summary

A2A server combined user and workspace settings with a shallow spread, so a workspace fileFiltering: { respectGitIgnore: false } would erase the user's enableRecursiveFileSearch: true entirely.
Replaced the spread with an inline one-level deep merge: for each key in workspace settings, if both sides are plain objects the key is merged; otherwise workspace value wins. Arrays and scalars ar


### PR-18 #28873 | Frequent / Core | Phase III (May–Sep '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/28873 | author `joneba` (CONTRIBUTOR) | created 2026-08-18 | closed 2026-08-18 | TTFR 15.1h | labels priority/p1, area/security, size/s
+31/-0 LOC, 2 files, linked issues 1, merged by None
**Title:** [SSR Agent] Issue Fix (28512): Prevent unhandled promise rejection on OAuth callback timeout
**Body:** fixes #28512
Original Issue URL: #28512
Context & Problem
An unhandled promise rejection occurred during the authentication flow when the OAuth callback server timed out after 5 minutes, as the rejection of the callback server's promise was not caught or handled if the authenticated state was abandoned.
Detailed Changes

packages/core/src/utils/oauth-flow.ts:

Attached a no-op .catch(() => {}) han


### PR-19 #1048 | Episodic Community | Phase I (Jun–Dec '25) | merged
https://github.com/google-gemini/gemini-cli/pull/1048 | author `scottdensmore` (CONTRIBUTOR) | created 2025-06-14 | closed 2025-06-14 | TTFR 0.4h | labels size/s
+20/-0 LOC, 1 files, linked issues 0, merged by scottdensmore
**Title:** docs: document environment variables for cloud services
**Body:** Adds documentation for new environment variables required for configuring and using Google Cloud services like Vertex AI and Code Assist.
The following variables are now documented:

GOOGLE_API_KEY
GOOGLE_CLOUD_PROJECT
GOOGLE_CLOUD_LOCATION
GEMINI_CODE_ASSIST


### PR-20 #14473 | Episodic Community | Phase I (Jun–Dec '25) | merged
https://github.com/google-gemini/gemini-cli/pull/14473 | author `jb-perez` (CONTRIBUTOR) | created 2025-12-03 | closed 2025-12-12 | TTFR 213.6h | labels size/xs
+2/-0 LOC, 2 files, linked issues 0, merged by scidomino
**Title:** Add license field into package.json
**Body:** Add the license field in the package.json to reflect the project license.
Summary
Add the license information into the package.json to reflect the project license.
Details
License field is used by different systems to quickly identify the project license.
How to Validate
Verify license property is present.
Pre-Merge Checklist


 Updated relevant documentation and README (if needed)
 Added/updated 


### PR-21 #15357 | Episodic Community | Phase I (Jun–Dec '25) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/15357 | author `ra1nyxin` (NONE) | created 2025-12-20 | closed 2026-01-24 | TTFR 624.0h | labels size/s, status/need-issue
+5/-5 LOC, 1 files, linked issues 0, merged by None
**Title:** Clarify locations of system defaults file
**Body:** Reorganize system defaults file locations for clarity.
Summary
This PR improves the readability of the "System defaults file" section in the README. By breaking down the paths for different operating systems into a structured list, users can more easily identify the correct location for their environment.
Details

Converted a dense paragraph of system paths into a nested list format.
Grouped paths

- `bdmorgan` (2026-01-15): Hi @ra1nyxin, thank you so much for your contribution to Gemini CLI! We really appreciate the time and effort you've put into this. We're making some updates to our contribution process to improve how we track and review changes. Please take a moment to review our recent discussion post: Improving Our Contribution Process & Introducing New Guidelines. Key Update: Starting January 26, 2026, the Gemini CLI project will require all pull requests to be associated with an existing issue. Any pull requests not linked to an issue by that date will be automatically closed. Thank you for your understan

### PR-22 #15548 | Episodic Community | Phase I (Jun–Dec '25) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/15548 | author `facelezzzz` (NONE) | created 2025-12-25 | closed 2026-01-24 | TTFR 499.4h | labels priority/p3, area/core, size/m
+60/-4 LOC, 4 files, linked issues 0, merged by None
**Title:** feat:Add ~/.gemini/system.md fallback for GEMINI_SYSTEM_MD=1|true
**Body:** Summary
This PR allows setting GEMINI_SYSTEM_MD=1 or true so that when .gemini/system.md does not exist in the project root, the system will fall back to $HOME/.gemini/system.md.
Details
Although GEMINI_SYSTEM_MD can be used to specify an explicit path, once a path is set, .gemini/system.md inside certain repositories will no longer take effect, which is inconvenient for our team.
What we want ins

- `bdmorgan` (2026-01-15): Hi @facelezzzz, thank you so much for your contribution to Gemini CLI! We really appreciate the time and effort you've put into this. We're making some updates to our contribution process to improve how we track and review changes. Please take a moment to review our recent discussion post: Improving Our Contribution Process & Introducing New Guidelines. Key Update: Starting January 26, 2026, the Gemini CLI project will require all pull requests to be associated with an existing issue. Any pull requests not linked to an issue by that date will be automatically closed. Thank you for your underst
- `facelezzzz` (2026-01-16): Yes, this PR addresses issue #15549. Please let me know if any changes are needed.

### PR-23 #1304 | Episodic Community | Phase I (Jun–Dec '25) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/1304 | author `bdmorgan` (COLLABORATOR) | created 2025-06-22 | closed 2025-06-22 | TTFR none | labels size/xl
+3054/-1103 LOC, 82 files, linked issues 0, merged by None
**Title:** Updated docs and /stats command to support lack of token caching support for OAuth users (b/426943001)
**Body:** ok so i think the only solution to this is to add in explicit caching support to CCPA APIs, which probably is also going to require some changes on the Titan implementation side of things as well. This is a fairly heavyweight change that I can work with the Services team to track, but the full implementation is not going to be in place in the next 48 hours.
I think the best option is just to be up


### PR-24 #18639 | Episodic Community | Phase II (Jan–Apr '26) | merged
https://github.com/google-gemini/gemini-cli/pull/18639 | author `aswinashok44` (CONTRIBUTOR) | created 2026-02-09 | closed 2026-02-09 | TTFR 1.3h | labels size/m, status/need-issue
+46/-8 LOC, 5 files, linked issues 0, merged by galdawave
**Title:** fix(chore): Support linting for cjs
**Body:** Summary
Enable linting for cjs files throughout the project
Details
Currently cjs files are ignored from linting or manual overrides are done, as part of gemini cli standalone binary feature a new cjs file will be added as the entry point for Node SEA binary, so going forward it would be better to have linting for cjs across the project.
Pre-Merge Checklist


 Updated relevant documentation and RE


### PR-25 #16965 | Episodic Community | Phase II (Jan–Apr '26) | merged
https://github.com/google-gemini/gemini-cli/pull/16965 | author `yuvrajangadsingh` (CONTRIBUTOR) | created 2026-01-18 | closed 2026-02-26 | TTFR 3.9h | labels priority/p2, area/platform, size/m, help wanted
+234/-6 LOC, 4 files, linked issues 2, merged by scidomino
**Title:** fix: prevent orphaned processes from consuming 100% CPU when terminal closes
**Body:** Summary
This PR fixes issues #15874 and #15873 where closing the terminal window causes orphaned Gemini CLI processes to spin at 100% CPU, making the system unresponsive.
Root Cause
When a terminal is closed, the shell sends SIGHUP to child processes. Without proper signal handling, the CLI process continues running but loses its controlling terminal, causing it to spin in a tight loop trying to r

- `yuvrajangadsingh` (2026-01-18): Thanks for catching this race condition! Fixed in commit 3c29341 by adding the isShuttingDown check and setting it to true before calling runExitCleanup() in the TTY check block. // Prevent race condition with signal handlers if (isShuttingDown) {   return; } isShuttingDown = true; Ready for another review!
- `yuvrajangadsingh` (2026-01-18): @gemini-code-assist Added the test case for TTY loss scenario in d358abb. Thanks for the suggestion!
- `yuvrajangadsingh` (2026-02-06): @gemini-code-assist review
- `yuvrajangadsingh` (2026-02-06): @gemini-code-assist review
- `yuvrajangadsingh` (2026-02-06): Hi @NTaylorMullen, this PR has been open for a few weeks now and all review feedback has been addressed. Would you or another maintainer be able to take a look when you get a chance? Thanks!
- `yuvrajangadsingh` (2026-02-17): Hey folks, just bumping this one again — it's been open for a while now and all review feedback has been addressed. Would really appreciate a look when someone has time. Thanks!
- `yuvrajangadsingh` (2026-02-20): Hey @Adib234 — would you be able to take a look at this one when you get a chance? It fixes orphaned child processes that spike to 100% CPU when the terminal closes. Has a community approval already and all checks pass. Thanks!
- `yuvrajangadsingh` (2026-02-25): moved setupSignalHandlers, setupTtyCheck, gracefulShutdown, and isShuttingDown into utils/cleanup.ts. tests updated to import from there too. gemini.tsx just calls the functions now — all the shutdown logic lives in cleanup.ts.

### PR-26 #24231 | Episodic Community | Phase II (Jan–Apr '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/24231 | author `holtskinner` (CONTRIBUTOR) | created 2026-03-30 | closed 2026-04-14 | TTFR none | labels size/m, status/need-issue
+57/-55 LOC, 5 files, linked issues 0, merged by None
**Title:** docs: Fix formatting of "code-like text" to use monospace
**Body:** 


### PR-27 #24473 | Episodic Community | Phase II (Jan–Apr '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/24473 | author `soisyourface` (NONE) | created 2026-04-01 | closed 2026-04-16 | TTFR none | labels priority/p2, area/core, size/m
+90/-16 LOC, 6 files, linked issues 1, merged by None
**Title:** feat(cli): add ignoreLocalDotEnv setting to isolate from project .env files
**Body:** Description
This PR introduces a new setting advanced.ignoreLocalDotEnv (defaulting to false) that allows users to explicitly opt-out of project-specific .env file loading.
When enabled, the CLI bypasses the search for .env and .gemini/.env files in the current workspace and parent directories, and instead falls back directly to the global configuration in ~/.gemini/.env.
Motivation
As discussed i


### PR-28 #24080 | Episodic Community | Phase II (Jan–Apr '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/24080 | author `gvenugo3` (NONE) | created 2026-03-28 | closed 2026-05-07 | TTFR 193.4h | labels priority/p2, area/core, size/l, help wanted
+679/-2 LOC, 7 files, linked issues 1, merged by None
**Title:** feat(cli): add gemini update command
**Body:** Summary
Implement a new gemini update command that checks for and installs newer versions of the CLI while preserving the current release channel (stable, preview, or nightly).
Features

Check for updates - Queries npm registry for latest version
Preserve release channel - Maintains current channel (stable/preview/nightly) during update
Multi-package manager support - Works with npm, yarn, pnpm, b

- `SHARABUMANOJKUMAR` (2026-04-05): Hi, I would like to work on this issue. I’m a GSoC 2026 applicant and have experience with Python and  Node.js and CLI tools. I’d love to contribute to this feature. Could you please guide me on how to proceed? Thanks!
- `gvenugo3` (2026-04-22): @mrpmohiburrahman made the changes you pointed out! Please let me know if everything looks good.
- `gvenugo3` (2026-04-22): @Adib234 please let me know if this implementation looks good.
- `spencer426` (2026-05-07): Thank you for your interest in contributing to the project! We are closing this PR due to inactivity.

### PR-29 #29252 | Episodic Community | Phase III (May–Sep '26) | merged
https://github.com/google-gemini/gemini-cli/pull/29252 | author `SandyTao520` (CONTRIBUTOR) | created 2026-09-08 | closed 2026-09-08 | TTFR 0.6h | labels priority/p1, area/agent, size/m
+54/-6 LOC, 3 files, linked issues 1, merged by SandyTao520
**Title:** fix(core): preserve explicit versioned Flash model IDs
**Body:** Summary
Preserve explicit versioned Flash model IDs instead of silently remapping them to the Gemini 3.5 Flash rollout default. This keeps --model pinning accurate and lets the API return an honest error for invalid model IDs.
Details

Limit Gemini 3.5 Flash rollout remapping to known aliases and backend model IDs.
Pass explicit versioned Flash IDs, such as gemini-3.8-flash, through unchanged.
Add


### PR-30 #28681 | Episodic Community | Phase III (May–Sep '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/28681 | author `shivajid` (NONE) | created 2026-08-04 | closed 2026-08-19 | TTFR none | labels priority/p1, size/l, size/xl, status/pr-nudge-sent
+1329/-7 LOC, 10 files, linked issues 0, merged by None
**Title:** feat(core,cli): add support for SGLang and local OpenAI-compatible en…
**Body:** …dpoints
Summary

Details

Related Issues

How to Validate

Pre-Merge Checklist


 Updated relevant documentation and README (if needed)
 Added/updated tests (if needed)
 Noted breaking changes (if any)
 Validated on required platforms/methods:

 MacOS

 npm run
 npx
 Docker
 Podman
 Seatbelt


 Windows

 npm run
 npx
 Docker


 Linux

 npm run
 npx
 Docker


### PR-31 #29286 | Episodic Community | Phase III (May–Sep '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/29286 | author `smrupchusakdi859-hash` (NONE) | created 2026-09-11 | closed 2026-09-26 | TTFR none | labels priority/p1, size/m, status/pr-nudge-sent
+70/-0 LOC, 1 files, linked issues 0, merged by None
**Title:** Implement Google search tool in RobustAutonomousAgent
**Body:** Summary

Details

Related Issues

How to Validate

Pre-Merge Checklist


 Updated relevant documentation and README (if needed)
 Added/updated tests (if needed)
 Noted breaking changes (if any)
 Validated on required platforms/methods:

 MacOS

 npm run
 npx
 Docker
 Podman
 Seatbelt


 Windows

 npm run
 npx
 Docker


 Linux

 npm run
 npx
 Docker


### PR-32 #27915 | Episodic Community | Phase III (May–Sep '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/27915 | author `magudeshhmw` (NONE) | created 2026-06-14 | closed 2026-06-29 | TTFR 0.8h | labels priority/p1, area/security, size/m, status/pr-nudge-sent
+119/-13 LOC, 4 files, linked issues 1, merged by None
**Title:** fix(core): trust dialog discloses the hook shape that never runs (#27901)
**Body:** What breaks
The workspace-trust dialog shows the inverse of the hooks that actually run. A project can ship a SessionStart hook in the canonical nested shape; it executes arbitrary shell on a single Trust folder click while the dialog never displays the command. Closes #27901.
Root cause
The disclosure parser and the execution engine read two mutually exclusive hook shapes:

Disclosure — FolderTru

- `acoderacom` (2026-06-14): Thanks for validating my findings!
- `magudeshhmw` (2026-06-22): Hi maintainers, This PR fixes issue #27901 where the workspace trust dialog displays a hook shape that differs from the hook shape actually executed. The change is limited to aligning the disclosure logic with the execution path and does not modify hook execution behavior. Please let me know if any changes are required. Thank you for your time and review.

### PR-33 #15560 | Newcomer (≤ 3 Actions) | Phase I (Jun–Dec '25) | merged
https://github.com/google-gemini/gemini-cli/pull/15560 | author `Mapleeeeeeeeeee` (CONTRIBUTOR) | created 2025-12-25 | closed 2025-12-26 | TTFR 1.3h | labels size/s
+24/-0 LOC, 4 files, linked issues 1, merged by NTaylorMullen
**Title:** fix(cli): add enableShellOutputEfficiency to settings schema
**Body:** What
Add enableShellOutputEfficiency setting to the settings schema so users can configure it via settings file.
Why
Fixes #12546
The enableShellOutputEfficiency option was introduced in PR #10651 but was not added to the settings schema. This means users cannot configure this setting through their settings file - it can only be controlled programmatically.
How

Added enableShellOutputEfficiency b

- `Mapleeeeeeeeeee` (2025-12-26): Pushed CI fixes. Could you please approve the workflow run? Thank you!
- `NTaylorMullen` (2025-12-26): Thank you for the contribution @Mapleeeeeeeeeee !

### PR-34 #5090 | Newcomer (≤ 3 Actions) | Phase I (Jun–Dec '25) | merged
https://github.com/google-gemini/gemini-cli/pull/5090 | author `Pranith124` (CONTRIBUTOR) | created 2025-07-29 | closed 2025-08-01 | TTFR 17.8h | labels size/m
+116/-109 LOC, 4 files, linked issues 1, merged by jacob314
**Title:** fix(config): Resolve duplicate config loading from home directory
**Body:** TLDR
Fixes a bug where config files were loaded twice when running the CLI from the home directory by adding checks in both the CLI and core packages to prevent duplicate loading.

Dive Deeper
Corrects a bug where running the CLI from the user's home directory would cause settings.json and GEMINI.md to be loaded twice, once for the user scope and once for the workspace scope.
This was happening be

- `allenhutchison` (2025-07-29): This is a great fix for an important bug. The approach of checking if the current directory is the home directory is definitely the right way to go. I have a few suggestions to make this PR even more robust. 1. Fix Linting Issues It looks like the Lint check is failing in the CI. Please run npm run preflight locally and commit the changes to fix the linting errors. 2. Use Real Path Resolution for Comparison The current implementation uses direct string comparison for the directory paths. This can be unreliable across different operating systems or when symbolic links are involved. For example,
- `Pranith124` (2025-07-30): Hi @allenhutchison, Thank you so much for the detailed and helpful feedback! I've made all the suggested changes.  1. Linting Issues: I ran npm run preflight and fixed the linting error. The checks are all passing now. 2. Real Path Resolution: I've updated the logic in both settings.ts and config.ts to use fs.realpathSync for a more robust path comparison, just as you suggested. 3. Test Fixes: The changes caused some of the existing tests in settings.test.ts to fail, so I've updated the test mocks to account for the new logic.  The full test suite is passing locally now. I believe this address
- `allenhutchison` (2025-07-30): This is a great fix! Using realpathSync to resolve symlinks is the correct way to prevent settings from being loaded multiple times. I've filed a separate issue (#5227) to address the unrelated snapshot test failure. Once that is resolved, this PR will be ready to merge. Thank you for the excellent contribution!
- `Pranith124` (2025-07-31): Thank you @allenhutchison for your valuable feedback and guidance. I'm a beginner in open source contribution and eager to gain experience. I would really appreciate it if you could assign me an issue to work on. Thank you once again!
- `jacob314` (2025-07-31): Thank you @allenhutchison for your valuable feedback and guidance. I'm a beginner in open source contribution and eager to gain experience. I would really appreciate it if you could assign me an issue to work on. Thank you once again!  Thank you so much for your contribution! This was a nice issue to fix. If you would like to work on other similar issues, here a lists of high priority but approachable issues we are hoping to fix over the next couple months. UX Robustness: #4245 UX Polish: #4251 I'm still finishing categorizing all the Core issues but here is the overall issue that I will be ad
- `Pranith124` (2025-07-31): Thank you @jacob314! I’ll definitely go through it and try to resolve the issues.

### PR-35 #6432 | Newcomer (≤ 3 Actions) | Phase I (Jun–Dec '25) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/6432 | author `mohab-kamle` (NONE) | created 2025-08-17 | closed 2025-08-18 | TTFR 26.0h | labels size/s
+10/-2 LOC, 2 files, linked issues 1, merged by None
**Title:** feat: improve InputPrompt component functionality
**Body:** TLDR
Fixes a bug where the input box vanishes while the model is generating a response.
Now, the input box remains visible and active, allowing users to type concurrently.
This improves workflow by removing the strict stop-and-wait interaction.
Dive Deeper
Previously, the input component was being unmounted during response generation.
This PR ensures that the input remains rendered at all times an

- `abhipatel12` (2025-08-18): Hey thanks for the contribution. A PR fixing this is already being reviewed at #6049

### PR-36 #2473 | Newcomer (≤ 3 Actions) | Phase I (Jun–Dec '25) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/2473 | author `Mautrak` (NONE) | created 2025-06-28 | closed 2025-06-28 | TTFR none | labels size/s
+32/-1 LOC, 3 files, linked issues 0, merged by None
**Title:** feat: enable --force-model by default
**Body:** TLDR

Dive Deeper

Reviewer Test Plan

Testing Matrix





🍏
🪟
🐧




npm run
❓
❓
❓


npx
❓
❓
❓


Docker
❓
❓
❓


Podman
❓
-
-


Seatbelt
❓
-
-



Linked issues / bugs


### PR-37 #2614 | Newcomer (≤ 3 Actions) | Phase I (Jun–Dec '25) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/2614 | author `tolysz` (NONE) | created 2025-06-29 | closed 2025-08-11 | TTFR 793.5h | labels size/l
+476/-29 LOC, 2 files, linked issues 0, merged by None
**Title:** Add dynamic fences in markdown code blocks.
**Body:** TLDR
Add dynamic fences in markdown code blocks. The standard ```  might not be enough for all the cases.
Dive Deeper
Markdown does not have notion of escaping inside the codeblock, it allows however to have dynamic code boundaries, number of ~ and backticks ` (I use 3+ to match the MarkdownDisplay.tsx)
Reviewer Test Plan
I added some more tests, and run with the existing ones.
Testing Matrix






- `allenhutchison` (2025-08-02): It looks like you have some linting errors that will need to be fixed. Also, we now have the marked package available in the app, so we could shift to using it in our markdown tools for detecting code blocks.
- `allenhutchison` (2025-08-11): Thanks again for your contribution and your participation in the community. In an effort to clean up older PRs I'm going to close this one, for now. Please reopen and ping me if you decide to take this up again.

### PR-38 #21775 | Newcomer (≤ 3 Actions) | Phase II (Jan–Apr '26) | merged
https://github.com/google-gemini/gemini-cli/pull/21775 | author `cynthialong0-0` (CONTRIBUTOR) | created 2026-03-09 | closed 2026-03-13 | TTFR 62.2h | labels priority/p1, area/security, size/l, 🔒 maintainer only
+283/-3 LOC, 8 files, linked issues 0, merged by cynthialong0-0
**Title:** feat(agent): add allowed domain restrictions for browser agent
**Body:** Summary
Add an optional allowedDomains to agents.browser setting to make sure browser agent to only navigate to allowed domains. If not set, it will be default to [*.google.com, github.com, localhost].
Details
This allowedDomains will be checked in:

BorwserManager.callTool before calling the MCP server, if it is not allowed, it will return an error result directly.
When connecting to mcp, it will


### PR-39 #19539 | Newcomer (≤ 3 Actions) | Phase II (Jan–Apr '26) | merged
https://github.com/google-gemini/gemini-cli/pull/19539 | author `JagjeevanAK` (CONTRIBUTOR) | created 2026-02-19 | closed 2026-02-28 | TTFR 143.1h | labels priority/p2, area/platform, area/non-interactive, size/m, help wanted
+131/-2 LOC, 2 files, linked issues 1, merged by scidomino
**Title:** fix: use full paths for ACP diff payloads
**Body:** Summary
Use full file paths in ACP diff payloads so IDE clients can render diffs correctly.
Details
Switch diff path values from fileName to filePath (with fallback when emitting tool results).
Related Issues
Closes #18808
How to Validate

Run the CLI in ACP mode and trigger a file edit that requires confirmation.
Ensure the IDE client shows a diff using the correct file path.

Pre-Merge Checklist

- `JagjeevanAK` (2026-02-24): hey @gundermanc can you check this PR ?
- `JagjeevanAK` (2026-02-25): hey @scidomino can you check this PR ?
- `scidomino` (2026-02-25): You have a bunch of failing tests. Please fix. Also, in the future, don't work on issues you're not assigned to.
- `JagjeevanAK` (2026-02-28): @scidomino pushed a signed-off test-only fix for the two failing zedIntegration assertions. Please re-run CI when possible.

### PR-40 #25832 | Newcomer (≤ 3 Actions) | Phase II (Jan–Apr '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/25832 | author `pthanki` (NONE) | created 2026-04-22 | closed 2026-04-22 | TTFR none | labels size/xs, status/need-issue
+1/-0 LOC, 1 files, linked issues 0, merged by None
**Title:** fix: Enter key unresponsive after selecting a skill from / command dropdown
**Body:** Problem
When using the / command in Gemini CLI to invoke a skill, pressing Enter after selecting a skill from the autocomplete dropdown does nothing. The CLI silently ignores the keypress and the skill is never triggered.
Steps to reproduce

Type / in the Gemini CLI prompt — the dropdown shows available skills
Use arrow keys to navigate and select a skill
Press Enter to run the selected skill







### PR-41 #19603 | Newcomer (≤ 3 Actions) | Phase II (Jan–Apr '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/19603 | author `BayarBH` (NONE) | created 2026-02-20 | closed 2026-02-20 | TTFR none | labels size/l
+885/-0 LOC, 6 files, linked issues 0, merged by None
**Title:** feat(cowork): Phase 2 — Multimodal, 2M Context & Advanced Tools
**Body:** Summary

src/agent/context-manager.ts — ProjectIndexer feeds the full codebase
into Gemini's 2M-token context window (manifest + git history + files).
src/tools/vision.ts — screenshot_and_analyze: URL/desktop/file capture
→ Gemini 2.0 vision analysis via @google/genai inlineData.
src/tools/search.ts — search: Gemini 2.0 native googleSearch grounding
with deduplicated source URLs.
src/tools/log-mon


### PR-42 #26149 | Newcomer (≤ 3 Actions) | Phase II (Jan–Apr '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/26149 | author `yeelam-gordon` (NONE) | created 2026-04-28 | closed 2026-05-13 | TTFR none | labels size/l, status/need-issue, status/pr-nudge-sent
+831/-0 LOC, 9 files, linked issues 0, merged by None
**Title:** feat(session): expose runtime identity for external observers
**Body:** Summary
Adds a small JSON runtime-identity sidecar at <session-temp>/runtime.json while a Gemini CLI session is alive, so external tools can answer:

"Is there a gemini-cli process currently running against session X?"

The file records (pid, sessionId, workDir, hostname, startedAt, geminiCliVersion). Consumers parse the file and verify the recorded PID is alive (OS-specific). It is the most relia

- `yeelam-gordon` (2026-04-28): Update: pushed a follow-up commit (eeaf84f) covering two reliability hardening items I'd missed in the initial port:    Concern Status (after follow-up)     Atomic tmp + fsync + rename, cleanup .tmp on failure ✅ matched in initial commit   UnicodeDecodeError → null (truncated UTF-8) ✅ TextDecoder({fatal:true})   Explicit isinstance-style type checks, no coercion ✅ typeof + Number.isInteger   Exclude bool from int guards ✅ typeof true === 'boolean' is naturally distinct from 'number'; covered by rejects bool pid test   No cleanup-on-quit (consumers verify PID liveness) ✅ followed   Test: no .tm
- `yeelam-gordon` (2026-04-29): Pushed a follow-up commit (e8091fab) that addresses a same-PID cross-session correctness issue. The bug being fixed When the same PID switches to serving a different session id mid-flight, the previous session's runtime.json keeps claiming this PID. An external observer running a PID-liveness check would then see one PID mapped to two different sessions and treat both as live — breaking the documented PID → session contract. Gemini-cli paths that perform an in-process session switch    Path What changes the session id     /clear (/new alias) – clearCommand.ts resetNewSessionState(<freshUUID>) 
- `yeelam-gordon` (2026-04-29): Refactored to mirror the cleaner shape from the parallel qwen-code port (PR #3714) — pushed fa05e761. What changed The same-PID session swap dance (clearRuntimeStatus(old) + writeRuntimeStatus(new, ...)) used to live at every caller of the session-id-changing methods:    Before After     4-step dance duplicated in clearCommand.ts AND useSessionBrowser.ts Single chokepoint inside Config.setSessionId, gated on a new runtimeStatusEnabled ownership flag    Config now has:  A private runtimeStatusEnabled = false field A markRuntimeStatusEnabled() public method, called by gemini.tsx immediately afte

### PR-43 #29115 | Newcomer (≤ 3 Actions) | Phase III (May–Sep '26) | merged
https://github.com/google-gemini/gemini-cli/pull/29115 | author `jesussamuel-byte` (CONTRIBUTOR) | created 2026-08-28 | closed 2026-09-04 | TTFR 95.3h | labels size/l, size/xl, status/need-issue
+2199/-60 LOC, 8 files, linked issues 0, merged by DavidAPierce
**Title:** fix(config): enforce strict permission and ownership checks on system-wide configuration paths
**Body:** Summary
Enforces file ownership and access control list (ACL) verification for system-wide configuration files on Windows and POSIX platforms before  loading configuration settings.
Details

Windows Security Validation: Implemented ACL verification using PowerShell in @google/gemini-cli-core (isPathSecureSync, buildWindowsAclScript, parseWindowsSecurityOutput). Confirms that unprivileged users and


### PR-44 #28432 | Newcomer (≤ 3 Actions) | Phase III (May–Sep '26) | merged
https://github.com/google-gemini/gemini-cli/pull/28432 | author `joneba` (CONTRIBUTOR) | created 2026-07-17 | closed 2026-07-28 | TTFR 0.3h | labels size/l, size/xl, status/need-issue, status/pr-nudge-sent
+475/-0 LOC, 2 files, linked issues 0, merged by joneba-google
**Title:** feat(pr-generator-db): implement Firestore concurrency dual-locking and test ingestion utilities
**Body:** Overview
This PR adds the central Firestore database interface (db_interface.py) for the Gemini CLI Issue-to-PR Code Generation Pipeline (gcli-intern-project-2026). It provides transactional locking routines,
document ID resolution, lifecycle status enums, and state transition helpers for the orchestrator and worker jobs.
──────
Summary of Changes
1.  Concurrency Dual-Locking & State Machine (db_i

- `sinansonmez` (2026-07-17): /gemini which model you are?
- `adamfweidman` (2026-07-21): I think you will want to add an init.py so this can be imported easily in the future :)

### PR-45 #27603 | Newcomer (≤ 3 Actions) | Phase III (May–Sep '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/27603 | author `vivekjm` (NONE) | created 2026-06-01 | closed 2026-06-16 | TTFR none | labels priority/p3, area/agent, size/m, status/pr-nudge-sent
+127/-0 LOC, 3 files, linked issues 1, merged by None
**Title:** fix(core): add platform-aware shell guidance
**Body:** Summary

add platform-aware shell usage guidance to the preview-model operational prompt
call out Windows-specific inspection commands instead of Unix-only examples on win32
cover the Windows prompt snippet in the core prompt test

Fixes #27751
Test plan

npm test --workspace @google/gemini-cli-core -- prompts.test.ts

- `vivekjm` (2026-06-09): Addressed the review threads in commit 64f67b2 by switching Windows large-output guidance to targeted commands (findstr, Get-Content -Tail, Select-String) and updating the prompt test expectation. Also opened and linked tracking issue #27751 for the status/need-issue requirement. Tested locally:  npm test --workspace @google/gemini-cli-core -- prompts.test.ts

### PR-46 #28096 | Newcomer (≤ 3 Actions) | Phase III (May–Sep '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/28096 | author `KittiphonKamnuan` (NONE) | created 2026-06-22 | closed 2026-07-07 | TTFR none | labels area/agent, size/m, status/pr-nudge-sent
+120/-9 LOC, 5 files, linked issues 1, merged by None
**Title:** fix(core): drop late tool calls after SIGINT cancellation (#28091)
**Body:** Summary
Closes #28091.
A SIGINT delivered after the stream consumer has already started a turn can still result in a delayed provider tool-call chunk being executed locally — the side effect runs and the tool result is submitted back to the model after the user has cancelled. The standalone reproducer in the issue confirms this on 0.47.0.
Root cause
The abort signal is only checked at the top of e

- `KittiphonKamnuan` (2026-06-23): Thanks for catching the queue leak, @gemini-code-assist. Fixed in e0efeb8 by moving the abort guard inside the try { ... } finally { ... } block instead of returning before the finally runs. This keeps the existing cleanup pattern intact:  isProcessing = false state.clearBatch() _processNextInRequestQueue()  ← was being skipped before, now runs on the aborted path too  Slightly different from the suggested patch (which duplicated the cleanup into the early-return branch) — putting the guard inside try means the cleanup lives in exactly one place, which I think is easier to maintain. Added a re

### PR-47 #28363 | Newcomer (≤ 3 Actions) | Phase III (May–Sep '26) | CLOSED
https://github.com/google-gemini/gemini-cli/pull/28363 | author `Arjan-P` (NONE) | created 2026-07-12 | closed 2026-07-27 | TTFR none | labels priority/p2, area/core, size/xs, status/pr-nudge-sent
+6/-1 LOC, 1 files, linked issues 1, merged by None
**Title:** fix(core): prevent AbortSignal listener leak in ShellExecutionService
**Body:** Summary

fix(core): prevent AbortSignal listener leak in ShellExecutionService

Details
Ensured the AbortSignal event listener is explicitly removed when a process finishes naturally, preventing potential memory leaks during long-lived CLI sessions.
Related Issues
Fixes #28280
Validate
Run npm test -w @google/gemini-cli-core -- src/service/shellExecutionService.test.ts
Should pass all 66 tests


## ISSUES

### ISSUE-01 #29434 | - | Phase III (May–Sep '26) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/29434 | author `junkwd` (NONE) | created 2026-09-21 | closed 2026-09-30 | TTFR none | labels priority/p1, area/core, kind/bug, status/manual-triage, effort/medium
**Title:** Headless `-p` with piped stdin hangs at 100% CPU (uninterruptible) when input contains `"@scope/pkg"` followed by quoted strings — @-command regex swallows the text, glob fallback stalls in minimatch
**Body:** What happened?
In headless mode (-p with content piped on stdin), the CLI hangs before sending any request to the model when the piped text contains an @-prefixed token that is immediately followed by a double quote and then more quoted strings — the most common case being source code with a scoped npm import such as import { x } from "@scope/pkg"; followed by other import … from "…" lines.
Sympto


### ISSUE-02 #28258 | - | Phase III (May–Sep '26) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/28258 | author `aniruddhaadak80` (CONTRIBUTOR) | created 2026-07-05 | closed 2026-10-14 | TTFR none | labels priority/p2, area/extensions, status/bot-triaged, kind/bug, effort/large
**Title:** refactor(cli): decouple useGeminiStream from lookahead logic for parallel agents
**Body:** What happened?
The useGeminiStream hook currently implements a tactical UI lookahead fix to prevent parallel agents from tearing visually when they finish at slightly different times.
See useGeminiStream.ts.
What did you expect to happen?
Architecturally, useGeminiStream should not be responsible for stitching together semantic batches using timing/refs.
packages/core should be refactored to emit 


### ISSUE-03 #29500 | - | Phase III (May–Sep '26) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/29500 | author `hugopicanzo` (NONE) | created 2026-09-25 | closed 2026-09-25 | TTFR none | labels status/need-triage, area/documentation
**Title:** Docs: typo in README installation section
**Body:** 


### ISSUE-04 #28696 | - | Phase III (May–Sep '26) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/28696 | author `gundermanc` (MEMBER) | created 2026-08-05 | closed 2026-08-12 | TTFR 0.0h | labels priority/p3, area/core, status/bot-triaged, kind/enhancement, help wanted, effort/large
**Title:** GSoC project issue
**Body:** Issue tracking the completion of the 2026 Quality GSoC contributor project.
Do not close.


### ISSUE-05 #28522 | - | Phase III (May–Sep '26) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/28522 | author `chadd28` (CONTRIBUTOR) | created 2026-07-23 | closed 2026-07-23 | TTFR none | labels status/need-triage, auto-close
**Title:** [test] 3
**Body:** testing app


### ISSUE-06 #26809 | - | Phase III (May–Sep '26) | NOT_PLANNED
https://github.com/google-gemini/gemini-cli/issues/26809 | author `Codeleafly` (NONE) | created 2026-05-10 | closed 2026-05-11 | TTFR none | labels priority/p2, area/core, status/bot-triaged, kind/bug, effort/small
**Title:** Potential for NaN in VirtualizedList scroll calculations
**Body:** What happened?
The calculation for actualScrollTop lacks defensive checks for cases where offsets or scrollAnchor.index are undefined or out of sync with the data array.
What did you expect to happen?
Add boundary checks and fallback values to ensure actualScrollTop always returns a valid number.
Client Information

Client Information
OS: linux
Date: Sunday, May 10, 2026
Gemini CLI: 0.42.0-nightly


### ISSUE-07 #26871 | - | Phase III (May–Sep '26) | NOT_PLANNED
https://github.com/google-gemini/gemini-cli/issues/26871 | author `vanshikavanshika-a11y` (NONE) | created 2026-05-11 | closed 2026-05-11 | TTFR none | labels status/need-triage, area/unknown
**Title:** As I mentioned [earlier this week](https://github.com/google-gemini/gemini-cli/discussions/22654), we have updated our project list based on current needs and individual maintainers' own interests. Project ideas have been documented as issues in the repo. The current projects are as follows:
**Body:** As I mentioned earlier this week, we have updated our project list based on current needs and individual maintainers' own interests. Project ideas have been documented as issues in the repo. The current projects are as follows:
[Build a suite of Gemini CLI skills for common investigative workflows — memory dump analysis, profiling, and performance diagnostics ]   (https-github.com-google-gemini-ge


### ISSUE-08 #27908 | - | Phase III (May–Sep '26) | NOT_PLANNED
https://github.com/google-gemini/gemini-cli/issues/27908 | author `mainmann` (NONE) | created 2026-06-14 | closed 2026-08-28 | TTFR none | labels priority/p3, area/platform, Stale, status/bot-triaged, kind/enhancement
**Title:** Gemini CLI is better in usage and getting task done than Antigravity CLI
**Body:** What would you like to be added?
Gemini daily quota limit and the tasks, it gets done is much better than Antigravity CLI, AGY gives weekly quota for gemini model, performance is good but usage and token gets burned quickly by subagents  compare to gemini Cli.  I was thinking to upgrade my plan but due to limitation for system cooldown, it does not look like good choice. AGY have powerful models b


### ISSUE-09 #27688 | - | Phase III (May–Sep '26) | NOT_PLANNED
https://github.com/google-gemini/gemini-cli/issues/27688 | author `seb-luke` (NONE) | created 2026-06-05 | closed 2026-08-26 | TTFR 4.2h | labels priority/p1, area/agent, Stale, status/bot-triaged, kind/bug
**Title:** Unable to use gemini-3.5-flash via VertexAI after v0.45.1
**Body:** What happened?
After upgrading to Gemini CLI version 0.45.1, the default gemini-3.5-flash was not working anymore and I received a suggestion to revert back to gemini-3.1-pro-preview. I have tried using gemini -m gemini-3.5-flash as well as inside the CLI using /model manage and even setting the version inside the settings. Nothing worked, the same issue has appeared.
I have asked Gemini, it check

- `sundaywind` (2026-06-05): This bug is real, and I’ve run into the same issue too.
- `vobornik` (2026-06-05): I can confirm this issue. After upgrading to v0.45.1, attempting to use gemini-3.5-flash under Vertex AI fails because the CLI incorrectly truncates the model name to gemini-3-flash in the API request, resulting in a 404 error:  projects/<your-project-id>/locations/global/publishers/google/models/gemini-3-flash was not found or your project does not have access to it.  Temporary Workaround Downgrading to the previous stable version (v0.45.0) immediately resolves the issue: npm install -g @google/gemini-cli@0.45.0
- `Dragon1573` (2026-06-08): So do I. Does any contributors identify the root cause? 00:26:29 D:\...\winget-pkgs  [issues/383039 ≡ +1 ~0 -0 !] 1ms pwsh $ gemini.ps1 --model auto -p "Introduce yourself in brief." Ripgrep is not available. Falling back to GrepTool. Error when talking to Gemini API Full report available at: C:\Users\MASKED\AppData\Local\Temp\gemini-client-error-Turn.run-sendMessageStream-2026-06-08T16-27-09-068Z.json ModelNotFoundError: Publisher Model `projects/MASKED/locations/asia-northeast1/publishers/google/models/gemini-3-flash` was not found or your project does not have access to it. Please ensure yo
- `tgmof` (2026-06-09): I think the title is wrong/misleading but I understand what you mean:  Assuming one use export GOOGLE_GENAI_USE_VERTEXAI=true and export GOOGLE_CLOUD_LOCATION="global" The "Auto" model selection is the default in Gemini CLI In Version 0.45.0, the "Auto" mode was setup to use gemini-3 / gemini 3.1 and it was working as expected. In 0.45.1 and 0.45.2, the "Auto" mode is setup to use gemini-3.5-flash as the orchestrator model but it fails with a 404 Not found error but it also offers to continue with a fallback model that works:    Rolling back the 0.45.0 "fixes" the issue (since 3.5 is not used 
- `anishs1207` (2026-06-11): Issue can be closed, already fixed in f08b4af.

### ISSUE-10 #27564 | - | Phase III (May–Sep '26) | NOT_PLANNED
https://github.com/google-gemini/gemini-cli/issues/27564 | author `kapcho` (NONE) | created 2026-05-29 | closed 2026-08-13 | TTFR none | labels priority/p1, area/agent, Stale, status/possible-duplicate, status/bot-triaged, kind/bug
**Title:** [Urgent] Severe Business Impact and Repeated Service Failure of Gemini CLI/API in Production Environment
**Body:** What happened?

Customer Information & Business Context


Customer Email: kapcho.park@gmail.com
Role: Senior Specialist / Project Lead (Solution Development)
Project Status: Critical delivery phase with upcoming Executive Leadership Reporting (Next Week).
Service Level: Paid User (High token consumption and API usage).


Background of Complaint (Executive Summary)
The user is leading a high-comple


### ISSUE-11 #17334 | - | Phase II (Jan–Apr '26) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/17334 | author `sehoon38` (CONTRIBUTOR) | created 2026-01-22 | closed 2026-06-01 | TTFR none | labels priority/p2, area/platform, 🔒 maintainer only, workstream-rollup, status/bot-triaged, kind/enhancement
**Title:** [Epic] Streamline A/B Testing & Experimentation Workflow
**Body:** Tracking issue for making A/B testing easier and more accessible within Gemini CLI. The goal is to reduce friction and dependency on external/internal tools (google3) for common experimentation tasks.
Context
We have existing A/B testing capabilities, but they are not fully utilized. The current process likely involves too much overhead or context switching.
Goals

Ease of Use: Make starting an A/


### ISSUE-12 #19965 | - | Phase II (Jan–Apr '26) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/19965 | author `anj-s` (CONTRIBUTOR) | created 2026-02-22 | closed 2026-03-10 | TTFR none | labels status/need-triage, area/platform
**Title:** Implement behavioral evals for tracker (implicit and explicit prompting)
**Body:** 


### ISSUE-13 #21599 | - | Phase II (Jan–Apr '26) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/21599 | author `django-hunter` (NONE) | created 2026-03-08 | closed 2026-03-08 | TTFR none | labels status/need-triage, area/security
**Title:** Bug: OAuth users get 400 INVALID_ARGUMENT on every request due to project number vs project ID mismatch
**Body:** Original content removed — This issue contained inaccurate information. The root cause was a local misconfiguration (GOOGLE_CLOUD_PROJECT set to a numeric project number). See the correct diagnosis in Discussions #21603 instead. Closing
this issue.


### ISSUE-14 #20941 | - | Phase II (Jan–Apr '26) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/20941 | author `KumarADITHYA123` (CONTRIBUTOR) | created 2026-03-03 | closed 2026-03-11 | TTFR 0.4h | labels priority/p2, area/core, help wanted
**Title:** Bug: PTY Shell aborts orphan nested background processes causing OS-level resource exhaustion
**Body:** What happened?
OVERVIEW While auditing the cross-platform execution lifecycles in packages/core/src/services/shellExecutionService.ts and process-utils.ts for a GSoC prototype, I identified a severe resource exhaustion vector relating to Node-PTY subsystem tear-downs.
Note: This architectural report is distinct from PR #20916 and Issue #15945. PR #20916 addresses a File Descriptor leak (via missin

- `KumarADITHYA123` (2026-03-03): Hello @Solventerritory , Thank you for your interest in helping with this issue! Please note that I am already actively investigating this and have completed the cross-platform architectural fix locally. My implementation successfully extends the KillOptions interface to support native taskkill tree teardowns on Windows, while preserving the process.kill group semantics for POSIX environments. The Vitest mock assertions have already been updated and the TypeScript compiler checks are passing flawlessly with zero CI regressions. I am currently finalizing the local branch and will be pushing up 

### ISSUE-15 #20190 | - | Phase II (Jan–Apr '26) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/20190 | author `sehoon38` (CONTRIBUTOR) | created 2026-02-24 | closed 2026-03-05 | TTFR none | labels status/need-triage, 🔒 maintainer only, workstream-rollup
**Title:** Improve integration testing for API request/response parsing
**Body:** Enhance our E2E and integration tests to specifically exercise various API response scenarios.

Add test cases that simulate "incomplete" or metadata-only messages in a stream.
Verify that the CLI can continue processing a stream even if intermediate chunks lack standard fields.


### ISSUE-16 #20885 | - | Phase II (Jan–Apr '26) | DUPLICATE
https://github.com/google-gemini/gemini-cli/issues/20885 | author `vladivis` (NONE) | created 2026-03-02 | closed 2026-05-19 | TTFR 884.0h | labels priority/p2, area/core, status/needs-info, status/need-retesting, status/bot-triaged, kind/bug, type/bug, effort/medium
**Title:** UI recursion/infinite scrolling when expanding large diffs via Ctrl+O (macOS/Zed)
**Body:** What happened?
When attempting to expand a large tool output (e.g., a write_file call with ~300 lines of code) using the Ctrl+O shortcut, the terminal UI enters an infinite recursion loop.
What did you expect to happen?
The content should expand, allowing the user to scroll through the diff normally.
Client information

CLI Version: 0.31.0
Git Commit: 72c6533
Session ID: d1336d8a-7620-48d7-99f2-1a

- `cocosheng-g` (2026-04-08): @vladivis, this issue has been inactive for over a month. Could you please try reproducing it with the latest nightly build and let us know if it still occurs? If we don't hear back, we will close this issue on 2026-04-22.
- `arunap2509` (2026-04-12): @cocosheng-g Hi i am facing the same issue, i am on v0.37, the latest as of now. It happens when i press ctrl O to expand the agent changes to files. I am in M1 Mac pro
- `Kovinda` (2026-04-17): Facing the same issue on v0.38.2. Happens when i press CTRL + O. On Windows 11 just like the video in #23518
- `vladivis` (2026-04-19): @cocosheng-g the problem remains, it's still not resolved, I'm working with the previous "alternate buffer" hotfix, but the smoothness of terminal scrolling and copying text from it leaves much to be desired. Gemini CLI v0.40.0-nightly.20260415.g06e7621b2
- `afernando79` (2026-04-23): If it helps, if I attempt to click and move the vertical scrollbar slowly through the entire history of messages after clicking CTRL+O, then it appears to settle the terminal. It is as if, the CTRL+O is attempting to expand ALL previous interactions which triggers a redraw or something for every single one. Scrolling feels like it is forcing the terminal to gradually go through each of these and expand them one by one. I cannot confirm this is definitely the case though, just felt like that was what was happening. Perhaps, can someone confirm if the CTRL+O is constrained to the most recent int
- `vladivis` (2026-05-08): @cocosheng-g , after finding the new “Terminal Buffer” setting and enabling it, I've been working with gemini-cli for a week now, and I can say that the issue has most likely been resolved. This setting fixes the whole problem. Gemini CLI v0.41.2

### ISSUE-17 #19970 | - | Phase II (Jan–Apr '26) | NOT_PLANNED
https://github.com/google-gemini/gemini-cli/issues/19970 | author `thiago-cavalcanti` (NONE) | created 2026-02-22 | closed 2026-05-29 | TTFR 1432.9h | labels priority/p2, area/enterprise, status/bot-triaged, kind/bug, status/need-information
**Title:** OAuth flow forces consumer Google One AI Pro entitlement over Enterprise Gemini Code Assist Standard, stripping proprietary IP guarantees
**Body:** What happened?
Description:
There is a critical entitlement routing conflict in the Gemini CLI for users who hold overlapping subscriptions on a single Google account. When an account has both a consumer Google One AI Pro/Ultra subscription and a Google Cloud-managed Enterprise Gemini Code Assist Standard annual or monthly license, the CLI's authentication flow completely ignores the Enterprise li

- `thiago-cavalcanti` (2026-03-10): Here's what Gemini 3.1 Pro on gemini-cli itself says about this issue after reading it and investigating this project's source code for an answer: Based on a thorough investigation of the gemini-cli codebase, I can confirm that the root cause of this bug is indeed within the gemini-cli itself.    While the Google backend server decides what tier is marked as "default" or "current," the CLI's codebase is hardcoded to blindly accept these values without ever presenting a choice to the user, even if the backend indicates that multiple entitlements are available.     Here is exactly what is happen
- `weogrim` (2026-04-23): I'm experiencing the exact same issue. After updating to version 0.39 today, the quota field appeared, and out of curiosity, I checked it only to find my quota is set to 200. I have everything properly set up in the Google Cloud Console. I have Owner rights, and I also explicitly added the permissions required according to this official tutorial: https://cloud.google.com/gemini/docs/codeassist/set-up-gemini Furthermore, I have my GOOGLE_CLOUD_PROJECT environment variable set correctly, and the paid subscription is successfully assigned to my email. The CLI seems to be completely ignoring my co

### ISSUE-18 #23336 | - | Phase II (Jan–Apr '26) | NOT_PLANNED
https://github.com/google-gemini/gemini-cli/issues/23336 | author `sergeiwallace` (NONE) | created 2026-03-21 | closed 2026-07-24 | TTFR 1.1h | labels priority/p2, area/core, Stale, status/bot-triaged, kind/bug, type/bug, effort/small
**Title:** "s94>thought" thought blocks leaking into terminal stdout
**Body:** What happened?
Describe the bug
During long interactive sessions, the internal, system-mandated thought blocks (e.g., ...94>thought) generated by the model prior to tool execution are bleeding through the UI layer and being printed directly to the terminal's standard output.
To Reproduce

Run gemini-cli in interactive mode.
Engage in a long, multi-turn session with heavy tool usage (e.g., run_shel

- `spigell` (2026-03-21): Yes, I noticed it happened when control is handed back to the main agent for a "continuation turn" ( from cli_help, for example ). Quite funny, but messy.
- `sergeiwallace` (2026-03-21): Update on root cause & replication: After further testing, we've identified that this bug is directly tied to session context size and chunk streaming. Restarting the terminal pane or running a soft restart (Shift+R) does not fix the issue if the user remains in the same session ID. The thought tags continue to bleed through into standard output. The Hypothesis:  In long, turn-intensive sessions with heavy tool usage, the JSON session history becomes massive. Because the gemini-cli client is streaming responses, the system-mandated  or ...94>thought blocks are likely getting split across netwo

### ISSUE-19 #19885 | - | Phase II (Jan–Apr '26) | NOT_PLANNED
https://github.com/google-gemini/gemini-cli/issues/19885 | author `data-coeur-anonymous` (NONE) | created 2026-02-22 | closed 2026-05-15 | TTFR 6.8h | labels priority/p3, area/core, area/security, Stale, status/bot-triaged, kind/bug, effort/medium
**Title:** Gemini Code Assist OAuth Sign-In fails with VS Code Remote Tunnels (localhost callback unreachable)
**Body:** What happened?
When using Gemini Code Assist in VS Code connected via Remote Tunnels (not SSH, not Dev Containers — actual code tunnel), the OAuth sign-in flow fails because the callback redirects to http://localhost:PORT/oauth2redirect?... which is not reachable from the local browser.
The extension starts a temporary HTTP server on a random port (e.g., 37273, 41885) inside the remote machine to 

- `Devnil434` (2026-03-03): @data-coeur-anonymous plz check the PR
- `cocosheng-g` (2026-05-15): This issue has been inactive for quite some time, so we are closing it as part of our routine backlog maintenance. If this is still affecting you on the latest version, please feel free to comment or open a new issue. Thanks!
- `renkoha28` (2026-05-15): Hi, i'm encountering this issue today may 15 2026 and the steps described to fix it worked for me, issue is still happening, my setup is windows with WSL ubuntu

### ISSUE-20 #15918 | - | Phase II (Jan–Apr '26) | DUPLICATE
https://github.com/google-gemini/gemini-cli/issues/15918 | author `sushovande` (NONE) | created 2026-01-05 | closed 2026-01-05 | TTFR 4.8h | labels area/agent
**Title:** Gemini went into a crazy loop
**Body:** What happened?
I asked it to create a new program from scratch. It did that well. After a few follow up changes, it began to spiral into repeated loops of checking things, muttering to itself, and then finally produced a long string of assertions like "I propose. I suggest. I counsel."
What did you expect to happen?
stop gracefully after successfully accomplishing the task
Client information

CLI 

- `abhipatel12` (2026-01-05): Thanks for sharing. We're seeing this across a few different issues and will consolidate them to #15938

### ISSUE-21 #12893 | - | Phase I (Jun–Dec '25) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/12893 | author `rcjsuen` (NONE) | created 2025-11-11 | closed 2025-11-21 | TTFR none | labels priority/p1, area/core, status/possible-duplicate
**Title:** Authentication URL is cut off in iTerm2
**Body:** What happened?
The OAuth URL does not word wrap in iTerm2 when running Gemini CLI inside a container.
What did you expect to happen?
The URL should wrap and I should be able to click on it to login.
Client information
I can't provide this since I can't even type /about.
Operating system: macOS 26.0.1
iTerm2: 3.6.5
Gemini CLI version: 0.13.0
Node version: 24.11.0
Login information
This was tested w


### ISSUE-22 #7029 | - | Phase I (Jun–Dec '25) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/7029 | author `mrcabbage972` (CONTRIBUTOR) | created 2025-08-25 | closed 2025-08-26 | TTFR none | labels area/core
**Title:** Maintain alternating chat history for empty or thought-only model responses
**Body:** What happened?
The issue is a flaw in the recordHistory method's logic. When the model's response contained only non-visible content (like a thought part), the method would filter it out but then fail to add a placeholder empty model turn. This would either leave two consecutive user turns in the history (in streaming mode) or simply an incomplete turn, causing tests to fail and breaking conversat


### ISSUE-23 #10417 | - | Phase I (Jun–Dec '25) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/10417 | author `silviojr` (CONTRIBUTOR) | created 2025-10-02 | closed 2025-10-02 | TTFR none | labels priority/p2, area/agent
**Title:** Add "Finish tool" support to subagents
**Body:** What would you like to be added?
It will allow the agent to choose when to finish instead of forcing it to finish
Why is this needed?
Better performance on swebench
Additional context
No response


### ISSUE-24 #1498 | - | Phase I (Jun–Dec '25) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/1498 | author `chingchun94` (NONE) | created 2025-06-25 | closed 2025-12-03 | TTFR 0.2h | labels priority/p2, Stale
**Title:** API Error: Unexpected line format in response:
**Body:** Describe the bug
When asking for "how to run in sandbox", it returns API Error
Client information
Windows
Windows PowerShell Text.txt

Additional context
Nope

- `chingchun94` (2025-06-25): I think it should prompt the user to login/provide API instead of returning the error? Didnt experience this when using WSL + windows
- `veilm` (2025-06-25): I think in your example the request fully succeeded on the "how to run in sandbox?" and only failed on the subsequent "how does the restriction work?" It would have failed on the first if your authentication wasn't configured
- `alex-orlovskyi` (2025-06-25): https://developers.google.com/gemini-code-assist/resources/available-locations Gemini CLI / Code assist plugin might be not available for you, if your personal gmail account bounded to country not in this list ^^.
- `adhhamofficial` (2025-06-26): The same error occurred to me halfway through a prompt. (Original prompt: "create an ecommerce website with plain php, html, css, js and use sqlite as db") I just asked it to continue the previous command and it successfully did. Model: gemini-2.5-flash System: WSL2 (Ubuntu)
- `pbartoszek` (2025-09-24): After upgrading to version 0.6.0 I hit the same issue:(( I am using Windows 11 and standard Terminal ✕ [API Error: Unexpected line format in response: ,] /about gives me │                                                        │ │ About Gemini CLI                                       │ │                                                        │ │ CLI Version        0.6.0                               │ │ Git Commit         7e1bce7                            │ │ Model              gemini-2.5-pro                      │ │ Sandbox            no sandbox                          │ │ OS              
- `emilianomoscato` (2025-09-25): I am having the same issue running Gemini CLI 0.6.1 on macOS 15.6.1
- `pbartoszek` (2025-10-01): It's working again for me but now from time to time I get ✕ [API Error: Model stream ended with an invalid chunk or missing finish reason.]
- `shannamurry` (2025-10-03): I have the same issue with EVERY prompt I try - what a piece of garbage - google, are you interested in fixing this bug or what? I am using 0.7.0 on MacOS 15.6 - authentication via oauth.  Here's the error:  { "error": { "message": "Unexpected line format in response: ,", "stack": "Error: Unexpected line format in response: ,\n    at file:///Users/shanna.murry/.nodenv/versions/20.19.3/lib/node_modules/@google/gemini-cli/node_modules/@google/gemini-cli-core/dist/src/code_assist/server.js:128:27\n    at process.processTicksAndRejections (node:internal/process/task_queues:95:5)\n    at async file

### ISSUE-25 #8030 | - | Phase I (Jun–Dec '25) | COMPLETED
https://github.com/google-gemini/gemini-cli/issues/8030 | author `rramkumar1` (CONTRIBUTOR) | created 2025-09-08 | closed 2025-09-13 | TTFR none | labels priority/p3
**Title:** Export saved chats to Markdown
**Body:** What would you like to be added?
A command like this would be useful for demonstrating what Gemini CLI has done to other team members:
/chat export foo filename.md

Markdown is much easier to digest than copying the raw json file of the saved conversation.
Why is this needed?
Makes it easy to show off something cool that Gemini CLI did!
Additional context
No response


### ISSUE-26 #10799 | - | Phase I (Jun–Dec '25) | NOT_PLANNED
https://github.com/google-gemini/gemini-cli/issues/10799 | author `xytras1` (NONE) | created 2025-10-09 | closed 2026-01-11 | TTFR 3.8h | labels priority/p3, Stale
**Title:** Gemini CLI support for Gemini 2.5 Computer Use model
**Body:** What would you like to be added?
Gemini CLI support for Gemini 2.5 Computer Use model . This probably should be the default model for Gemini CLI since "Computer Use" is the main purpose IMO.
https://blog.google/technology/google-deepmind/gemini-computer-use-model/
Why is this needed?
Gemini CLI "Computer Use" is the main purpose IMO
Additional context
No response

- `bobcatfish` (2025-10-09): Interesting point! We'll see what the folks focused on model quality think - we have some support at the moment for switching at least between flash and pro models.

### ISSUE-27 #2016 | - | Phase I (Jun–Dec '25) | DUPLICATE
https://github.com/google-gemini/gemini-cli/issues/2016 | author `meatpaste` (NONE) | created 2025-06-26 | closed 2025-06-27 | TTFR 0.1h | labels 
**Title:** Editor setting incorrectly reports Windsurf (Not installed)
**Body:** What happened?
Editor list said Windsurf is not installed, but i'm using the Gemini CLI from within WIndsurf in fact.
What did you expect to happen?
Able to select Windsurf editor
Client information

CLI Version: 0.1.4
Git Commit: 1078a54
Operating System: darwin v23.11.0
Sandbox Environment: no sandbox
Model Version: gemini-2.5-pro
Memory Usage: 205.3 MB

Login information
No response
Anything el

- `ptone` (2025-06-26): is there a windsurf command on your path? See #1778 for similar
- `tifroz` (2025-06-27): Not sure this is a duplicate of the linked cursor issue? I am working on a MacOS 15.5, where the windsurf executable lives at /Applications/Windsurf.app/Contents/MacOS/Electron. I do have an alias setup (see which command output below) which windsurf windsurf: aliased to /Applications/Windsurf.app/Contents/MacOS/Electron  It doesn't work for me,  the Gemini CLI says Windsurf (Not installed). What is the CLI looking for? │ CLI Version            0.1.3                                      │ │ Git Commit             382486e (local modifications)              │ │ Model                  gemini-2.5-
- `alkindi17` (2025-06-28): @tifroz  Try installing the windsurf command by pressing cmd+shift+p > Install 'surf' command in Windsurf. Open a new terminal window. Try running gemini again.  This worked for me

### ISSUE-28 #12900 | - | Phase I (Jun–Dec '25) | NOT_PLANNED
https://github.com/google-gemini/gemini-cli/issues/12900 | author `MoDeMFoX` (NONE) | created 2025-11-11 | closed 2026-02-15 | TTFR none | labels status/need-triage, priority/p2, area/core, Stale
**Title:** Feature Request: Bootable USB Image for Portable Gemini CLI Environment
**Body:** What would you like to be added?
As an IT professional and power user, I frequently work on multiple computers, some of which I cannot or do
not wish to install new software on. I want to run gemini-cli from a self-contained, bootable USB drive so
that I can use its powerful capabilities for diagnostics, troubleshooting, and development on any computer
that has internet access.
Feature Description


### ISSUE-29 #14483 | - | Phase I (Jun–Dec '25) | NOT_PLANNED
https://github.com/google-gemini/gemini-cli/issues/14483 | author `kjh9211` (NONE) | created 2025-12-04 | closed 2026-03-08 | TTFR 300.8h | labels status/need-triage, priority/p1, area/security, Stale
**Title:** gemini can access root directory.
**Body:** What happened?
gemini call shell with command "cd ../ ; dir"
What did you expect to happen?
access deny
Client information

Client Information
Run gemini to enter the interactive CLI, then run the /about command.
> /about
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                        

- `jacob314` (2025-12-23): Not a P0. To completely prevent access to the root directory you must enable the sandbox. However we should be able to detect and warn about more commands like this.

### ISSUE-30 #12963 | - | Phase I (Jun–Dec '25) | DUPLICATE
https://github.com/google-gemini/gemini-cli/issues/12963 | author `Vitallity` (NONE) | created 2025-11-12 | closed 2025-11-19 | TTFR 2.2h | labels priority/p1, area/core, status/possible-duplicate
**Title:** Error: "Cannot resize a pty that has already exited"
**Body:** What happened?
Hi there!
Description
When using the Gemini CLI to interact with a Git repository on Windows, the CLI
consistently crashes when attempting to execute the git add . command via the
run_shell_command tool. The crash is accompanied by the error message "Cannot resize a
pty that has already exited". This issue prevents using the CLI for git-related
workflows.
Steps to Reproduce

Initial

- `lodela` (2025-11-12): Is there any way to return the entire context?? or I have to start again from cero??? 😡😡 thats not fair... more than 8 hours waisted... once you start again have to re-read all the freaking context-files and start to respond questions to the stupid model again and finally another freaking Gemini error... I can not trust Gemini anymore... from your side google... what an incredible marketing you do... your product sucks! thers no way to continue working with this piece of nothing... PLEASE FIXIT... it imposible to work like this. C:\Users\norberto.lodela\AppData\Roaming\nvm\v24.10.0\node_module
- `scidomino` (2025-11-19): You can save your chat with /chat save foo which will persist your context to a file that you can then load with /chat load foo.
- `Vitallity` (2025-11-19): You can save your chat with /chat save foo which will persist your context to a file that you can then load with /chat load foo.  I don't always have time to save my chats; sometimes the cli closes unexpectedly, and that's it—partially or completely lost history. Or are you suggesting I save literally every successfully received message separately?
- `scidomino` (2025-11-26): Is this fixed?  This was closed as a duplicate of #10258. Please see that bug to understand the current status.
