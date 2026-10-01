"""Assemble the full placement plan."""
from wild_plan_lib import Plan
import plan_e0_e1, plan_m1_p0, plan_water


def build() -> Plan:
    p = Plan()
    plan_e0_e1.build(p)
    plan_m1_p0.build(p)
    plan_water.build(p)
    return p
