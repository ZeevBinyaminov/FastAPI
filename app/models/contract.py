from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    bytecode: Mapped[str] = mapped_column(Text, nullable=False)
    prediction: Mapped[int] = mapped_column(Integer, nullable=False)
    processing_time_ms: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    metadata_rel: Mapped["ContractMetadata"] = relationship(
        back_populates="contract_rel", uselist=False, cascade="all, delete-orphan"
    )


class ContractMetadata(Base):
    __tablename__ = "contract_metadata"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    total_instructions: Mapped[int]
    unique_instructions: Mapped[int]
    block_dependent_count: Mapped[int]
    block_dependency_index: Mapped[float]
    has_TIMESTAMP: Mapped[int]
    has_NUMBER: Mapped[int]
    has_DIFFICULTY: Mapped[int]
    has_GASLIMIT: Mapped[int]
    has_COINBASE: Mapped[int]
    has_BLOCKHASH: Mapped[int]
    environmental_instructions_count: Mapped[int]
    environmental_ratio: Mapped[float]
    unique_environmental_ops: Mapped[int]
    environmental_complexity: Mapped[float]
    balance_operations: Mapped[int]
    address_operations: Mapped[int]
    caller_operations: Mapped[int]
    origin_operations: Mapped[int]
    callvalue_operations: Mapped[int]
    external_dependency_index: Mapped[float]
    calldata_size_ops: Mapped[int]
    calldata_load_ops: Mapped[int]
    calldata_copy_ops: Mapped[int]
    total_calldata_ops: Mapped[int]
    calldata_density: Mapped[float]
    external_call_count: Mapped[int]
    has_external_calls: Mapped[int]
    call_value_ops: Mapped[int]
    call_gas_limit_ops: Mapped[int]
    potential_reentrancy_pattern: Mapped[int]
    reads_from_memory: Mapped[int]
    writes_to_memory: Mapped[int]
    memory_access_ratio: Mapped[float]
    pushes: Mapped[int]
    pops: Mapped[int]
    stack_imbalance: Mapped[int]
    stack_operations_ratio: Mapped[float]
    stack_underflow_risk: Mapped[int]
    total_gas_cost: Mapped[float]
    avg_gas_per_instruction: Mapped[float]
    max_gas_instruction: Mapped[float]
    high_gas_instructions: Mapped[int]
    gas_dos_risk_index: Mapped[float]
    arithmetic_ops_count: Mapped[int]
    arithmetic_density: Mapped[float]
    unsafe_arithmetic_pattern: Mapped[int]
    control_flow_ops: Mapped[int]
    jumpi_count: Mapped[int]
    conditional_branching_ratio: Mapped[float]
    control_flow_complexity: Mapped[float]
    caller_based_checks: Mapped[int]
    origin_usage: Mapped[int]
    access_control_ratio: Mapped[float]
    uses_origin_instead_caller: Mapped[int]
    balance_before_external_call: Mapped[int]
    randomness_ops_count: Mapped[int]
    has_bad_randomness_pattern: Mapped[int]
    dangerous_ops_count: Mapped[int]
    dangerous_ops_density: Mapped[float]
    opcode_entropy: Mapped[float]
    reentrancy_risk_score: Mapped[float]
    frontrunning_risk_score: Mapped[float]
    dos_risk_score: Mapped[float]
    arithmetic_risk_score: Mapped[float]
    overall_security_risk_score: Mapped[float]
    has_reentrancy_indicators: Mapped[int]
    has_unchecked_external_calls: Mapped[int]
    has_arithmetic_vulnerabilities: Mapped[int]
    has_access_control_issues: Mapped[int]
    has_dos_vulnerabilities: Mapped[int]

    contract_rel: Mapped["Contract"] = relationship(
        back_populates="metadata_rel")
