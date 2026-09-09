# Evaluating the meta-agent skills

The deterministic suite uses local fake CLIs; it never calls a model, reads credentials, or
mutates an external system:

```sh
python3 -m unittest discover -s tests -v
```

It exercises both packaged helpers through their command-line interface. It checks literal
prompt transport, private logs, provider completion/failure signals, invalid structured
handoffs, interrupted output, deadlines, cancellation, and cleanup of same-group children
without killing unrelated processes. Packaging checks cover versions, shared files, and links.
Run on macOS/Linux with Python 3.9+. Windows runs packaging checks and skips POSIX lifecycle tests.

These fixtures test execution mechanics, not provider access or model quality. For a real
provider run, first establish authorization, route-specific authentication, compatible CLI
controls, and a bounded task/usage budget. Do not make paid calls as part of installation or
routine structural validation. Live tests require deliberately choosing that evaluation mode;
they are not triggered by the command above.

## Fresh-context behavior

Use `scenarios.json` as an evaluation menu. Give an independent agent only the realistic
request, selected skill, raw fixture inputs, and permitted resources. Do not supply the expected
checks or suspected failure to that agent; the evaluator uses them after inspecting its actions.
Use disposable workspaces and synthetic files, never private repositories or credentials.

For an implementation fixture, provide a small program with an observable failing test plus
an unrelated user-edited notes file. For resume, provide two fake session records and the
captured intended ID. Label dry-run selection tests separately from live CLI resume tests.
When using fake CLIs, explicitly identify them as test doubles and judge execution mechanics
without pretending they establish real authentication, model access, or sandbox enforcement.

Compare the same tasks with no skill, the current skill, and the candidate revision in fresh
contexts. Record skill commit/version, host/worker models and effort, CLI/platform, successful
acceptance checks, unintended actions, time, tool calls, retries, usage when available, and
parent correction effort. Do not report invented costs when a host does not expose usage.
Repeat consequential cases to distinguish a regression from normal model variation. Practitioner
reports suggest cases to test; they do not establish a default for this user's workloads.

Promote a change when observed outcomes justify it. Do not infer improvement from shorter files,
preferred wording, a structural validator, or one successful trial. Keep raw temporary artifacts
out of the repository; checked-in reports contain only synthetic outcomes and limitations.
