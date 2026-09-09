#!/usr/bin/env python3
"""Run one bounded CLI turn on Linux/macOS with Python 3.9+.

The caller supplies and verifies authentication, capabilities, and the complete argv.
This helper does not modify CLI flags or enforce sandbox/network/spending policy.
It stops the owned POSIX process group, including children surviving its leader;
new sessions and remote/detached provider work require a separate supervisor.

Exit codes: 0 succeeded (including a blocked task), 1 failed, 2 incomplete,
3 timed_out, 4 cancelled, 5 invalid_output, 64 invalid request/launch setup.
"""

import argparse
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


SKILL_VERSION = "0.2.1"
RESULT_PROTOCOL = "worker-result-v1"
EXIT_CODES = {
    "succeeded": 0, "failed": 1, "incomplete": 2,
    "timed_out": 3, "cancelled": 4, "invalid_output": 5,
}
TERM_GRACE_SECONDS = 1.0
KILL_GRACE_SECONDS = 1.0
ARRAY_FIELDS = (
    "findings", "changes", "verification", "blockers", "recommended_next_steps",
)
HANDOFF_PROPERTIES = {
    "status": {"type": "string", "enum": ["completed", "blocked", "failed"]},
    "summary": {"type": "string"},
    **{name: {"type": "array", "items": {"type": "string"}} for name in ARRAY_FIELDS},
}


class InputError(Exception):
    pass


class OutputError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise InputError(message)


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def constant(_value):
        raise ValueError("non-finite JSON number")

    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def check_schema():
    """Fail closed if the bundled fixed protocol changes; not a schema engine."""
    path = Path(__file__).resolve().parent.parent / "assets" / "result.schema.json"
    try:
        schema = strict_json(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        raise InputError("cannot read the bundled result schema") from None
    allowed = {
        "$schema", "$id", "title", "description", "type", "additionalProperties",
        "properties", "required",
    }
    if (not isinstance(schema, dict) or not set(schema).issubset(allowed)
            or schema.get("type") != "object"
            or schema.get("additionalProperties") is not False
            or schema.get("properties") != HANDOFF_PROPERTIES
            or schema.get("required") != list(HANDOFF_PROPERTIES)):
        raise InputError("bundled schema differs from supported worker-result-v1")


def validate_handoff(value):
    if not isinstance(value, dict) or set(value) != set(HANDOFF_PROPERTIES):
        raise OutputError("structured handoff has missing or unexpected fields")
    if value["status"] not in ("completed", "blocked", "failed"):
        raise OutputError("structured handoff has an invalid task status")
    if not isinstance(value["summary"], str):
        raise OutputError("structured handoff summary must be a string")
    for field in ARRAY_FIELDS:
        if (not isinstance(value[field], list)
                or any(not isinstance(item, str) for item in value[field])):
            raise OutputError("structured handoff evidence fields must be string arrays")
    return value


def events_from(text):
    if not text.strip():
        return []
    try:
        value = strict_json(text)
        if not isinstance(value, dict):
            raise OutputError("CLI output must contain JSON objects")
        return [value]
    except (ValueError, UnicodeError):
        pass
    events = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            value = strict_json(line)
        except (ValueError, UnicodeError):
            raise OutputError("CLI output contains malformed or truncated JSON") from None
        if not isinstance(value, dict):
            raise OutputError("CLI JSONL output must contain objects")
        events.append(value)
    return events


def numeric_usage(value):
    """Keep usage counters, not arbitrary text supplied in an event."""
    if not isinstance(value, dict):
        return {}
    result = {}
    for key, item in value.items():
        if isinstance(item, (int, float)) and not isinstance(item, bool):
            if isinstance(item, int) or math.isfinite(item):
                result[key] = item
        elif isinstance(item, dict):
            nested = numeric_usage(item)
            if nested:
                result[key] = nested
    return result


def benign_claude_tail(event):
    """Allow documented informational tails, never evidence of unfinished work."""
    return (event.get("type") == "prompt_suggestion"
            or event.get("type") == "system" and (
                event.get("subtype") == "session_state_changed" and event.get("state") == "idle"
                or event.get("subtype") == "task_notification" and event.get("status") == "completed"))


def parse_result(provider, events, structured):
    result = {
        "status": "incomplete", "reason": "CLI completion signal is missing",
        "completion": False, "session_id": None, "usage": {},
        "reported_models": [], "output": None, "task_status": None,
    }
    if not events:
        return result
    if provider == "claude":
        finals = [(i, event) for i, event in enumerate(events) if event.get("type") == "result"]
        if len(finals) > 1:
            raise OutputError("multiple Claude results in a bounded turn")
        if not finals:
            if any(event.get("type") == "error" for event in events):
                result.update(status="failed", reason="Claude reported an error")
            return result
        index, final = finals[0]
        session_id = final.get("session_id")
        result["session_id"] = session_id if isinstance(session_id, str) else None
        result["usage"] = numeric_usage(final.get("usage"))
        cost = final.get("total_cost_usd")
        if (isinstance(cost, (int, float)) and not isinstance(cost, bool)
                and (isinstance(cost, int) or math.isfinite(cost))):
            result["usage"]["total_cost_usd"] = cost
        models = {event["model"] for event in events if isinstance(event.get("model"), str)}
        model_usage = final.get("modelUsage")
        if isinstance(model_usage, dict):
            models.update(model_usage)
        result["reported_models"] = sorted(models)
        subtype = final.get("subtype")
        if (final.get("is_error") is True or isinstance(subtype, str) and subtype.startswith("error")
                or any(event.get("type") == "error" for event in events)):
            result.update(status="failed", reason="Claude reported a failed turn")
            return result
        if any(not benign_claude_tail(event) for event in events[index + 1:]):
            result["reason"] = "Claude result was followed by further events"
            return result
        if final.get("subtype") != "success" or final.get("is_error") is not False:
            result["reason"] = "Claude success was not confirmed"
            return result
        terminal = final.get("terminal_reason")
        stop = final.get("stop_reason")
        result["terminal_reason"] = terminal if isinstance(terminal, str) else None
        result["stop_reason"] = stop if isinstance(stop, str) else None
        if (terminal not in (None, "completed")
                or stop in ("max_tokens", "model_context_window_exceeded")):
            result["reason"] = "Claude returned before the task finished"
            return result
        output = final.get("structured_output") if structured else final.get("result")
    else:
        starts = [event for event in events if event.get("type") == "thread.started"]
        finals = [(i, event) for i, event in enumerate(events) if event.get("type") == "turn.completed"]
        if (len(starts) > 1 or len(finals) > 1
                or sum(event.get("type") == "turn.started" for event in events) > 1):
            raise OutputError("multiple Codex threads or turns in a bounded invocation")
        if starts and isinstance(starts[0].get("thread_id"), str):
            result["session_id"] = starts[0]["thread_id"]
        if finals:
            result["usage"] = numeric_usage(finals[0][1].get("usage"))
        result["reported_models"] = sorted({
            event["model"] for event in events if isinstance(event.get("model"), str)
        })
        if any(event.get("type") in ("turn.failed", "error") for event in events):
            result.update(status="failed", reason="Codex reported a failed turn")
            return result
        if not result["session_id"] or not finals:
            return result
        final_index = finals[0][0]
        messages = [
            (i, event["item"]) for i, event in enumerate(events)
            if event.get("type") == "item.completed" and isinstance(event.get("item"), dict)
            and event["item"].get("type") == "agent_message"
        ]
        if not messages:
            result["reason"] = "Codex completed without a final agent message"
            return result
        if final_index != len(events) - 1:
            result["reason"] = "Codex activity continued after turn completion"
            return result
        if events.index(starts[0]) >= messages[-1][0]:
            result["reason"] = "Codex message precedes its thread start"
            return result
        output = messages[-1][1].get("text")
    result["completion"] = True
    try:
        if structured:
            if provider == "codex":
                if not isinstance(output, str):
                    raise OutputError("Codex structured output must be JSON text")
                try:
                    output = strict_json(output)
                except (ValueError, UnicodeError):
                    raise OutputError("Codex final message is not valid handoff JSON") from None
            output = validate_handoff(output)
            result["task_status"] = output["status"]
        elif not isinstance(output, str) or not output.strip():
            raise OutputError("CLI completed without a nonempty text result")
        elif not structured:
            try:
                output.encode("utf-8")
            except UnicodeError:
                raise OutputError("CLI text result contains invalid Unicode") from None
    except OutputError as error:
        result.update(status="invalid_output", reason=str(error))
        return result
    result.update(status="succeeded", reason="CLI turn and result completed", output=output)
    return result


def group_exists(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def signal_group(pgid, signum):
    try:
        os.killpg(pgid, signum)
    except ProcessLookupError:
        pass


def stop_group(process):
    signal_group(process.pid, signal.SIGTERM)
    for signum, grace in ((None, TERM_GRACE_SECONDS), (signal.SIGKILL, KILL_GRACE_SECONDS)):
        if signum is not None:
            signal_group(process.pid, signum)
        until = time.monotonic() + grace
        while time.monotonic() < until:
            process.poll()  # Reap the leader so it cannot keep the group alive as a zombie.
            if not group_exists(process.pid):
                return "stopped"
            time.sleep(0.025)
    process.poll()
    return "unconfirmed" if group_exists(process.pid) else "stopped"


def private_file(path):
    descriptor = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    return os.fdopen(descriptor, "wb")


def write_private(path, text):
    data = text.encode("utf-8")
    with private_file(path) as output:
        output.write(data)


def execute(argv, cwd, timeout, prompt, out_path, err_path):
    cancellation = []
    previous = {}
    process = None
    start = time.monotonic()

    def cancelled(signum, _frame):
        if not cancellation:
            cancellation.append(signum)

    try:
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous[signum] = signal.signal(signum, cancelled)
        with private_file(out_path) as stdout, private_file(err_path) as stderr:
            try:
                process = subprocess.Popen(
                    argv, cwd=cwd, stdin=prompt, stdout=stdout, stderr=stderr,
                    shell=False, start_new_session=True,
                )
            except OSError as error:
                raise InputError("cannot launch executable: " + type(error).__name__) from None
            status, reason = None, None
            while process.poll() is None:
                if cancellation:
                    status, reason = "cancelled", "supervisor received a cancellation signal"
                    break
                if time.monotonic() - start >= timeout:
                    status, reason = "timed_out", "wall-clock deadline reached"
                    break
                time.sleep(min(0.025, max(0.0, timeout - (time.monotonic() - start))))
            if cancellation:
                status, reason = "cancelled", "supervisor received a cancellation signal"
            cleanup = "not_needed"
            if group_exists(process.pid):
                if status is None:
                    status, reason = "incomplete", "worker exited with same-group child work still running"
                cleanup = stop_group(process)
            exit_code = process.poll()
            return {
                "runtime_status": status, "reason": reason, "exit_code": exit_code,
                "duration_seconds": round(time.monotonic() - start, 3),
                "process_group_cleanup": cleanup,
                "cancellation_signal": cancellation[0] if cancellation else None,
            }
    finally:
        if process is not None and group_exists(process.pid):
            signal_group(process.pid, signal.SIGKILL)
            process.poll()
        for signum, handler in previous.items():
            signal.signal(signum, handler)


def arguments():
    parser = Parser(description=__doc__)
    parser.add_argument("--provider", required=True, choices=("claude", "codex"))
    parser.add_argument("--argv-file", required=True, type=Path)
    parser.add_argument("--cwd", required=True, type=Path)
    parser.add_argument("--timeout", required=True, type=float)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--prompt-file", type=Path)
    parser.add_argument("--structured", action="store_true")
    parser.add_argument("--cli-version")
    parser.add_argument("--model")
    parser.add_argument("--effort")
    args = parser.parse_args()
    if os.name != "posix" or not (sys.platform == "darwin" or sys.platform.startswith("linux")):
        raise InputError("bounded process-group execution is supported only on Linux and macOS")
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        raise InputError("--timeout must be positive and finite")
    try:
        argv = strict_json(args.argv_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        raise InputError("--argv-file must contain a readable JSON argument array") from None
    if (not isinstance(argv, list) or not argv
            or any(not isinstance(item, str) or "\0" in item for item in argv)):
        raise InputError("argv must be a nonempty array of strings without NUL bytes")
    try:
        for item in argv:
            item.encode("utf-8")
    except UnicodeError:
        raise InputError("argv strings must contain valid Unicode") from None
    executable = Path(argv[0])
    if not executable.is_absolute() or not executable.is_file() or not os.access(executable, os.X_OK):
        raise InputError("argv[0] must be an absolute path to an executable file")
    try:
        args.cwd = args.cwd.resolve(strict=True)
    except OSError:
        raise InputError("--cwd must be an existing directory") from None
    if not args.cwd.is_dir():
        raise InputError("--cwd must be an existing directory")
    if args.structured:
        check_schema()
    args.output_dir = Path(os.path.abspath(args.output_dir))
    return args, argv


def run():
    args, argv = arguments()
    try:
        prompt = args.prompt_file.open("rb") if args.prompt_file else sys.stdin.buffer
    except OSError:
        raise InputError("--prompt-file must be readable") from None
    try:
        try:
            args.output_dir.mkdir(mode=0o700)
        except FileExistsError:
            raise InputError("--output-dir already exists; choose a new path") from None
        except OSError:
            raise InputError("cannot create --output-dir; its parent must exist and be writable") from None
        paths = {name: args.output_dir / filename for name, filename in (
            ("stdout", "stdout.txt"), ("stderr", "stderr.txt"), ("manifest", "run.json"),
        )}
        manifest = {
            "skill_version": SKILL_VERSION, "result_protocol": RESULT_PROTOCOL,
            "provider": args.provider, "cwd": str(args.cwd), "timeout_seconds": args.timeout,
            "requested": {key: value for key, value in (
                ("cli_version", args.cli_version), ("model", args.model), ("effort", args.effort),
            ) if value is not None},
            "task_status": None, "completion": False, "session_id": None,
            "usage": {}, "reported_models": [], "terminal_reason": None, "stop_reason": None,
        }
        try:
            manifest.update(execute(argv, str(args.cwd), args.timeout, prompt, paths["stdout"], paths["stderr"]))
        except InputError as error:
            manifest.update(runtime_status="failed", reason=str(error), exit_code=None,
                            duration_seconds=0, process_group_cleanup="not_needed")
            code = 64
        else:
            try:
                parsed = parse_result(args.provider, events_from(paths["stdout"].read_text(encoding="utf-8")), args.structured)
            except (OutputError, UnicodeError) as error:
                parsed = {"status": "invalid_output", "reason": str(error) if isinstance(error, OutputError)
                          else "CLI output is not UTF-8", "output": None}
            for key in ("task_status", "completion", "session_id", "usage", "reported_models", "terminal_reason", "stop_reason"):
                if key in parsed:
                    manifest[key] = parsed[key]
            if manifest["runtime_status"] is None:
                if manifest["exit_code"] != 0:
                    manifest.update(runtime_status="failed", reason="CLI process exited unsuccessfully")
                else:
                    manifest.update(runtime_status=parsed["status"], reason=parsed["reason"])
            if parsed.get("output") is not None:
                paths["result"] = args.output_dir / ("result.json" if args.structured else "result.txt")
                content = (json.dumps(parsed["output"], indent=2) + "\n"
                           if args.structured else parsed["output"])
                write_private(paths["result"], content)
            code = EXIT_CODES[manifest["runtime_status"]]
        manifest["artifacts"] = {key: str(path) for key, path in paths.items()}
        write_private(paths["manifest"], json.dumps(manifest, indent=2) + "\n")
        print(json.dumps(manifest, separators=(",", ":")))
        return code
    finally:
        if args.prompt_file:
            prompt.close()


def main():
    try:
        return run()
    except (InputError, OSError) as error:
        reason = str(error) if isinstance(error, InputError) else "runner filesystem operation failed: " + type(error).__name__
        print(json.dumps({"runtime_status": "failed", "reason": reason}, separators=(",", ":")))
        return 64


if __name__ == "__main__":
    sys.exit(main())
