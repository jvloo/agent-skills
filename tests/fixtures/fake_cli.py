"""Local protocol fixture: never calls a provider or reads credentials."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


def emit(provider, text, scenario):
    if provider == "claude":
        event = {
            "type": "result", "subtype": "success", "is_error": False,
            "session_id": "test-session", "result": text,
            "usage": {"input_tokens": 3, "output_tokens": 4},
        }
        if scenario.startswith("structured"):
            event["structured_output"] = json.loads(text)
        if scenario == "failure":
            event.update(subtype="error_max_budget_usd", is_error=True)
        if scenario == "missing_completion":
            event = {"type": "assistant", "message": {"content": text}}
        if scenario in ("aborted_tools", "aborted_streaming", "tool_deferred", "hook_stopped", "background_requested", "completed"):
            event["terminal_reason"] = scenario
        if scenario == "max_tokens":
            event["stop_reason"] = "max_tokens"
        if scenario == "stream":
            print(json.dumps({"type": "system", "subtype": "init", "session_id": "test-session"}))
        print(json.dumps(event), flush=True)
    else:
        print(json.dumps({"type": "thread.started", "thread_id": "test-session"}))
        print(json.dumps({"type": "turn.started"}))
        print(json.dumps({"type": "item.completed", "item": {
            "id": "message-1", "type": "agent_message", "text": text,
        }}))
        if scenario == "failure":
            print(json.dumps({"type": "turn.failed", "error": {"message": "fixture failure"}}))
        elif scenario != "missing_completion":
            print(json.dumps({"type": "turn.completed", "usage": {"input_tokens": 3, "output_tokens": 4}}))
        sys.stdout.flush()


def main():
    scenario, provider = sys.argv[1:3]
    if scenario == "child":
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        Path(sys.argv[3]).write_text(str(os.getpid()))
        while True:
            time.sleep(0.1)
    prompt = sys.stdin.read()
    print("fixture diagnostic", file=sys.stderr, flush=True)
    if scenario in ("timeout", "cancel", "leftover_child"):
        child = subprocess.Popen([sys.executable, __file__, "child", provider, sys.argv[3]])
        for _ in range(200):
            if Path(sys.argv[3]).exists():
                break
            time.sleep(0.01)
        print(json.dumps({"type": "fixture.partial", "child_pid": child.pid}), flush=True)
        if scenario == "leftover_child":
            emit(provider, "parent finished", "success")
            return
        while True:
            time.sleep(0.1)
    text = prompt
    if scenario.startswith("structured"):
        result = {"status": "blocked", "summary": "Need fixture input", "findings": [],
                  "changes": [], "verification": [], "blockers": ["Missing input"],
                  "recommended_next_steps": []}
        if scenario == "structured_extra":
            result["extra"] = True
        elif scenario == "structured_missing":
            del result["summary"]
        elif scenario == "structured_wrong_type":
            result["findings"] = "not an array"
        text = json.dumps(result)
    emit(provider, text, scenario)
    if scenario == "suggestion_tail":
        print(json.dumps({"type": "prompt_suggestion", "suggestion": "Read next file",
                          "uuid": "suggestion-1", "session_id": "test-session"}))
    if scenario in ("idle_tail", "running_tail", "requires_action_tail"):
        print(json.dumps({"type": "system", "subtype": "session_state_changed",
                          "state": scenario.removesuffix("_tail"), "uuid": "state-1", "session_id": "test-session"}))
    if scenario in ("task_completed_tail", "task_failed_tail", "task_stopped_tail"):
        print(json.dumps({"type": "system", "subtype": "task_notification", "task_id": "task-1",
                          "status": scenario.split("_")[1], "output_file": "fixture-output.txt",
                          "summary": "fixture notification", "uuid": "notification-1", "session_id": "test-session"}))
    if scenario == "tool_tail":
        if provider == "claude":
            print(json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "id": "tool-1", "name": "Read", "input": {"file_path": "next.txt"}}
            ]}}))
        else:
            print(json.dumps({"type": "item.started", "item": {
                "id": "command-1", "type": "command_execution", "status": "in_progress", "command": "echo next"
            }}))
    if scenario == "truncated":
        sys.stdout.write('{"type":')
    if scenario == "nonzero":
        raise SystemExit(7)


if __name__ == "__main__":
    main()
