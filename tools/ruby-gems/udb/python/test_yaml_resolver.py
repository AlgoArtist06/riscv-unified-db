# SPDX-FileCopyrightText: Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
# SPDX-FileCopyrightText: 2024-2025 Contributors to the RISCV UnifiedDB <https://github.com/riscv/riscv-unified-db>
# SPDX-License-Identifier: BSD-3-Clause-Clear

import pytest
import yaml_resolver
from yaml_resolver import resolve


@pytest.fixture(autouse=True)
def _clear_resolve_cache():
    """resolve() memoizes by relative path, so isolate each test."""
    yaml_resolver.resolved_objs.clear()


def _make_arch(tmp_path, inherits_target):
    arch_root = tmp_path / "arch"
    (arch_root / "ext").mkdir(parents=True)
    (tmp_path / "outside").mkdir()
    (tmp_path / "outside" / "secrets.yaml").write_text('name: secrets\nsecret: "s3cret"\n')
    (arch_root / "ext" / "Evil.yaml").write_text(f'name: Evil\n$inherits: "{inherits_target}"\n')
    return arch_root


def test_inherits_rejects_relative_path_escaping_arch_root(tmp_path):
    arch_root = _make_arch(tmp_path, "../outside/secrets.yaml#")

    with pytest.raises(ValueError, match="escapes"):
        resolve("ext/Evil.yaml", arch_root, False, False)


def test_inherits_rejects_absolute_path(tmp_path):
    arch_root = _make_arch(tmp_path, f"{tmp_path / 'outside' / 'secrets.yaml'}#")

    with pytest.raises(ValueError, match="escapes"):
        resolve("ext/Evil.yaml", arch_root, False, False)


def test_inherits_still_resolves_targets_inside_arch_root(tmp_path):
    arch_root = tmp_path / "arch"
    (arch_root / "ext").mkdir(parents=True)
    (arch_root / "ext" / "Base.yaml").write_text("name: Base\nfoo: 1\n")
    (arch_root / "ext" / "Child.yaml").write_text(
        'name: Child\n$inherits: "ext/Base.yaml#"\nbar: 2\n'
    )

    resolved = resolve("ext/Child.yaml", arch_root, False, False)

    assert resolved["foo"] == 1
    assert resolved["bar"] == 2
