#!/usr/bin/env python3
"""Structural validator for this Agent Plugins 1.0 marketplace.

Checks the portable Agent Plugins 1.0 contract (root plugin.json + skills/ + mcp.json)
plus the three distribution manifests Claude Code/Cursor/Codex read.
Stdlib only. Exit code 0 = all checks passed.

Usage: python3 scripts/validate.py [repo_root]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SPEC = "1.0.0"
PLUGIN_SCHEMA = f"https://agent-plugins.org/schemas/{SPEC}/plugin.schema.json"
MCP_SCHEMA = f"https://agent-plugins.org/schemas/{SPEC}/mcp.schema.json"

PLUGIN_FIELDS = {
    "$schema", "name", "version", "description", "author",
    "homepage", "repository", "license", "keywords", "extensions",
}
MCP_FIELDS = {"$schema", "mcpServers"}
NAME_RE = re.compile(r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$")

failures: list[str] = []
checks = 0


def check(cond: bool, msg: str) -> bool:
    global checks
    checks += 1
    if not cond:
        failures.append(msg)
    return cond


def load_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        failures.append(f"{path}: invalid JSON ({exc})")
        return None
    if not isinstance(data, dict):
        failures.append(f"{path}: top level is not an object")
        return None
    return data


def check_name(value: object, where: str) -> None:
    ok = isinstance(value, str) and 1 <= len(value) <= 64 and bool(NAME_RE.match(value))
    if ok:
        ok = "--" not in value and ".." not in value
    check(ok, f"{where}: invalid plugin name {value!r} (1-64 chars, [a-z0-9.-], alnum ends, no '--'/'..')")


def check_path(raw: object, where: str, root: Path) -> Path | None:
    if not isinstance(raw, str) or not raw.startswith("./"):
        failures.append(f"{where}: source must be a './'-prefixed relative path, got {raw!r}")
        return None
    if ".." in Path(raw).parts:
        failures.append(f"{where}: source contains '..' ({raw})")
        return None
    resolved = (root / raw).resolve()
    if not str(resolved).startswith(str(root.resolve())):
        failures.append(f"{where}: source escapes marketplace root ({raw})")
        return None
    check(resolved.is_dir(), f"{where}: source directory does not exist ({raw})")
    return resolved


def frontmatter(path: Path) -> dict | None:
    text = path.read_text()
    if not text.startswith("---\n"):
        failures.append(f"{path}: SKILL.md missing YAML frontmatter")
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        failures.append(f"{path}: SKILL.md frontmatter not terminated")
        return None
    block = text[4:end]
    data: dict[str, str] = {}
    key = None
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            data[key] = val.strip()
        elif key == "description" and line.strip():
            data[key] = (data[key] + " " + line.strip()).strip()
    return data


def check_plugin(plugin_dir: Path, entry_name: str) -> None:
    where = plugin_dir.name
    manifest_path = plugin_dir / "plugin.json"
    if not check(manifest_path.is_file(), f"{where}: missing root plugin.json"):
        return
    manifest = load_json(manifest_path)
    if manifest is None:
        return

    unknown = set(manifest) - PLUGIN_FIELDS
    check(not unknown, f"{where}/plugin.json: unknown top-level fields {sorted(unknown)} (schema is closed)")

    check(manifest.get("$schema") == PLUGIN_SCHEMA,
          f"{where}/plugin.json: $schema must be {PLUGIN_SCHEMA}")
    check_name(manifest.get("name"), f"{where}/plugin.json")
    check(manifest.get("name") == entry_name,
          f"{where}/plugin.json: name {manifest.get('name')!r} != marketplace entry {entry_name!r}")
    check(isinstance(manifest.get("version"), str) and manifest["version"],
          f"{where}/plugin.json: version must be a non-empty string")
    check(isinstance(manifest.get("description"), str) and manifest["description"],
          f"{where}/plugin.json: description must be a non-empty string")

    author = manifest.get("author")
    if author is not None:
        check(isinstance(author, dict), f"{where}/plugin.json: author must be an object")
        if isinstance(author, dict):
            check(set(author) <= {"name", "email", "url"},
                  f"{where}/plugin.json: author allows only name/email/url, got {sorted(author)}")
            check(isinstance(author.get("name"), str) and author.get("name"),
                  f"{where}/plugin.json: author.name required")
    check(isinstance(manifest.get("keywords", []), list), f"{where}/plugin.json: keywords must be an array")

    # Inline components are not allowed by the portable manifest.
    for forbidden in ("skills", "mcpServers", "commands", "hooks", "agents"):
        check(forbidden not in manifest, f"{where}/plugin.json: '{forbidden}' is not a portable field")

    # skills/ — each immediate child dir containing SKILL.md is one skill.
    skills_dir = plugin_dir / "skills"
    if skills_dir.is_dir():
        skill_dirs = [p for p in sorted(skills_dir.iterdir()) if p.is_dir()]
        check(bool(skill_dirs), f"{where}/skills: directory present but empty")
        for sd in skill_dirs:
            sm = sd / "SKILL.md"
            if not check(sm.is_file(), f"{where}/skills/{sd.name}: missing SKILL.md"):
                continue
            fm = frontmatter(sm)
            if fm is None:
                continue
            check(fm.get("name") == sd.name,
                  f"{where}/skills/{sd.name}: frontmatter name {fm.get('name')!r} != directory name")
            check(bool(fm.get("description")), f"{where}/skills/{sd.name}: frontmatter description required")
        print(f"  {where}: {len(skill_dirs)} skill(s) — {', '.join(p.name for p in skill_dirs)}")

    # mcp.json — closed schema, one transport variant per server.
    mcp_path = plugin_dir / "mcp.json"
    if mcp_path.is_file():
        mcp = load_json(mcp_path)
        if mcp is not None:
            check(set(mcp) <= MCP_FIELDS, f"{where}/mcp.json: unknown top-level fields {sorted(set(mcp) - MCP_FIELDS)}")
            check(mcp.get("$schema") == MCP_SCHEMA, f"{where}/mcp.json: $schema must be {MCP_SCHEMA}")
            servers = mcp.get("mcpServers")
            if check(isinstance(servers, dict), f"{where}/mcp.json: mcpServers must be an object"):
                for sname, server in servers.items():
                    _check_server(where, sname, server)

    # Client shims must exist and agree on the plugin name.
    for shim in (".claude-plugin/plugin.json", ".cursor-plugin/plugin.json"):
        shim_path = plugin_dir / shim
        if check(shim_path.is_file(), f"{where}: missing {shim} shim"):
            shim_data = load_json(shim_path) or {}
            check(shim_data.get("name") == entry_name, f"{where}/{shim}: name must equal {entry_name!r}")


def _check_server(where: str, sname: str, server: object) -> None:
    label = f"{where}/mcp.json[{sname}]"
    if not isinstance(server, dict):
        failures.append(f"{label}: server config must be an object")
        return
    kind = server.get("type")
    allowed = {
        "stdio": {"type", "command", "args", "env", "cwd"},
        "streamable-http": {"type", "url", "headers"},
        "sse": {"type", "url", "headers"},
    }
    if not check(kind in allowed, f"{label}: unknown transport type {kind!r}"):
        return
    extra = set(server) - allowed[kind]
    check(not extra, f"{label}: fields {sorted(extra)} do not belong to the '{kind}' variant")

    if kind == "stdio":
        cmd = server.get("command")
        check(isinstance(cmd, str) and cmd and ("/" not in cmd or cmd.startswith("./")),
              f"{label}: command must be a bare executable or './'-relative path")
        return

    url = server.get("url")
    if not check(isinstance(url, str) and url.startswith(("http://", "https://")), f"{label}: url must be absolute http(s)"):
        return
    check("#" not in url, f"{label}: url must not contain a fragment")
    check("@" not in url.split("://", 1)[1].split("/", 1)[0], f"{label}: url must not contain user information")
    host = url.split("://", 1)[1].split("/", 1)[0].split(":")[0]
    if host not in {"localhost", "127.0.0.1", "::1"}:
        check(url.startswith("https://"), f"{label}: non-loopback url must use https")
    headers = server.get("headers", {})
    check(isinstance(headers, dict), f"{label}: headers must be an object")
    if isinstance(headers, dict):
        check(len({h.lower() for h in headers}) == len(headers), f"{label}: duplicate header names (case-insensitive)")
        print(f"  {where}: MCP {sname} -> {url}")


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent).resolve()
    print(f"Validating {root} against Agent Plugins {SPEC}\n")

    manifests = {
        "claude": root / ".claude-plugin/marketplace.json",
        "cursor": root / ".cursor-plugin/marketplace.json",
        "codex": root / ".agents/plugins/marketplace.json",
    }
    entries: dict[str, str] = {}

    for client, path in manifests.items():
        if not check(path.is_file(), f"missing {path.relative_to(root)}"):
            continue
        data = load_json(path)
        if data is None:
            continue
        check(isinstance(data.get("name"), str) and data["name"], f"{path.name} ({client}): name required")
        plugins = data.get("plugins")
        if not check(isinstance(plugins, list) and plugins, f"{client}: plugins[] required and non-empty"):
            continue
        print(f"{client}: marketplace {data.get('name')!r}, {len(plugins)} plugin(s)")
        seen: set[str] = set()
        for i, entry in enumerate(plugins):
            if not check(isinstance(entry, dict), f"{client}: plugins[{i}] must be an object"):
                continue
            name = entry.get("name")
            check_name(name, f"{client}: plugins[{i}].name")
            # Codex marketplace entries use policy/category; description is optional there.
            if client != "codex":
                check(bool(entry.get("description")), f"{client}: plugins[{i}] description recommended")
            check(name not in seen, f"{client}: duplicate plugin entry {name!r}")
            seen.add(name)
            src = entry.get("source")
            if isinstance(src, dict):
                check(src.get("source") in {"local", "url", "git-subdir", "github", "npm", "archive"},
                      f"{client}: plugins[{i}].source.source unknown")
                src_path = src.get("path")
            elif client == "cursor" and isinstance(src, str) and not src.startswith("./"):
                src_path = "./" + src
            else:
                src_path = src
            resolved = check_path(src_path, f"{client}: plugins[{i}].source", root)
            if resolved:
                prev = entries.get(name)
                check(prev in (None, str(resolved)),
                      f"{client}: plugin {name!r} resolves to conflicting paths")
                entries[name] = str(resolved)

    for name, path in sorted(entries.items()):
        print()
        check_plugin(Path(path), name)

    total = checks
    print()
    if failures:
        print(f"FAILED — {len(failures)} problem(s) across {total} checks:")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print(f"PASS — {total} checks, {len(entries)} plugin(s), Agent Plugins {SPEC} conformant")
    return 0


if __name__ == "__main__":
    sys.exit(main())
