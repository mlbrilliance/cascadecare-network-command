"""
Case Repository Protocol Contracts
===================================
Defines the interfaces (Python Protocols) that the ORM implementation must satisfy.
Downstream slices (shim, agents, UI data layer) depend on these contracts, not
on concrete SQLAlchemy model classes.

This file is a SPECIFICATION artifact — it lives in specs/002-case-schema/contracts/
and is NOT imported by production code directly. The concrete implementation in
src/cascadecare/db/repositories/ MUST satisfy these Protocols.

Usage in type checking:
    from cascadecare.db.repositories.case import CaseRepositoryImpl
    repo: CaseRepository = CaseRepositoryImpl(session)  # mypy validates conformance
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Value objects (data classes — no ORM dependency)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MasterCaseRecord:
    id: uuid.UUID
    title: str
    goal: str
    status: str          # "open" | "in_progress" | "escalated" | "closed"
    reversal_count: int
    current_reversal: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ParentCaseRecord:
    id: uuid.UUID
    master_case_id: uuid.UUID
    stakeholder_name: str
    stakeholder_type: str   # "provider" | "payer" | "vendor"
    goal: str
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class GrandchildCaseRecord:
    id: uuid.UUID
    parent_case_id: uuid.UUID
    grandchild_type: str    # "baa_obligation" | "regulator_compliance" | "investigation"
    obligation_id: str
    status: str
    privilege_flag: str | None   # "attorney_client" | "work_product" | None
    response_deadline: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class CaseStateEventRecord:
    id: uuid.UUID
    case_id: uuid.UUID
    case_level: str          # "master" | "parent" | "grandchild"
    previous_status: str
    new_status: str
    triggered_by: str
    note: str | None
    occurred_at: datetime


@dataclass(frozen=True)
class CaseHierarchyRecord:
    """Full three-level hierarchy returned by a single traversal query."""
    master: MasterCaseRecord
    parents: list[ParentCaseRecord]
    grandchildren: dict[uuid.UUID, list[GrandchildCaseRecord]]
    # grandchildren keyed by parent_case_id


# ---------------------------------------------------------------------------
# Repository Protocols
# ---------------------------------------------------------------------------

@runtime_checkable
class MasterCaseRepository(Protocol):
    """Manages MasterCrisisCase persistence."""

    async def create(
        self,
        *,
        title: str,
        goal: str,
    ) -> MasterCaseRecord:
        """Create a new master crisis case with status=open."""
        ...

    async def get(self, case_id: uuid.UUID) -> MasterCaseRecord | None:
        """Return master case by ID, or None if not found."""
        ...

    async def update_status(
        self,
        case_id: uuid.UUID,
        *,
        new_status: str,
        triggered_by: str,
        note: str | None = None,
    ) -> MasterCaseRecord:
        """
        Transition case status. Writes a CaseStateEvent in the same transaction.
        Raises ValueError for invalid status transitions.
        """
        ...

    async def update_goal(
        self,
        case_id: uuid.UUID,
        *,
        new_goal: str,
        reversal_description: str,
    ) -> MasterCaseRecord:
        """Record a goal reversal. Increments reversal_count."""
        ...


@runtime_checkable
class ParentCaseRepository(Protocol):
    """Manages ParentCase persistence."""

    async def create(
        self,
        *,
        master_case_id: uuid.UUID,
        stakeholder_name: str,
        stakeholder_type: str,
        goal: str,
    ) -> ParentCaseRecord:
        """
        Create a parent case. Raises ValueError if master case is closed.
        Raises LookupError if master case does not exist.
        """
        ...

    async def get(self, case_id: uuid.UUID) -> ParentCaseRecord | None: ...

    async def list_by_master(
        self, master_case_id: uuid.UUID
    ) -> list[ParentCaseRecord]:
        """Return all parent cases under a given master, ordered by created_at."""
        ...

    async def update_status(
        self,
        case_id: uuid.UUID,
        *,
        new_status: str,
        triggered_by: str,
        note: str | None = None,
    ) -> ParentCaseRecord: ...


@runtime_checkable
class GrandchildCaseRepository(Protocol):
    """Manages GrandchildCase persistence."""

    async def create(
        self,
        *,
        parent_case_id: uuid.UUID,
        grandchild_type: str,
        obligation_id: str,
        privilege_flag: str | None = None,
        response_deadline: datetime | None = None,
    ) -> GrandchildCaseRecord:
        """
        Create a grandchild case.
        Raises ValueError if parent case is closed.
        Raises LookupError if parent case does not exist.
        """
        ...

    async def get(self, case_id: uuid.UUID) -> GrandchildCaseRecord | None: ...

    async def list_by_parent(
        self, parent_case_id: uuid.UUID
    ) -> list[GrandchildCaseRecord]:
        """Return all grandchild cases under a given parent, ordered by created_at."""
        ...

    async def update_status(
        self,
        case_id: uuid.UUID,
        *,
        new_status: str,
        triggered_by: str,
        note: str | None = None,
    ) -> GrandchildCaseRecord: ...


@runtime_checkable
class HierarchyRepository(Protocol):
    """Traversal queries spanning multiple levels."""

    async def get_full_hierarchy(
        self, master_case_id: uuid.UUID
    ) -> CaseHierarchyRecord | None:
        """
        Single-query traversal returning master + all parents + all grandchildren.
        Returns None if master case does not exist.
        Must complete in <500 ms for the demo dataset.
        """
        ...

    async def get_ancestor_chain(
        self, case_id: uuid.UUID, case_level: str
    ) -> dict[str, Any]:
        """
        Return the full ancestor chain for any case.
        For grandchild: {grandchild: ..., parent: ..., master: ...}
        For parent:     {parent: ..., master: ...}
        For master:     {master: ...}
        """
        ...

    async def list_by_type_and_status(
        self,
        *,
        case_level: str,
        status: str | None = None,
        case_type: str | None = None,
    ) -> list[MasterCaseRecord | ParentCaseRecord | GrandchildCaseRecord]:
        """Cross-type query by status and/or subtype."""
        ...
